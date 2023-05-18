from __future__ import annotations
from collections.abc import Callable
from mocksafe.custom_types import Call


class AnyCallMatcher:
    def __call__(self: AnyCallMatcher, _: Call) -> bool:
        return True

    def __repr__(self: AnyCallMatcher) -> str:
        return "*"


class ExactCallMatcher:
    def __init__(self: ExactCallMatcher, exact: Call):
        self._exact = exact

    def __call__(self: ExactCallMatcher, actual: Call) -> bool:
        return actual == self._exact

    def __repr__(self: ExactCallMatcher) -> str:
        args, kwargs = self._exact
        fmt_args = ", ".join(args)
        fmt_kwargs = ", ".join(f"{k}={v}" for k, v in kwargs.items())
        call_sig = f"{fmt_args}, {fmt_kwargs}" if kwargs else fmt_args
        return f"call({call_sig})"


class CustomCallMatcher:
    def __init__(self: CustomCallMatcher, call_lambda: Callable[..., bool]):
        self._call_lambda = call_lambda

    def __call__(self: CustomCallMatcher, actual: Call) -> bool:
        args, kwargs = actual
        return self._call_lambda(*args, **kwargs)

    def __repr__(self: CustomCallMatcher) -> str:
        return str(self._call_lambda)
