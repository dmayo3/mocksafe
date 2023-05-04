from typing import Generic, TypeVar
from collections.abc import Callable
from mocksafe.custom_types import MethodName, Call


T = TypeVar("T")


class MethodSpy(Generic[T]):
    def __init__(self, name: MethodName, delegate: Callable[..., T]):
        self._name = name
        self._delegate = delegate
        self._calls: list[Call] = []

    def __call__(self, *args, **kwargs) -> T:
        self._calls.append((tuple(args), kwargs.copy()))
        return self._delegate(*args, **kwargs)

    def __repr__(self) -> str:
        return f"MethodSpy[{self._name}:{len(self.calls)} call(s)]"

    @property
    def name(self) -> MethodName:
        return self._name

    @property
    def calls(self) -> list[Call]:
        return self._calls

    def pop_call(self) -> Call:
        return self._calls.pop()

    def nth_call(self, n: int) -> Call:
        return self._calls[n]
