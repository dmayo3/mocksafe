from inspect import Parameter
from types import GenericAlias, UnionType, MappingProxyType
from typing import cast
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
        if param.annotation != Parameter.empty and not _type_match(
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


def _type_match(arg, expected_type: type) -> bool:
    try:
        # Handle generic type by checking just the base type
        # E.g. for dict[str, str] just check isinstance(arg, type(dict))
        origin_type = cast(GenericAlias, expected_type).__origin__
        return isinstance(arg, origin_type)
    except AttributeError:
        pass

    try:
        # Handle union type: recursively match any type in the union
        union: tuple = cast(UnionType, expected_type).__args__
        return any(_type_match(arg, t) for t in union)
    except AttributeError:
        pass

    return isinstance(arg, expected_type)
