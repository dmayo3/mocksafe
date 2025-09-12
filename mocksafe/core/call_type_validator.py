from __future__ import annotations
import builtins
import contextlib
from inspect import Parameter, Signature
from collections.abc import Callable, Sequence, Mapping
from numbers import Number
from urllib.parse import urlencode
from types import GenericAlias
from typing import Union, Any, cast
from mocksafe.core.custom_types import MethodName


class CallTypeValidator:
    def __init__(
        self: CallTypeValidator,
        method_name: MethodName,
        params: Mapping[str, Parameter],
        args: Sequence,
        kwargs: dict,
    ):
        self._method_name = method_name
        self._signature = self._create_validation_signature(params)
        self._args = self._prepare_args(params, args)
        self._kwargs = kwargs

    def validate(self: CallTypeValidator) -> None:
        """Validate that arguments match the signature and have correct types."""
        try:
            # Use Python's built-in argument binding
            bound = self._signature.bind(*self._args, **self._kwargs)
            bound.apply_defaults()

            # Validate types for all bound arguments
            for param_name, value in bound.arguments.items():
                param = self._signature.parameters[param_name]
                self._validate_type(param, value)

        except TypeError as e:
            # Re-raise with our method name for better error messages
            error_msg = str(e).replace("missing", f"{self._method_name}() missing")
            error_msg = error_msg.replace("got", f"{self._method_name}() got")
            error_msg = error_msg.replace("takes", f"{self._method_name}() takes")
            raise TypeError(error_msg) from None

    def _create_validation_signature(
        self: CallTypeValidator, params: Mapping[str, Parameter]
    ) -> Signature:
        """Create a signature for validation, excluding self/cls if present."""
        param_list = list(params.items())

        # Skip self/cls parameter if it exists
        if param_list and param_list[0][0] in {"self", "cls"}:
            param_list = param_list[1:]

        return Signature([param for _, param in param_list])

    def _prepare_args(
        self: CallTypeValidator,
        params: Mapping[str, Parameter],
        args: Sequence,
    ) -> tuple:
        """Prepare arguments, handling the special case of injected cls."""
        param_names = list(params.keys())

        # For class methods, skip the injected cls argument
        if param_names and param_names[0] == "cls" and args:
            return tuple(args[1:])

        return tuple(args)

    def _validate_type(self: CallTypeValidator, param: Parameter, value: Any) -> None:
        """Validate a single parameter's type."""
        # Handle *args and **kwargs by validating each item
        if param.kind == Parameter.VAR_POSITIONAL:
            items = value if isinstance(value, tuple) else (value,)
            for item in items:
                self._validate_single_type(param, item)
        elif param.kind == Parameter.VAR_KEYWORD:
            items_dict = value if isinstance(value, dict) else {param.name: value}
            for item in items_dict.values():
                self._validate_single_type(param, item)
        else:
            self._validate_single_type(param, value)

    def _validate_single_type(self: CallTypeValidator, param: Parameter, arg: Any) -> None:
        """Validate that a single argument matches the parameter's type annotation."""
        if param.annotation != Parameter.empty and not type_match(arg, param.annotation):
            raise TypeError(
                f"Invalid type passed to mocked method {self._method_name}() for "
                f"parameter: '{param}'. Actual argument passed was: "
                f"{arg} ({type(arg)})."
            )


def type_match(arg: Any, annotation: Any) -> bool:
    expected_type: Any = _resolve_type(annotation)

    if _is_union(expected_type):
        generic_type: GenericAlias = cast(GenericAlias, expected_type)

        union: tuple = generic_type.__args__

        # Recursively match any type in the union
        return any(type_match(arg, t) for t in union)

    try:
        # Handle other generic types by checking just the base type
        # E.g. for dict[str, str] just check isinstance(arg, type(dict))
        generic_type = cast(GenericAlias, expected_type)
        return _coercable_type_match(arg, generic_type.__origin__)
    except AttributeError:
        pass

    try:
        return _coercable_type_match(arg, expected_type)
    except TypeError as err:
        if "@runtime_checkable" in str(err):
            raise TypeError(
                f"Could not validate that argument '{arg}' ({type(arg)}) is compatible"
                f" with the expected Protocol type: {expected_type}. The Protocol type"
                " must be annotated with @runtime_checkable."
            ) from err

        gh_issue_params = {
            "title": "Type Match Error",
            "labels": "bug",
            "body": f"Arg: '{arg}' ({type(arg)}); Expected: {expected_type}",
        }
        gh_raise_issue_url = _gh_raise_issue_url(gh_issue_params)

        raise NotImplementedError(
            f"Could not validate that argument '{arg}' ({type(arg)}) is compatible "
            f"with expected type: {expected_type}.\n"
            f"Please raise an issue for this: {gh_raise_issue_url}\n"
            "In the meantime please work around the problem."
        ) from err


def _resolve_type(annotation: Any) -> Any:
    if not isinstance(annotation, str):
        return annotation

    # It's a string literal type that we need to resolve
    # E.g. def g(x: "int") needs to resolve to int
    with contextlib.suppress(AttributeError):
        return getattr(builtins, annotation)

    gh_issue_params = {
        "title": "Failed to resolve literal annotation",
        "labels": "bug",
        "body": f"Annotation: '{annotation}'",
    }
    gh_raise_issue_url = _gh_raise_issue_url(gh_issue_params)
    raise NotImplementedError(
        f"Failed to resolve literal type annotation '{annotation}'.\n"
        f"Please raise an issue for this: {gh_raise_issue_url}\n"
        "In the meantime please work around the problem."
    )


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


def _gh_raise_issue_url(gh_issue_params: dict[str, str]) -> str:
    gh_repo = "https://github.com/dmayo3/mocksafe"
    return f"{gh_repo}/issues/new?{urlencode(gh_issue_params)}"


def _coercable_type_match(arg: Any, annotation: Any) -> bool:
    """
    Check if arg is an instance of annotation or can be coerced to it
    without loss of precision.

    Examples:
        >>> _coercable_type_match(1, int)
        True
        >>> _coercable_type_match(1.0, int)
        True
        >>> _coercable_type_match(1, float)
        True
        >>> _coercable_type_match(1, bool)
        False
        >>> _coercable_type_match(1, str)
        False
        >>> _coercable_type_match("", bool)
        False
    """
    # Exact match
    if isinstance(arg, annotation):
        return True

    # Special case: don't coerce to bool
    # Needed because issubclass(bool, Number) is True!
    if annotation == bool:
        return False

    # Only coerce numbers that can be converted without loss of precision
    if not isinstance(arg, Number):
        return False
    if not issubclass(annotation, Number) or not callable(annotation):
        return False
    # Numeric types should also be callable, e.g. int(1.0) -> 1
    constructor = cast(Callable[[Number], Number], annotation)
    return constructor(arg) == arg
