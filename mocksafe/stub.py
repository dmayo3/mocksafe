from typing import Generic, TypeVar
from collections.abc import Callable
from mocksafe.custom_types import MethodName, CallMatcher


T = TypeVar("T")
ResultsProvider = Callable[..., T]


class MethodStub(Generic[T]):
    def __init__(self, name: MethodName, result_type: type[T]):
        self._name = name
        self._stubs: list[tuple[CallMatcher, ResultsProvider]] = []
        self._result_type = result_type

    def __call__(self, *args, **kwargs) -> T:
        call = (tuple(args), kwargs)
        for matcher, results in self._stubs:
            if matcher(call):
                return results(*args, **kwargs)

        default_value = self._result_type()
        return default_value

    def __repr__(self) -> str:
        reps = []
        for matcher, results in self._stubs:
            reps.append(f"{matcher} -> {results}")
        return ";".join(reps)

    @property
    def name(self) -> MethodName:
        return self._name

    def add(self, matcher: CallMatcher, results: list[T]) -> None:
        self.add_effect(matcher, CannedResults(results))

    def add_effect(self, matcher: CallMatcher, effect: ResultsProvider) -> None:
        self._stubs.append((matcher, effect))


class CannedResults(Generic[T]):
    def __init__(self, results: list[T]):
        self._results = results

    def __call__(self, *args, **kwargs) -> T:
        if len(self._results) == 1:
            return self._results[0]
        return self._results.pop(0)

    def __repr__(self) -> str:
        return str(self._results[0])


class ErrorResult(Generic[T]):
    def __init__(self, error: BaseException):
        self._error = error

    def __call__(self, *args, **kwargs) -> T:
        raise self._error

    def __repr__(self) -> str:
        return str(self._error)
