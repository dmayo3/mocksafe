from __future__ import annotations
from collections.abc import Callable
from mocksafe.custom_types import Call
from mocksafe.mock import MethodMock


Args = tuple


def that(mock_method: Callable) -> MockCalls:
    if not isinstance(mock_method, MethodMock):
        raise ValueError("Not a SafeMocked method: mock_method")
    return MockCalls(mock_method)


class MockCalls:
    def __init__(self, method_mock: MethodMock):
        self._method_mock = method_mock

    @property
    def was_called(self) -> bool:
        return self.num_calls > 0

    @property
    def was_not_called(self) -> bool:
        return not self.was_called

    @property
    def num_calls(self) -> int:
        return len(self._method_mock.calls)

    @property
    def last_call(self) -> Args | Call:
        return self.nth_call(-1)

    def nth_call(self, n: int) -> Args | Call:
        call = self._method_mock.nth_call(n)

        args, kwargs = call

        if kwargs:
            return call
        return args
