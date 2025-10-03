"""Tests for forward reference type annotations support."""

from __future__ import annotations

import pytest
from mocksafe import mock
from mocksafe.apis.bdd import when


class MyClass:
    """Test class with forward reference return types."""

    def create(self) -> MyClass:
        """Factory method that returns an instance of its own class."""
        return MyClass()

    def create_with_args(self, name: str) -> MyClass:
        """Factory method with arguments."""
        instance = MyClass()
        # Store name as an attribute (not used in tests, just for completeness)
        return instance

    def get_related(self) -> OtherClass:
        """Method that returns a forward-referenced class."""
        return OtherClass()

    @classmethod
    def from_dict(cls: type[MyClass], data: dict) -> MyClass:
        """Class method with forward reference return type."""
        return cls()


class OtherClass:
    """Another test class."""

    def get_my_class(self) -> MyClass:
        """Method that returns MyClass without forward reference."""
        return MyClass()


def test_forward_reference_same_class():
    """Test stubbing a method that returns its own class type using forward reference."""
    mock_obj = mock(MyClass)
    result = MyClass()

    # This should work with forward reference return type
    when(mock_obj.create).any_call().then_return(result)

    assert mock_obj.create() is result


def test_forward_reference_same_class_with_args():
    """Test stubbing a factory method with arguments and forward reference return type."""
    mock_obj = mock(MyClass)
    result = MyClass()

    when(mock_obj.create_with_args).called_with(mock_obj.create_with_args("test")).then_return(
        result
    )

    assert mock_obj.create_with_args("test") is result


def test_forward_reference_other_class():
    """Test stubbing a method that returns another class using forward reference."""
    mock_obj = mock(MyClass)
    result = OtherClass()

    when(mock_obj.get_related).any_call().then_return(result)

    assert mock_obj.get_related() is result


def test_class_method_with_forward_reference():
    """Test stubbing a class method with forward reference return type."""
    mock_obj = mock(MyClass)
    result = MyClass()

    when(mock_obj.from_dict).called_with(mock_obj.from_dict({"key": "value"})).then_return(result)

    assert mock_obj.from_dict({"key": "value"}) is result


def test_regular_type_annotation_still_works():
    """Test that regular (non-forward-reference) type annotations still work."""
    mock_obj = mock(OtherClass)
    result = MyClass()

    when(mock_obj.get_my_class).any_call().then_return(result)

    assert mock_obj.get_my_class() is result


def test_invalid_return_type_with_forward_reference():
    """Test that type validation still works with forward references."""
    mock_obj = mock(MyClass)

    # This should raise a TypeError because we're trying to return
    # an incompatible type (string instead of MyClass)
    with pytest.raises(TypeError, match="Cannot use stub result"):
        # Intentionally passing wrong type to test error handling
        when(mock_obj.create).any_call().then_return("not a MyClass instance")  # type: ignore


def test_chained_forward_references():
    """Test methods that return instances used in chained calls."""
    mock_obj = mock(MyClass)
    mock_result = mock(MyClass)
    another_result = mock(MyClass)

    when(mock_obj.create).any_call().then_return(mock_result)
    when(mock_result.create).any_call().then_return(another_result)

    assert mock_obj.create().create() is another_result
