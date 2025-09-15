from __future__ import annotations
import pytest
from typing import Any, cast
from mocksafe.core.mock import SafeMock, MethodMock, mock_reset


class TestClass:
    some_attribute: int = 123

    def foo(self: TestClass): ...

    @classmethod
    def class_method(cls: type[TestClass]) -> str:
        return cls.__name__

    @staticmethod
    def static_method() -> str:
        return "static"

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


def test_get_mocked_attr_extracts_correct_signature_for_class_methods():
    """Test that class method signatures include the cls parameter."""
    mock_object = SafeMock(TestClass)

    # Get the mocked method to check its signature
    mocked_class_method = mock_object.get_mocked_attr("class_method")
    assert isinstance(mocked_class_method, MethodMock)

    # The signature should include 'cls' as the first parameter
    signature = mocked_class_method._signature
    params = list(signature.parameters.values())

    # For now, this test will fail because we haven't implemented the fix yet
    # But it establishes what we expect once Stage 1 is complete
    assert len(params) >= 1, "Class method signature should have at least the cls parameter"
    first_param = params[0]
    assert first_param.name == "cls", f"First parameter should be 'cls', got '{first_param.name}'"


def test_get_mocked_attr_preserves_instance_method_signatures():
    """Test that instance method signatures are not affected by class method changes."""
    mock_object = SafeMock(TestClass)

    # Get the mocked instance method
    mocked_instance_method = mock_object.get_mocked_attr("foo")
    assert isinstance(mocked_instance_method, MethodMock)

    # Instance method signature should have 'self' parameter
    signature = mocked_instance_method._signature
    params = list(signature.parameters.values())

    assert len(params) >= 1, "Instance method signature should have at least the self parameter"
    first_param = params[0]
    assert first_param.name == "self", f"First parameter should be 'self', got '{first_param.name}'"


def test_get_mocked_attr_handles_static_methods():
    """Test that static method signatures are handled correctly."""
    mock_object = SafeMock(TestClass)

    # Get the mocked static method
    mocked_static_method = mock_object.get_mocked_attr("static_method")
    assert isinstance(mocked_static_method, MethodMock)

    # Static method should have no implicit first parameter
    signature = mocked_static_method._signature
    params = list(signature.parameters.values())

    # Static methods don't have self or cls parameters
    assert len(params) == 0, f"Static method should have 0 parameters, got {len(params)}"
