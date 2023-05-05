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

    def add(self, matcher: CallMatcher, effects: list[T | BaseException]) -> None:
        self.add_effect(matcher, CannedEffects(effects))

    def add_effect(self, matcher: CallMatcher, effect: ResultsProvider) -> None:
        self._stubs.append((matcher, effect))


class CannedEffects(Generic[T]):
    def __init__(self, effects: list[T]):
        self._effects = effects

    def __call__(self, *args, **kwargs) -> T:
        if len(self._effects) == 1:
            effect = self._effects[0]
        else:
            effect = self._effects.pop(0)

        if isinstance(effect, BaseException):
            raise effect
        return effect

    def __repr__(self) -> str:
        return str(self._effects[0])
