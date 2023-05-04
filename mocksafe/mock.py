from __future__ import annotations
from itertools import count
from typing import Generic, TypeVar, cast
from collections.abc import Callable
from mocksafe.custom_types import MethodName, CallMatcher, Call
from mocksafe.spy import MethodSpy
from mocksafe.stub import MethodStub, ErrorResult, ResultsProvider
from mocksafe.call_matchers import ExactCallMatcher


T = TypeVar("T")

MOCK_NUMBER = count()


def mock(class_type: type[T]) -> T:
    # Is there a more type safe / proper way to do this?
    return cast(T, SafeMock(class_type))


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

        original_method: Callable = self._class_type.__dict__[method_name]
        return_type: type = original_method.__annotations__["return"]
        method_mock = MethodMock(method_name, return_type)
        self._mocks[method_name] = method_mock
        return method_mock


class MethodMock(Generic[T]):
    def __init__(self, name: MethodName, result_type: type[T]):
        self._stub = MethodStub(name, result_type)
        self._spy = MethodSpy(name, self._stub)

    def __call__(self, *args, **kwargs) -> T:
        return self._spy(*args, **kwargs)

    def __repr__(self) -> str:
        return f"MethodMock[{self._stub}]"

    @property
    def name(self) -> MethodName:
        return self._stub.name

    def add_stub(self, matcher: CallMatcher, results: list[T]) -> None:
        self._stub.add(matcher, results)

    def raise_error(self, matcher: CallMatcher, error: BaseException) -> None:
        self._stub.add_effect(matcher, ErrorResult(error))

    def custom_result(self, matcher: CallMatcher, custom: ResultsProvider) -> None:
        self._stub.add_effect(matcher, custom)

    def stub_last_call(self, results: list[T]) -> None:
        recorded_call = self._spy.pop_call()
        matcher = call_equal_to(recorded_call)
        self._stub.add(matcher, results)

    @property
    def calls(self) -> list[Call]:
        return self._spy._calls

    def nth_call(self, n: int) -> Call:
        return self._spy.nth_call(n)
