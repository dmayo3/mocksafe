from typing import Generic, TypeVar
from mocksafe.custom_types import MethodName, CallMatcher


T = TypeVar("T")


class MethodStub(Generic[T]):
    def __init__(self, name: MethodName, result_type: type[T]):
        self._name = name
        self._stubs: list[tuple[CallMatcher, list[T]]] = []
        self._result_type = result_type

    def __call__(self, *args, **kwargs) -> T:
        call = (tuple(args), kwargs)
        for matcher, results in self._stubs:
            if matcher(call):
                if len(results) == 1:
                    return results[0]
                return results.pop(0)

        default_value = self._result_type()
        return default_value

    def __repr__(self) -> str:
        reps = []
        for matcher, result in self._stubs:
            reps.append(f"{matcher} -> {result}")
        return ";".join(reps)

    @property
    def name(self) -> MethodName:
        return self._name

    def add(self, matcher: CallMatcher, results: list[T]) -> None:
        self._stubs.append((matcher, results))
