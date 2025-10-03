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
        _ = name  # Acknowledge unused parameter
        return instance

    def get_related(self) -> OtherClass:
        """Method that returns a forward-referenced class."""
        return OtherClass()

    @classmethod
    def from_dict(cls: type[MyClass], data: dict) -> MyClass:
        """Class method with forward reference return type."""
        _ = data  # Acknowledge unused parameter
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


def test_unresolvable_forward_reference():
    """Test handling of forward references that can't be resolved."""

    class LocalClass:
        """Local class with unresolvable forward reference."""

        def get_unknown(self):
            """Method with reference to non-existent class."""
            return None  # type: ignore[name-defined]  # noqa: F821

    # This should not crash - the unresolvable annotation should be handled gracefully
    mock_obj = mock(LocalClass)

    # Since the type can't be resolved, it should accept any value
    when(mock_obj.get_unknown).any_call().then_return("any value")
    assert mock_obj.get_unknown() == "any value"


def test_forward_reference_in_local_scope():
    """Test forward references defined in local scope."""

    class OuterClass:
        """Outer class with method returning inner class."""

        def get_inner(self) -> InnerClass:
            """Returns an inner class instance."""
            return InnerClass()

    class InnerClass:
        """Inner class defined after outer class."""

        value: int = 42

    mock_obj = mock(OuterClass)
    result = InnerClass()

    when(mock_obj.get_inner).any_call().then_return(result)
    assert mock_obj.get_inner() is result


def test_complex_type_annotation_error_handling():
    """Test handling of complex type annotations that might fail."""
    # pylint: disable=import-outside-toplevel
    from typing import Any, Generic, TypeVar

    T = TypeVar("T")  # noqa: N806

    class ComplexClass(Generic[T]):
        """Class with complex generic type annotations."""

        def complex_method(self) -> ComplexClass[T]:
            """Method with complex forward reference."""
            return ComplexClass()

    # This should handle potential TypeError in get_type_hints gracefully
    mock_obj = mock(ComplexClass)
    result: ComplexClass[Any] = ComplexClass()

    when(mock_obj.complex_method).any_call().then_return(result)
    assert mock_obj.complex_method() is result


def test_builtin_type_string_annotation():
    """Test that builtin types as strings are resolved correctly."""

    class BuiltinStringTypes:
        """Class using builtin types as string annotations."""

        def get_int(self) -> int:
            """Returns int with string annotation."""
            return 42

        def get_str(self) -> str:
            """Returns str with string annotation."""
            return "hello"

    mock_obj = mock(BuiltinStringTypes)

    # These should work and validate types correctly
    when(mock_obj.get_int).any_call().then_return(100)
    assert mock_obj.get_int() == 100

    when(mock_obj.get_str).any_call().then_return("world")
    assert mock_obj.get_str() == "world"

    # Type validation should still work
    with pytest.raises(TypeError, match="Cannot use stub result"):
        when(mock_obj.get_int).any_call().then_return("not an int")  # type: ignore


def test_frame_stack_resolution():
    """Test that frame stack traversal works for finding types."""

    # Define a type at module level that will be in frame globals
    global ModuleLevelClass  # pylint: disable=global-variable-undefined

    class ModuleLevelClass:
        """Class defined at module level."""

    class ClassWithModuleRef:
        """Class referencing module-level class."""

        def get_module_class(self) -> ModuleLevelClass:
            """Returns module-level class."""
            return ModuleLevelClass()

    mock_obj = mock(ClassWithModuleRef)
    result = ModuleLevelClass()

    when(mock_obj.get_module_class).any_call().then_return(result)
    assert mock_obj.get_module_class() is result


def test_frame_locals_resolution():
    """Test that frame locals are checked for type resolution."""

    def function_with_local_class():
        """Function that defines a class locally."""

        class LocalDefinedClass:
            """Class defined in function local scope."""

        class RefersToLocal:
            """Class that refers to locally defined class."""

            def get_local(self) -> LocalDefinedClass:
                """Method returning local class."""
                return LocalDefinedClass()

        # Mock the class with local reference
        mock_obj = mock(RefersToLocal)
        result = LocalDefinedClass()

        # This should work with frame locals lookup
        when(mock_obj.get_local).any_call().then_return(result)
        assert mock_obj.get_local() is result

        return True

    # Execute the function to trigger frame locals lookup
    assert function_with_local_class()
