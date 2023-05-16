from inspect import Parameter
from types import GenericAlias, MappingProxyType
from typing import Union, cast
from mocksafe.custom_types import MethodName


class CallTypeValidator:
    def __init__(
        self,
        method_name: MethodName,
        params: MappingProxyType[str, Parameter],
        args,
        kwargs,
    ):
        self._method_name = method_name
        self._params = params
        self._args = list(args)
        self._kwargs = kwargs.copy()

    def validate(self):
        expected_names = list(self._params.keys())

        if expected_names and expected_names[0] == "self":
            # Exclude 'self' parameter
            expected_names = expected_names[1:]

        for name in expected_names:
            param = self._params[name]

            if param.kind == Parameter.VAR_POSITIONAL:  # *args
                # Consume any remaining args to be matched
                self._args = []
            elif param.kind == Parameter.VAR_KEYWORD:  # **kwargs
                # Consume any remaining kwargs to be matched
                self._kwargs = {}
            elif self._param_match_arg(param):
                arg = self._args.pop(0)
                self._validate_type(param, arg)
            elif self._param_match_kwarg(name, param):
                arg = self._kwargs.pop(name, param.default)
                self._validate_type(param, arg)
            else:
                raise TypeError(
                    f"Call to mocked method {self._method_name}() missing a required argument: {param}."
                )

        self._check_extra_positional_args()
        self._check_extra_keyword_args()

    def _param_match_arg(self, param: Parameter) -> bool:
        if param.kind not in [
            Parameter.POSITIONAL_ONLY,
            Parameter.POSITIONAL_OR_KEYWORD,
        ]:
            return False

        if self._args:
            return True

        return False

    def _param_match_kwarg(self, name: str, param: Parameter) -> bool:
        if param.kind not in [Parameter.KEYWORD_ONLY, Parameter.POSITIONAL_OR_KEYWORD]:
            return False

        return name in self._kwargs or param.default != Parameter.empty

    def _validate_type(self, param, arg):
        if param.annotation != Parameter.empty and not type_match(
            arg, param.annotation
        ):
            raise TypeError(
                f"Invalid type passed to mocked method {self._method_name}() for parameter: '{param}'. Actual argument passed was: {arg} ({type(arg)})."
            )

    def _check_extra_positional_args(self):
        if self._args:
            raise TypeError(
                f"Mocked method {self._method_name}() was passed too many positional argument(s): {self._args}."
            )

    def _check_extra_keyword_args(self):
        if self._kwargs:
            raise TypeError(
                f"Mocked method {self._method_name}() was passed unexpected keyword argument(s): {self._kwargs}."
            )


def type_match(arg, expected_type: type) -> bool:
    if _is_union(expected_type):
        generic_type: GenericAlias = cast(GenericAlias, expected_type)

        union: tuple = generic_type.__args__

        # Recursively match any type in the union
        return any(type_match(arg, t) for t in union)

    try:
        # Handle other generic types by checking just the base type
        # E.g. for dict[str, str] just check isinstance(arg, type(dict))
        generic_type = cast(GenericAlias, expected_type)
        return isinstance(arg, generic_type.__origin__)
    except AttributeError:
        pass

    return isinstance(arg, expected_type)


def _is_union(t: type) -> bool:
    # 1. Check for types.UnionType

    # This type is not supported in Python 3.9
    # So we check for it at runtime in this hacky way
    if t.__class__.__name__ == "UnionType":
        return True

    # 2. Check for typing.Union / typing.Optional
    # Both are equivalent under the covers
    try:
        generic_type: GenericAlias = cast(GenericAlias, t)

        # typing.Union cannot be used with isinstance()
        return generic_type.__origin__ == Union
    except AttributeError:
        pass

    return False
