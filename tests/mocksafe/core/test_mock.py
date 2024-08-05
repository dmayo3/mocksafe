from __future__ import annotations
import pytest
from typing import Any, cast
from mocksafe.core.mock import SafeMock, MethodMock, mock_reset


class TestClass:
    some_attribute: int = 123

    def foo(self: TestClass):
        ...

    @property
    def bar(self: TestClass) -> int:
        return -1


def test_mock_reset():
    mock_object = SafeMock(TestClass)

    mock_object.foo()

    foo: MethodMock = mock_object.mocked_methods["foo"]

    assert len(foo.calls) == 1

    mock_reset(mock_object)

    assert len(foo.calls) == 0


def test_mock_set_and_get_simple_attribute():
    mock_object = cast(TestClass, SafeMock(TestClass))

    mock_object.some_attribute = 123

    assert mock_object.some_attribute == 123

    with pytest.raises(AttributeError):
        cast(Any, mock_object).does_not_exist = "this should be rejected"
