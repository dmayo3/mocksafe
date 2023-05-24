from __future__ import annotations
import inspect
from itertools import count
from types import ModuleType
from typing import Generic, TypeVar, Optional, Union, Any, cast
from mocksafe.custom_types import MethodName, CallMatcher, Call
from mocksafe.spy import MethodSpy
from mocksafe.stub import MethodStub, ResultsProvider
from mocksafe.call_matchers import ExactCallMatcher


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
        SafeMock[Random#...]

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
        >>> mock_random
        SafeMock[random#...]

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
        self._original: Union[type[T], M] = module or spec
        self._original_class: type = module.__class__ if module else spec
        self._mocks: dict[MethodName, MethodMock] = {}

        self._spec = spec
        self._name = f"{self._original.__name__}#{identity}"

    @property
    def mocked_methods(self: SafeMock) -> dict[MethodName, MethodMock]:
        return self._mocks.copy()

    def reset(self: SafeMock) -> None:
        for mocked_method in self._mocks.values():
            mocked_method.reset()

    # This is a bit of a hack to fool isinstance checks.
    # Is there a better way?
    @property  # type: ignore
    def __class__(self: SafeMock):
        return self._original_class

    def __repr__(self: SafeMock) -> str:
        return f"SafeMock[{self._name}]"

    def __getattr__(self: SafeMock, attr_name: str) -> MethodMock:
        if attr_name in getattr(self._spec, "__attrs__", []):
            # Field attribute defined on the original class
            raise AttributeError(f"{self}.{attr_name} attribute value not set.")

        original_attr = self.get_original_attr(attr_name)

        if isinstance(original_attr, property):
            raise ValueError(
                (
                    "MockSafe doesn't currently support properties, "
                    f"so {self}.{attr_name} could not be mocked."
                ),
            )

        if attr_name not in self._mocks:
            signature = inspect.signature(original_attr)
            self._mocks[attr_name] = MethodMock(
                self._spec, str(self), attr_name, signature
            )

        return self._mocks[attr_name]

    def get_original_attr(self: SafeMock, attr_name: str) -> Any:
        try:
            return getattr(self._spec, attr_name)
        except AttributeError:
            raise AttributeError(
                (
                    f"{self}.{attr_name} attribute doesn't exist on the "
                    f"original mocked type/module {self._original}."
                ),
            ) from None


class MethodMock(Generic[T]):
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
