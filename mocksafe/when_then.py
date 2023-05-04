from __future__ import annotations
from typing import Generic, TypeVar
from collections.abc import Callable
from mocksafe.custom_types import CallMatcher
from mocksafe.mock import MethodMock
from mocksafe.call_matchers import AnyCallMatcher


T = TypeVar("T")
ANY_CALL: CallMatcher = AnyCallMatcher()


def when(mock_method: Callable[..., T]) -> WhenStubber[T]:
    if not isinstance(mock_method, MethodMock):
        raise ValueError("Not a SafeMocked method: mock_method")
    return WhenStubber(mock_method)


class WhenStubber(Generic[T]):
    def __init__(self, method_mock: MethodMock[T]):
        self._method_mock = method_mock

    def any_call(self) -> MatchCallStubber[T]:
        return MatchCallStubber(self._method_mock, matcher=ANY_CALL)

    def called_with(self, _: T) -> LastCallStubber[T]:
        return LastCallStubber(self._method_mock)


class MatchCallStubber(Generic[T]):
    def __init__(self, method_mock: MethodMock[T], matcher: CallMatcher):
        self._method_mock = method_mock
        self._matcher = matcher

    def then_return(self, result: T, *consecutive_results: T) -> None:
        results: list[T] = [result, *consecutive_results]
        self._method_mock.add_stub(self._matcher, results)


class LastCallStubber(Generic[T]):
    def __init__(self, method_mock: MethodMock[T]):
        self._method_mock = method_mock

    def then_return(self, result: T, *consecutive_results: T) -> None:
        results: list[T] = [result, *consecutive_results]
        self._method_mock.stub_last_call(results)
