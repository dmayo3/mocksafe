from __future__ import annotations
from inspect import Signature
from typing import Generic, Optional, TypeVar, Protocol, runtime_checkable
from mocksafe.core.custom_types import MethodName, Call
from mocksafe.core.call_type_validator import CallTypeValidator


T = TypeVar("T", covariant=True)


class Delegate(Protocol[T]):
    def __call__(self, *args, **kwargs) -> Optional[T]:
        ...


@runtime_checkable
class CallRecorder(Protocol):
    """
    Generic Protocol for getting information about
    mocked / spied calls.
    """

    @property
    def name(self) -> MethodName:
        ...

    @property
    def calls(self) -> list[Call]:
        ...

    def nth_call(self, n: int) -> Call:
        ...


class MethodSpy(CallRecorder, Generic[T]):
    def __init__(
        self: MethodSpy,
        name: MethodName,
        delegate: Delegate,
        signature: Signature,
    ):
        self._name = name
        self._delegate = delegate
        self._calls: list[Call] = []
        self._signature = signature

    def __call__(self: MethodSpy, *args, **kwargs) -> Optional[T]:
        validator = CallTypeValidator(
            self._name,
            self._signature.parameters,
            args,
            kwargs,
        )
        validator.validate()

        self._calls.append((tuple(args), kwargs.copy()))

        return self._delegate(*args, **kwargs)

    def __repr__(self: MethodSpy) -> str:
        return f"MethodSpy[{self._name}:{len(self.calls)} call(s)]"

    @property
    def name(self: MethodSpy) -> MethodName:
        return self._name

    @property
    def calls(self: MethodSpy) -> list[Call]:
        return self._calls

    def pop_call(self: MethodSpy) -> Call:
        return self._calls.pop()

    # pylint: disable=raise-missing-from
    def nth_call(self: MethodSpy, n: int) -> Call:
        try:
            return self._calls[n]
        except IndexError:
            if not self._calls:
                raise ValueError(f"The mocked method {self._name}() was not called.")

            raise ValueError(
                (
                    f"Mocked method {self._name}() was not called {n + 1} time(s). "
                    f"The actual number of calls was {len(self.calls)}."
                ),
            )
