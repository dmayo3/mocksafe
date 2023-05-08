import types
from inspect import Signature, Parameter
from typing import Generic, TypeVar, cast
from collections.abc import Callable
from mocksafe.custom_types import MethodName, Call


T = TypeVar("T")


class MethodSpy(Generic[T]):
    def __init__(
        self, name: MethodName, delegate: Callable[..., T], signature: Signature
    ):
        self._name = name
        self._delegate = delegate
        self._calls: list[Call] = []
        self._signature = signature

    def __call__(self, *args, **kwargs) -> T:
        self._validate_type_correctness(args, kwargs)
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

    # pylint: disable=raise-missing-from
    def nth_call(self, n: int) -> Call:
        try:
            return self._calls[n]
        except IndexError:
            if not self._calls:
                raise ValueError(f"The mocked method {self._name}() was not called.")

            raise ValueError(
                f"Mocked method {self._name}() was not called {n+1} time(s). "
                f"The actual number of calls was {len(self.calls)}."
            )

    def _validate_type_correctness(self, args, kwargs):
        expected_params = self._signature.parameters
        expected_names = list(expected_params.keys())

        if expected_names and expected_names[0] != "self":
            raise TypeError(
                "Mocked method {self._name}() is missing `self` as the first parameter"
            )

        expected_names = expected_names[1:]  # Exclude 'self' parameter

        args = list(args)
        kwargs = kwargs.copy()

        for name in expected_names:
            param = expected_params[name]

            if args:
                arg = args.pop(0)
            elif name in kwargs:
                arg = kwargs.pop(name)
            elif param.default != Parameter.empty:
                arg = param.default
            else:
                raise TypeError(
                    f"Call to mocked method {self._name}() missing a required positional argument: {param}."
                )

            if param.annotation == Parameter.empty:
                continue

            if not _type_match(arg, param.annotation):
                raise TypeError(
                    f"Invalid type passed to mocked method {self._name}() for parameter: '{param}'. Actual argument passed was: {arg} ({type(arg)})."
                )

        if args:
            raise TypeError(
                f"Mocked method {self._name}() was passed too many positional argument(s): {args}."
            )
        if kwargs:
            raise TypeError(
                f"Mocked method {self._name}() was passed unexpected keyword argument(s): {kwargs}."
            )


def _type_match(arg, expected_type: type) -> bool:
    try:
        # Handle generic type by checking just the base type
        # E.g. for dict[str, str] just check isinstance(arg, type(dict))
        origin_type = cast(types.GenericAlias, expected_type).__origin__
        return isinstance(arg, origin_type)
    except AttributeError:
        pass

    try:
        # Handle union type: recursively match any type in the union
        union: tuple = cast(types.UnionType, expected_type).__args__
        return any(_type_match(arg, t) for t in union)
    except AttributeError:
        pass

    return isinstance(arg, expected_type)
