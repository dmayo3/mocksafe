from __future__ import annotations
import inspect
from itertools import count
from typing import Generic, TypeVar, cast
from collections.abc import Callable
from mocksafe.custom_types import MethodName, CallMatcher, Call
from mocksafe.spy import MethodSpy
from mocksafe.stub import MethodStub, ResultsProvider
from mocksafe.call_matchers import ExactCallMatcher


T = TypeVar("T")

MOCK_NUMBER = count()


def mock(class_type: type[T], name: str | None = None) -> T:
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


def mock_reset(mock_object) -> None:
    if not isinstance(mock_object, SafeMock):
        raise ValueError(f"Not a SafeMocked object: {mock_object}")
    mock_object.reset()


def call_equal_to(exact: Call) -> CallMatcher:
    return ExactCallMatcher(exact)


class SafeMock(Generic[T]):
    def __init__(self, class_type: type[T], name: str | None = None):
        self._class_type = class_type
        self._mocks: dict[MethodName, MethodMock] = {}
        self._name = name or next(MOCK_NUMBER)

    @property
    def mocked_methods(self) -> dict[MethodName, MethodMock]:
        return self._mocks.copy()

    # This is a bit of a hack to fool isinstance checks.
    # Is there a better way?
    @property  # type: ignore
    def __class__(self):
        return self._class_type

    def __repr__(self) -> str:
        return f"SafeMock[{self._class_type.__name__}#{self._name}]"

    def __getattr__(self, method_name: MethodName) -> MethodMock:
        if method_mock := self._mocks.get(method_name):
            return method_mock

        original_method: Callable = getattr(self._class_type, method_name)
        signature = inspect.signature(original_method)
        method_mock = MethodMock(self._class_type, method_name, signature)
        self._mocks[method_name] = method_mock
        return method_mock


class MethodMock(Generic[T]):
    def __init__(
        self, class_type: type[T], name: MethodName, signature: inspect.Signature
    ):
        self._class_type = class_type
        self._stub: MethodStub = MethodStub(name, signature.return_annotation)
        self._spy: MethodSpy = MethodSpy(name, self._stub, signature)

    def __call__(self, *args, **kwargs) -> T:
        return self._spy(*args, **kwargs)

    def __repr__(self) -> str:
        return f"MethodMock[{self._stub}]"

    @property
    def full_name(self) -> str:
        return f"{self._class_type.__name__}.{self.name}"

    @property
    def name(self) -> MethodName:
        return self._stub.name

    def add_stub(self, matcher: CallMatcher, effects: list[T | BaseException]) -> None:
        self._stub.add(matcher, effects)

    def stub_last_call(self, effects: list[T | BaseException]) -> None:
        matcher = call_equal_to(self._spy.pop_call())
        self._stub.add(matcher, effects)

    def custom_result_for_last_call(self, custom: ResultsProvider) -> None:
        matcher = call_equal_to(self._spy.pop_call())
        self.custom_result(matcher, custom)

    def custom_result(self, matcher: CallMatcher, custom: ResultsProvider) -> None:
        self._stub.add_effect(matcher, custom)

    @property
    def calls(self) -> list[Call]:
        return self._spy._calls

    def nth_call(self, n: int) -> Call:
        return self._spy.nth_call(n)
