from __future__ import annotations
from inspect import Signature, isclass
from typing import Generic, TypeVar, Optional, Union
from collections.abc import Callable
from mocksafe.custom_types import MethodName, CallMatcher
from mocksafe.call_type_validator import type_match


T = TypeVar("T")
ResultsProvider = Callable[..., T]


# Stub default values for these simple built-in types
PRIMITIVES = [str, int, bool, float, dict, list, tuple, set]


class MethodStub(Generic[T]):
    def __init__(self: MethodStub, name: MethodName, result_type: type):
        self._name = name
        self._stubs: list[tuple[CallMatcher, ResultsProvider]] = []
        self._result_type = result_type

    def __call__(self: MethodStub, *args, **kwargs) -> Optional[T]:
        call = (tuple(args), kwargs)
        for matcher, results in self._stubs:
            if matcher(call):
                return results(*args, **kwargs)

        # No default return value has been stubbed, try to determine
        # something sensible to return

        default_value: Optional[T]
        result_type: type = self._result_type

        primitive_result_type = isclass(result_type) and any(
            issubclass(result_type, p) for p in PRIMITIVES
        )

        if primitive_result_type:
            default_value = result_type()
        else:
            default_value = None

        return default_value

    def __repr__(self: MethodStub) -> str:
        reps = []
        for matcher, results in self._stubs:
            reps.append(f"{matcher} -> {results}")
        return "; ".join(reps)

    @property
    def name(self: MethodStub) -> MethodName:
        return self._name

    def add(
        self: MethodStub, matcher: CallMatcher, effects: list[Union[T, BaseException]]
    ) -> None:
        self._validate_effects(effects)
        self.add_effect(matcher, CannedEffects(effects))

    def add_effect(
        self: MethodStub, matcher: CallMatcher, effect: ResultsProvider
    ) -> None:
        self._stubs.insert(0, (matcher, effect))

    def _validate_effects(
        self: MethodStub, effects: list[Union[T, BaseException]]
    ) -> None:
        # Runtime check in case static type checking allows an incompatible type
        # to slip through
        if self._result_type == Signature.empty:
            return  # Nothing we can check

        for e in effects:
            if isinstance(e, BaseException):
                continue
            if not type_match(e, self._result_type):
                raise TypeError(
                    (
                        f"Cannot use stub result {e} ({type(e)}) with the mocked method"
                        f" {self._name}(), the expected return type is:"
                        f" {self._result_type}."
                    ),
                )


class CannedEffects(Generic[T]):
    def __init__(self: CannedEffects, effects: list[T]):
        self._effects = effects

    def __call__(self: CannedEffects, *args, **kwargs) -> T:
        if len(self._effects) == 1:
            effect = self._effects[0]
        else:
            effect = self._effects.pop(0)

        if isinstance(effect, BaseException):
            raise effect
        return effect

    def __repr__(self: CannedEffects) -> str:
        return str(self._effects[0])
