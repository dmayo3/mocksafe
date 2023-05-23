from __future__ import annotations
import inspect
from itertools import count
from typing import Generic, TypeVar, Optional, Union, Any, cast
from mocksafe.custom_types import MethodName, CallMatcher, Call
from mocksafe.spy import MethodSpy
from mocksafe.stub import MethodStub, ResultsProvider
from mocksafe.call_matchers import ExactCallMatcher


T = TypeVar("T")

MOCK_NUMBER = count()


def mock(class_type: type[T], name: Optional[str] = None) -> T:
    """
    Creates a mock of the given ``class_type``.

    :param class_type: the class to be mocked of generic type ``T``
    :type class_type: type[T]

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
    return cast(T, SafeMock(class_type, name))


def mock_reset(mock_object: Any) -> None:
    if not isinstance(mock_object, SafeMock):
        raise ValueError(f"Not a SafeMocked object: {mock_object}")
    mock_object.reset()


def call_equal_to(exact: Call) -> CallMatcher:
    return ExactCallMatcher(exact)


class SafeMock(Generic[T]):
    def __init__(self: SafeMock, class_type: type[T], name: Optional[str] = None):
        self._class_type = class_type
        self._mocks: dict[MethodName, MethodMock] = {}
        self._name = name or next(MOCK_NUMBER)

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
        return self._class_type

    def __repr__(self: SafeMock) -> str:
        return f"SafeMock[{self._class_type.__name__}#{self._name}]"

    def __getattr__(self: SafeMock, attr_name: str) -> MethodMock:
        if attr_name in getattr(self._class_type, "__attrs__", []):
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
            self._mocks[attr_name] = MethodMock(self._class_type, attr_name, signature)

        return self._mocks[attr_name]

    def get_original_attr(self: SafeMock, attr_name: str) -> Any:
        try:
            return getattr(self._class_type, attr_name)
        except AttributeError as err:
            raise AttributeError(
                (
                    f"{self}.{attr_name} attribute doesn't exist on the "
                    f"original mocked type {self._class_type}."
                ),
            ) from err


class MethodMock(Generic[T]):
    def __init__(
        self: MethodMock,
        class_type: type[T],
        name: MethodName,
        signature: inspect.Signature,
    ):
        self._stub: MethodStub
        self._spy: MethodSpy

        self._class_type = class_type
        self._name = name
        self._signature = signature
        self.reset()

    def reset(self: MethodMock) -> None:
        self._stub = MethodStub(self._name, self._signature.return_annotation)
        self._spy = MethodSpy(self._name, self._stub, self._signature)

    def __call__(self: MethodMock, *args, **kwargs) -> T:
        return self._spy(*args, **kwargs)

    def __repr__(self: MethodMock) -> str:
        return f"MethodMock[{self._stub}]"

    @property
    def full_name(self: MethodMock) -> str:
        return f"{self._class_type.__name__}.{self.name}"

    @property
    def name(self: MethodMock) -> MethodName:
        return self._stub.name

    def add_stub(
        self: MethodMock,
        matcher: CallMatcher,
        effects: list[Union[T, BaseException]],
    ) -> None:
        self._stub.add(matcher, effects)

    def stub_last_call(
        self: MethodMock, effects: list[Union[T, BaseException]]
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
