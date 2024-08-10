from __future__ import annotations
import inspect
from itertools import count
from types import ModuleType
from typing import Generic, TypeVar, Optional, Union, Any, cast, get_type_hints
from mocksafe.core.custom_types import MethodName, PropertyName, CallMatcher, Call
from mocksafe.core.mock_property import MockProperty
from mocksafe.core.spy import MethodSpy, CallRecorder
from mocksafe.core.stub import MethodStub, ResultsProvider
from mocksafe.core.call_matchers import ExactCallMatcher


T = TypeVar("T")
V = TypeVar("V")
M = TypeVar("M", bound=ModuleType)


MOCK_NUMBER = count()


def mock(spec: type[T], name: Optional[str] = None) -> T:
    """
    Creates a mock of the given ``spec``.

    :param spec: the specification (class/protocol/type) to be mocked
                 of generic type ``T``
    :type spec: type[T]

    :param name: optional custom name to help identify the
        mock object in str representations
    :type name: str, optional

    :return: a mock object but typed with the generic type ``T``
    :rtype: T

    :Example:
        >>> from random import Random
        >>> mock_random: Random = mock(Random)
        >>> mock_random
        SafeMock(<class 'random.Random'>)

    To stub a mocked method see:

    :meth:`mocksafe.when`

    To assert calls made to a mocked method see:

    :meth:`mocksafe.that`

    To retrieve calls that were made to a mocked method see:

    :meth:`mocksafe.spy`
    """

    # Is there a more type safe / proper way to do this?
    return cast(T, SafeMock(spec, name))


def mock_module(module: M, name: Optional[str] = None) -> M:
    """
    Creates a mocked version of the given ``module``.

    :param module: module to be mocked of generic ModuleType ``M``
    :type module: M

    :param name: optional custom name to help identify the
                 mock object in str representations
    :type name: str, optional

    :return: a mock object but typed with the generic ModuleType ``M``
    :rtype: M

    :Example:
        >>> import random
        >>> mock_random = mock_module(random)
        >>> mock_random  # doctest: +NORMALIZE_WHITESPACE
        SafeMock(<class 'MockSpec(module=random)'>,
                 <module 'random' from '.../random.py'>)

    To stub a mocked function on the module see:

    :meth:`mocksafe.when`

    To assert calls made to a mocked function see:

    :meth:`mocksafe.that`

    To retrieve calls that were made to a mocked function see:

    :meth:`mocksafe.spy`
    """

    # Dynamically create a class-like type that looks like the module
    module_spec = type(
        f"MockSpec(module={module.__name__})",
        (),
        {
            **module.__dict__,
            # Set this to None otherwise it ends up looking like:
            # <class 'mocksafe.mock.{module.__name__}'>
            "__module__": None,
        },
    )
    return cast(M, SafeMock(module_spec, name, module))


def mock_reset(mock_object: Any) -> None:
    """
    Reset a mock object's configured stubbing and recorded calls.
    """
    if not isinstance(mock_object, SafeMock):
        raise ValueError(f"Not a SafeMocked object: {mock_object}")
    mock_object.reset()


def call_equal_to(exact: Call) -> CallMatcher:
    return ExactCallMatcher(exact)


class SafeMock(Generic[T]):
    _custom_name: str | None
    _original: type[T] | ModuleType
    _original_class: type
    _module: ModuleType | None
    _mocks: dict[MethodName, MethodMock]
    _properties: dict[PropertyName, MockProperty]
    _spec: type[T]
    _name: str

    def __init__(
        self: SafeMock,
        spec: type[T],
        name: Optional[str] = None,
        module: Optional[M] = None,
    ):
        """
        :param spec: the specification (class/protocol/type) to be mocked
                     of generic type ``T``
        :param name: optional identifier for debugging
                     (defaults to an autoincrementing integer)
        :param module: optional original module if applicable, for debugging
        """
        identity = name or next(MOCK_NUMBER)

        # We set on __dict__ to avoid invoking __setattr__
        # and causing infinite recursion
        self.__dict__["_custom_name"] = name
        self.__dict__["_original"] = module or spec
        self.__dict__["_original_class"] = module.__class__ if module else spec
        self.__dict__["_module"] = module
        self.__dict__["_mocks"] = {}
        self.__dict__["_properties"] = {}
        self.__dict__["_spec"] = spec
        self.__dict__["_name"] = f"{self._original.__name__}#{identity}"

    @property
    def mocked_methods(self: SafeMock) -> dict[MethodName, MethodMock]:
        return self._mocks.copy()

    def reset(self: SafeMock) -> None:
        for mocked_method in self._mocks.values():
            mocked_method.reset()

    # This is a bit of a hack to fool isinstance checks.
    # Is there a better way?
    @property  # type: ignore
    def __class__(self: SafeMock):  # type: ignore
        return self._original_class

    def __str__(self: SafeMock) -> str:
        return f"SafeMock[{self._name}]"

    def __repr__(self: SafeMock) -> str:
        constructor_args: list[str] = [repr(self._spec)]
        if self._custom_name:
            constructor_args.append(repr(self._custom_name))
        if self._module:
            constructor_args.append(repr(self._module))

        return f"SafeMock({', '.join(constructor_args)})"

    def __getattr__(self: SafeMock, attr_name: str) -> MethodMock | Any:
        original_attr = self.get_original_attr(attr_name)

        if isinstance(original_attr, property):
            prop = self._properties.get(attr_name)
            if not prop or not prop.fget:
                # TODO: implement support for automatic mocking, like we do for
                # MethodMock below
                raise ValueError(
                    f"Property: {self}.{attr_name} needs to be mocked before use",
                )
            return prop.fget(prop)

        if attr_name not in self._mocks:
            signature = inspect.signature(original_attr)
            self._mocks[attr_name] = MethodMock(
                self._spec, str(self), attr_name, signature
            )

        return self._mocks[attr_name]

    def __setattr__(self: SafeMock, attr_name: str, value: Any) -> None:
        try:
            spec_annotations = get_type_hints(self._spec)
        except (KeyError, AttributeError):
            spec_annotations = {}

        # Check if there's an attribute already set or a property
        try:
            original_attr = self.get_original_attr(attr_name)
        except AttributeError:
            original_attr = None

        attr_defined = original_attr or attr_name in spec_annotations
        attrs_unknown = not original_attr and not spec_annotations

        if isinstance(original_attr, property):
            prop = self._properties.get(attr_name)
            if not prop or not prop.fset:
                raise ValueError(
                    f"Property setter: {self}.{attr_name} needs to be stubbed"
                    " before use"
                )
            prop.fset(prop, value)
        elif attr_defined or attrs_unknown:
            self.__dict__[attr_name] = value
        else:
            raise AttributeError(
                f"Cannot set non-existent attribute: {self}.{attr_name} that does"
                " not seem to exist on the original mocked class"
            )

    def get_original_attr(self: SafeMock, attr_name: str) -> Any:
        try:
            spec_annotations = get_type_hints(self._spec)
        except (KeyError, AttributeError):
            # get_type_hints() can blow up on mocked modules
            # as they are not real classes
            spec_annotations = {}

        if attr_name in spec_annotations:
            # Field attribute annotated on the original class but with
            # no value for it stubbed on the mock object yet

            # TODO: attempt to return a default value for it based on the
            # annotation type
            raise AttributeError(f"{self}.{attr_name} field value not stubbed.")

        if attr_name in getattr(self._spec, "__attrs__", []):
            # Field attribute defined on the original class but with
            # no value for it stubbed on the mock object yet.

            # Note that __attrs__ is not a Python standard, it's a convention
            # used by the requests library.
            raise AttributeError(f"{self}.{attr_name} field value not stubbed.")

        try:
            return getattr(self._spec, attr_name)
        except AttributeError:
            raise AttributeError(
                (
                    f"{self}.{attr_name} attribute doesn't exist on the "
                    f"original mocked type/module {self._original}."
                ),
            ) from None


class MethodMock(CallRecorder, Generic[T]):
    def __init__(
        self: MethodMock,
        spec: type[T],
        parent_name: str,
        name: MethodName,
        signature: inspect.Signature,
    ):
        self._stub: MethodStub
        self._spy: MethodSpy

        self._spec = spec
        self._parent_name = parent_name
        self._name = name
        self._signature = signature
        self.reset()

    def reset(self: MethodMock) -> None:
        self._stub = MethodStub(self._name, self._signature.return_annotation)
        self._spy = MethodSpy(self._name, self._stub, self._signature)

    def __call__(self: MethodMock, *args, **kwargs) -> Any:
        return self._spy(*args, **kwargs)

    def __repr__(self: MethodMock) -> str:
        return f"MethodMock[{self._stub}]"

    @property
    def full_name(self: MethodMock) -> str:
        return f"{self._parent_name}.{self.name}"

    @property
    def name(self: MethodMock) -> MethodName:
        return self._stub.name

    def add_stub(
        self: MethodMock,
        matcher: CallMatcher,
        effects: list[Union[V, BaseException]],
    ) -> None:
        self._stub.add(matcher, effects)

    def stub_last_call(
        self: MethodMock, effects: list[Union[V, BaseException]]
    ) -> None:
        matcher = call_equal_to(self._spy.pop_call())
        self._stub.add(matcher, effects)

    def custom_result_for_last_call(self: MethodMock, custom: ResultsProvider) -> None:
        matcher = call_equal_to(self._spy.pop_call())
        self.custom_result(matcher, custom)

    def custom_result(
        self: MethodMock, matcher: CallMatcher, custom: ResultsProvider
    ) -> None:
        self._stub.add_effect(matcher, custom)

    @property
    def calls(self: MethodMock) -> list[Call]:
        return self._spy._calls

    def nth_call(self: MethodMock, n: int) -> Call:
        return self._spy.nth_call(n)
