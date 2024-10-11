import sys
import contextlib
import random
from inspect import Parameter
from types import ModuleType
from typing import (
    Mapping,
    ContextManager,
    Callable,
    Protocol,
    Sequence,
    Union,
    Optional,
    Any,
    Generator,
)
from collections import OrderedDict
from collections.abc import Iterable, Iterator, Sized
from decimal import Decimal
from fractions import Fraction

import pytest

from mocksafe.core.call_type_validator import (
    CallTypeValidator,
    type_match,
    _coercable_type_match,
)


ANY_NAME = "any_name"
ANY_PARAMETER = Parameter(ANY_NAME, Parameter.POSITIONAL_OR_KEYWORD)

NO_PARAMS: Mapping[str, Parameter] = {}
SELF_PARAM: Mapping[str, Parameter] = {"self": ANY_PARAMETER}


async def async_function():
    ...


def test_validate_no_params():
    validator = CallTypeValidator(ANY_NAME, NO_PARAMS, (), {})
    validator.validate()


def test_validate_too_many_args():
    validator = CallTypeValidator(ANY_NAME, NO_PARAMS, ("one too many args",), {})
    with pytest.raises(TypeError):
        validator.validate()


def test_validate_too_many_kwargs():
    validator = CallTypeValidator(ANY_NAME, NO_PARAMS, (), {"too_many": "kwargs"})
    with pytest.raises(TypeError):
        validator.validate()


def test_validator_ignores_self_arg():
    validator = CallTypeValidator(ANY_NAME, SELF_PARAM, (), {})
    validator.validate()


def test_validates_missing_positional_arg():
    positional_param = Parameter(ANY_NAME, Parameter.POSITIONAL_ONLY)
    params = OrderedDict(**SELF_PARAM, **{ANY_NAME: positional_param})

    validator = CallTypeValidator(ANY_NAME, params, (), {})

    with pytest.raises(TypeError):
        validator.validate()

    validator = CallTypeValidator(ANY_NAME, params, (), {"unexpected": "keyword"})

    with pytest.raises(TypeError):
        validator.validate()


def test_validates_missing_kwarg():
    kw_param = Parameter(ANY_NAME, Parameter.KEYWORD_ONLY)
    params = OrderedDict(**SELF_PARAM, **{ANY_NAME: kw_param})

    validator = CallTypeValidator(ANY_NAME, params, (), {})

    with pytest.raises(TypeError):
        validator.validate()

    validator = CallTypeValidator(ANY_NAME, params, ("unexpected-arg",), {})

    with pytest.raises(TypeError):
        validator.validate()


def test_validates_matching_arg():
    params = {ANY_NAME: Parameter(ANY_NAME, Parameter.POSITIONAL_ONLY)}

    validator = CallTypeValidator(ANY_NAME, params, ("this arg matches",), {})

    validator.validate()


def test_validates_matching_kwarg():
    params = {"foo": Parameter("foo", Parameter.KEYWORD_ONLY)}

    validator = CallTypeValidator(ANY_NAME, params, (), {"foo": "bar"})

    validator.validate()


def test_validates_matching_either_arg():
    params = {"foo": Parameter("foo", Parameter.POSITIONAL_OR_KEYWORD)}

    validator = CallTypeValidator(ANY_NAME, params, ("bar",), {})
    validator.validate()

    validator = CallTypeValidator(ANY_NAME, params, (), {"foo": "bar"})
    validator.validate()


def test_validates_mixed_param_kinds():
    params = OrderedDict(**SELF_PARAM)
    params["foo"] = Parameter("foo", Parameter.POSITIONAL_ONLY)
    params["bar"] = Parameter("bar", Parameter.KEYWORD_ONLY)

    validator = CallTypeValidator(ANY_NAME, params, ("baz",), {"bar": "quux"})
    validator.validate()


def test_validates_varargs():
    params = {"args": Parameter("args", Parameter.VAR_POSITIONAL)}

    validator = CallTypeValidator(ANY_NAME, params, ("foo",), {})
    validator.validate()

    validator = CallTypeValidator(ANY_NAME, params, ("foo", "bar", "baz"), {})
    validator.validate()


def test_validates_var_kwargs():
    params = {"kwargs": Parameter("kwargs", Parameter.VAR_KEYWORD)}

    validator = CallTypeValidator(ANY_NAME, params, (), {"foo": "bar"})
    validator.validate()

    validator = CallTypeValidator(ANY_NAME, params, (), {"baz": "quux", "foo": "bar"})
    validator.validate()


@pytest.mark.parametrize(
    "arg_value,param_type",
    [
        # Built-ins, collections, "primitive" types, etc.
        (True, bool),
        (123, int),
        (3.45, float),
        (2j, complex),
        (Decimal("1.23"), Decimal),
        (Fraction(1, 4), Fraction),
        ([1, 2, 3], Iterable),
        ("string", Iterable),
        ((1, 2, 3), Iterable),
        ({"a": "b"}, Iterable),
        ({"a": "b"}, Iterable),
        (iter([1, 2, 3]), Iterator),
        ([1, 2, 3], Sequence),
        ("string", Sequence),
        ((1, 2, 3), Sequence),
        ([1, 2, 3], list),
        (("a", "b"), tuple),
        (range(10), range),
        ("hi", str),
        (b"hello", bytes),
        (bytearray(b"\xf0\xf1\xf2"), bytearray),
        (memoryview(b"abcefg"), memoryview),
        ({1, 2, 3}, set),
        (frozenset({4, 5, 6, 6}), frozenset),
        ({"a": "b"}, dict),
        (contextlib.nullcontext(), ContextManager),
        (lambda: None, Callable),
        (type(int), type),
        (None, object),
        (None, type(None)),
        (..., type(Ellipsis)),
        (NotImplemented, type(NotImplemented)),
        (async_function, Callable),
        # String literal types
        # E.g.  def f(n: "int")
        (True, "bool"),
        (123, "int"),
        (3.45, "float"),
        (2j, "complex"),
        ([1, 2, 3], "list"),
        (("a", "b"), "tuple"),
        (range(10), "range"),
        ("hi", "str"),
        (b"hello", "bytes"),
        (bytearray(b"\xf0\xf1\xf2"), "bytearray"),
        (memoryview(b"abcefg"), "memoryview"),
        ({1, 2, 3}, "set"),
        (frozenset({4, 5, 6, 6}), "frozenset"),
        ({"a": "b"}, "dict"),
        (type(int), "type"),
        (None, "object"),
    ],
)
def test_validates_standard_types(arg_value: Any, param_type: Any):
    params = {
        ANY_NAME: Parameter(
            ANY_NAME, Parameter.POSITIONAL_OR_KEYWORD, annotation=param_type
        )
    }

    validator = CallTypeValidator(ANY_NAME, params, (arg_value,), {})
    validator.validate()

    validator = CallTypeValidator(ANY_NAME, params, (), {ANY_NAME: arg_value})
    validator.validate()

    if arg_value is not None:
        validator = CallTypeValidator(ANY_NAME, params, (None,), {})
        with pytest.raises(TypeError):
            validator.validate()


@pytest.mark.parametrize(
    "arg_value,param_type",
    [
        (True, Union[bool, int]),
        (123, Union[bool, int]),
        ("yes", Optional[str]),
        (None, Optional[str]),
        (True, Union[bool, None]),
        (None, Union[bool, None]),
        # New union syntax in Python 3.10+ only
        *(
            [
                (True, bool | int),  # type: ignore
                (123, bool | int),  # type: ignore
                ("yes", str | None),  # type: ignore
                (None, str | None),  # type: ignore
            ]
            if sys.version_info[:3] >= (3, 10)
            else []
        ),
    ],
)
def test_validates_union_types(arg_value: Any, param_type: Any):
    params = {
        ANY_NAME: Parameter(ANY_NAME, Parameter.POSITIONAL_ONLY, annotation=param_type)
    }

    validator = CallTypeValidator(ANY_NAME, params, (arg_value,), {})
    validator.validate()

    if arg_value is not None:
        wrong_type: bytes = b"this shouldn't match the param_type"
        validator = CallTypeValidator(ANY_NAME, params, (wrong_type,), {})
        with pytest.raises(TypeError):
            validator.validate()


def test_validates_class_type():
    # Validate with collections.abc.Sized, a really simple (abstract) class type
    params = {
        ANY_NAME: Parameter(ANY_NAME, Parameter.POSITIONAL_ONLY, annotation=Sized)
    }

    sized_arg: Sized = [1, 2, 3]

    assert isinstance(sized_arg, Sized)

    unsized_arg = False

    validator = CallTypeValidator(ANY_NAME, params, (sized_arg,), {})
    validator.validate()

    validator = CallTypeValidator(ANY_NAME, params, (unsized_arg,), {})
    with pytest.raises(TypeError):
        validator.validate()


def test_validates_module_types():
    params = {
        ANY_NAME: Parameter(ANY_NAME, Parameter.POSITIONAL_ONLY, annotation=ModuleType)
    }

    validator = CallTypeValidator(ANY_NAME, params, (random,), {})
    validator.validate()

    validator = CallTypeValidator(ANY_NAME, params, ("not random at all",), {})
    with pytest.raises(TypeError):
        validator.validate()


def test_validates_callable_types():
    params = {
        ANY_NAME: Parameter(ANY_NAME, Parameter.POSITIONAL_ONLY, annotation=Callable)
    }

    validator = CallTypeValidator(ANY_NAME, params, (lambda: None,), {})
    validator.validate()

    validator = CallTypeValidator(ANY_NAME, params, ("not callable",), {})
    with pytest.raises(TypeError):
        validator.validate()


@pytest.mark.parametrize(
    "arg_value,param_type",
    [
        ({"x": 1, "y": 2}, dict[str, int]),
        ((1, 2, 3), tuple[int]),
        (
            [
                "generic",
                "type",
                "parameters",
                "can't",
                "actually",
                "be validated",
                "at",
                "runtime",
            ],
            list[int],
        ),
        (lambda: None, Callable[[bool, int], str]),
        (
            [
                "The",
                "contents",
                "of",
                "this",
                "Sequence",
                "can",
                "still",
                "be",
                "anything",
            ],
            Sequence[bool],
        ),
    ],
)
def test_validates_generic_types(arg_value: Any, param_type: Any):
    params = {
        ANY_NAME: Parameter(ANY_NAME, Parameter.POSITIONAL_ONLY, annotation=param_type)
    }

    validator = CallTypeValidator(ANY_NAME, params, (arg_value,), {})
    validator.validate()


@pytest.mark.parametrize(
    "bad_value,expected_type",
    [
        ([], dict[str, int]),
        ({}, tuple[int]),
        ((), list[int]),
        ("not callable", Callable[..., bool]),
        ({"not", "a", "Sequence"}, Sequence[str]),
    ],
)
def test_ensures_generic_origin_type(bad_value: Any, expected_type: Any):
    params = {
        ANY_NAME: Parameter(
            ANY_NAME, Parameter.POSITIONAL_ONLY, annotation=expected_type
        )
    }

    validator = CallTypeValidator(ANY_NAME, params, (bad_value,), {})
    with pytest.raises(TypeError):
        validator.validate()


def test_validates_generator():
    def generate() -> Generator[int, None, None]:
        yield from range(10)

    params = {
        ANY_NAME: Parameter(
            ANY_NAME, Parameter.POSITIONAL_ONLY, annotation=Generator[int, None, None]
        )
    }

    validator = CallTypeValidator(ANY_NAME, params, (generate(),), {})
    validator.validate()

    validator = CallTypeValidator(ANY_NAME, params, ([1, 2, 3],), {})
    with pytest.raises(TypeError):
        validator.validate()


def test_validates_typed_var_args():
    params = {"args": Parameter("args", Parameter.VAR_POSITIONAL, annotation=int)}

    validator = CallTypeValidator(ANY_NAME, params, (1,), {})
    validator.validate()

    validator = CallTypeValidator(ANY_NAME, params, (1, 2, 3), {})
    validator.validate()

    validator = CallTypeValidator(ANY_NAME, params, ("bad",), {})
    with pytest.raises(TypeError):
        validator.validate()

    validator = CallTypeValidator(ANY_NAME, params, (1, 2, "bad"), {})
    with pytest.raises(TypeError):
        validator.validate()


def test_validates_typed_var_kwargs():
    params = {"kwargs": Parameter("kwargs", Parameter.VAR_KEYWORD, annotation=int)}

    validator = CallTypeValidator(ANY_NAME, params, (), {"x": 1})
    validator.validate()

    validator = CallTypeValidator(ANY_NAME, params, (), {"x": 1, "y": 2, "z": 3})
    validator.validate()

    validator = CallTypeValidator(ANY_NAME, params, (), {"bad": "type"})
    with pytest.raises(TypeError):
        validator.validate()

    validator = CallTypeValidator(ANY_NAME, params, (), {"x": 1, "bad": "type"})
    with pytest.raises(TypeError):
        validator.validate()


@pytest.mark.parametrize(
    "arg,annotation,expect_match",
    [
        (1, int, True),
        (1.0, int, True),
        (1.0, float, True),
        (1, float, True),
        (1, Union[int, float], True),
        (1.0, Union[int, float], True),
        (1, bool, False),
        (1, str, False),
    ],
)
def test_type_match(arg: Any, annotation: Any, expect_match: bool):
    assert type_match(arg, annotation) == expect_match


@pytest.mark.parametrize(
    "arg,annotation,expect_match",
    [
        (1, int, True),
        (1.0, int, True),
        (1, float, True),
        (1, bool, False),
        ([], bool, False),
        ("", bool, False),
        ("", bool, False),
        (1, str, False),
        ("", bool, False),
        ("", str, True),
        ([], tuple, False),
        (tuple(), tuple, True),
        (True, bool, True),
        (False, bool, True),
        (b"hello", bytes, True),
    ],
)
def test_coercable_type_match(arg: Any, annotation: Any, expect_match: bool):
    assert _coercable_type_match(arg, annotation) == expect_match


def test_protocol_type_match_err():
    class ProtoType(Protocol):
        def do_the_thing(self) -> bool:
            ...

    class Implementation(ProtoType):
        def do_the_thing(self) -> bool:
            return True

    with pytest.raises(TypeError) as excinfo:
        type_match(Implementation(), ProtoType)

    assert "The Protocol type must be annotated with @runtime_checkable." in str(
        excinfo.value
    )
