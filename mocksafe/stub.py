from inspect import Signature, isclass
from typing import Generic, TypeVar
from collections.abc import Callable
from mocksafe.custom_types import MethodName, CallMatcher


T = TypeVar("T")
ResultsProvider = Callable[..., T]


# Stub default values for these simple built-in types
PRIMITIVES = [str, int, bool, float, dict, list, tuple, set]


class MethodStub(Generic[T]):
    def __init__(self, name: MethodName, result_type: type):
        self._name = name
        self._stubs: list[tuple[CallMatcher, ResultsProvider]] = []
        self._result_type = result_type

    def __call__(self, *args, **kwargs) -> T | None:
        call = (tuple(args), kwargs)
        for matcher, results in self._stubs:
            if matcher(call):
                return results(*args, **kwargs)

        # No default return value has been stubbed, try to determine
        # something sensible to return

        default_value: T | None
        result_type: type = self._result_type

        if result_type == type(None):
            default_value = None  # type: ignore
        elif result_type == Signature.empty:
            # There are no type annotations to infer type from.
            # Fall back to None.
            default_value = None
        elif not isclass(result_type):
            default_value = None
        elif any(issubclass(result_type, p) for p in PRIMITIVES):
            default_value = result_type()

        return default_value

    def __repr__(self) -> str:
        reps = []
        for matcher, results in self._stubs:
            reps.append(f"{matcher} -> {results}")
        return "; ".join(reps)

    @property
    def name(self) -> MethodName:
        return self._name

    def add(self, matcher: CallMatcher, effects: list[T | BaseException]) -> None:
        self._validate_effects(effects)
        self.add_effect(matcher, CannedEffects(effects))

    def add_effect(self, matcher: CallMatcher, effect: ResultsProvider) -> None:
        self._stubs.insert(0, (matcher, effect))

    def _validate_effects(self, effects: list[T | BaseException]):
        # Runtime check in case static type checking allows an incompatible type
        # to slip through
        if self._result_type == Signature.empty:
            return  # Nothing we can check

        for e in effects:
            if isinstance(e, BaseException):
                continue
            if not isinstance(e, self._result_type):
                raise TypeError(
                    f"Cannot use stub result {e} ({type(e)}) with the mocked method {self._name}(), the expected return type is: {self._result_type}."
                )


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
