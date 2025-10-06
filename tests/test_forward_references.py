"""Tests for forward reference type annotation resolution."""

from typing import Any

import pytest
from mocksafe import mock
from mocksafe.apis.bdd import when


# Test classes WITHOUT future annotations (explicit string forward refs)
class ClassWithStringForwardRefs:
    """Test class with explicit string forward references."""

    def create(self) -> "ClassWithStringForwardRefs":
        """Factory method that returns the same class type."""
        instance = ClassWithStringForwardRefs()
        return instance

    def create_with_name(self, name: str) -> "ClassWithStringForwardRefs":
        """Factory method with parameters returning the same class type."""
        instance = ClassWithStringForwardRefs()
        # Store name as an attribute (not used in tests, just for completeness)
        _ = name  # Acknowledge unused parameter
        return instance

    def get_related(self) -> "OtherClassForStringRefs":
        """Method that returns a forward-referenced class."""
        return OtherClassForStringRefs()

    @classmethod
    def from_dict(
        cls: type["ClassWithStringForwardRefs"], data: dict
    ) -> "ClassWithStringForwardRefs":
        """Class method with forward reference return type."""
        _ = data  # Acknowledge unused parameter
        return cls()


class OtherClassForStringRefs:
    """Another class for forward reference testing."""

    def get_value(self) -> int:
        """Return a simple value."""
        return 42


# Test functions for explicit string forward references
def test_string_forward_reference_same_class():
    """Test stubbing a factory method with explicit string forward reference return type."""
    mock_obj = mock(ClassWithStringForwardRefs)
    result = ClassWithStringForwardRefs()

    when(mock_obj.create).any_call().then_return(result)
    assert mock_obj.create() is result


def test_string_forward_reference_same_class_with_args():
    """Test stubbing a factory method with arguments and string forward reference return type."""
    mock_obj = mock(ClassWithStringForwardRefs)
    result = ClassWithStringForwardRefs()

    # Call the method first, then stub it
    mock_obj.create_with_name("test")
    when(mock_obj.create_with_name).called_with(mock_obj.create_with_name("test")).then_return(
        result
    )
    assert mock_obj.create_with_name("test") is result


def test_string_forward_reference_other_class():
    """Test stubbing a method that returns a different forward-referenced class."""
    mock_obj = mock(ClassWithStringForwardRefs)
    result = OtherClassForStringRefs()

    when(mock_obj.get_related).any_call().then_return(result)
    assert mock_obj.get_related() is result


def test_string_class_method_with_forward_reference():
    """Test stubbing a class method with string forward reference return type."""
    mock_obj = mock(ClassWithStringForwardRefs)
    result = ClassWithStringForwardRefs()

    # Call the method first, then stub it
    mock_obj.from_dict({"key": "value"})
    when(mock_obj.from_dict).called_with(mock_obj.from_dict({"key": "value"})).then_return(result)
    assert mock_obj.from_dict({"key": "value"}) is result


# Test with from __future__ import annotations in local scope
def test_future_annotations_forward_reference():
    """Test forward references with future annotations enabled locally."""

    code = '''
from __future__ import annotations

class FutureAnnotationClass:
    """Class with future annotations."""

    def create(self) -> FutureAnnotationClass:
        """Factory method with future annotation."""
        return FutureAnnotationClass()

    def get_other(self) -> OtherFutureClass:
        """Method referencing another class."""
        return OtherFutureClass()

class OtherFutureClass:
    """Another class for testing."""

    def get_value(self) -> int:
        """Simple method."""
        return 123
'''

    # Execute the code with future annotations
    globals_dict: dict[str, type] = {}
    exec(code, globals_dict)  # noqa: S102  # pylint: disable=exec-used

    # Get the classes
    future_annotation_class = globals_dict["FutureAnnotationClass"]
    other_future_class = globals_dict["OtherFutureClass"]

    # Test mocking with future annotations
    mock_obj: Any = mock(future_annotation_class)
    result: Any = future_annotation_class()

    when(mock_obj.create).any_call().then_return(result)
    assert mock_obj.create() is result

    # Test cross-class reference
    other_result: Any = other_future_class()
    when(mock_obj.get_other).any_call().then_return(other_result)
    assert mock_obj.get_other() is other_result


def test_regular_type_annotation_still_works():
    """Test that regular (non-forward) type annotations still work correctly."""

    class SimpleClass:
        """Class with regular type annotations."""

        def get_number(self) -> int:
            """Method with regular type annotation."""
            return 42

    mock_obj = mock(SimpleClass)

    when(mock_obj.get_number).any_call().then_return(100)
    assert mock_obj.get_number() == 100

    # Test type validation - this should raise an error if we try to return wrong type
    with pytest.raises(TypeError, match="Cannot use stub result"):
        when(mock_obj.get_number).any_call().then_return("wrong type")  # type: ignore[arg-type]


def test_invalid_return_type_with_forward_reference():
    """Test that type validation works with resolved forward references."""
    mock_obj = mock(ClassWithStringForwardRefs)

    # This should work - returning the correct type
    when(mock_obj.create).any_call().then_return(ClassWithStringForwardRefs())

    # This should fail - returning wrong type
    with pytest.raises(TypeError, match="Cannot use stub result"):
        when(mock_obj.create).any_call().then_return("wrong type")  # type: ignore[arg-type]


def test_chained_forward_references():
    """Test classes that reference each other."""

    class ChainedA:
        """Class that references ChainedB."""

        def get_b(self) -> "ChainedB":
            """Get a ChainedB instance."""
            return ChainedB()

    class ChainedB:
        """Class that references ChainedA."""

        def get_a(self) -> "ChainedA":
            """Get a ChainedA instance."""
            return ChainedA()

    mock_a = mock(ChainedA)
    mock_b = mock(ChainedB)

    when(mock_a.get_b).any_call().then_return(mock_b)
    when(mock_b.get_a).any_call().then_return(mock_a)

    assert mock_a.get_b() is mock_b
    assert mock_b.get_a() is mock_a


def test_unresolvable_forward_reference():
    """Test handling of forward references that can't be resolved."""

    class LocalClass:
        """Local class with unresolvable forward reference."""

        def get_unknown(self) -> "NonExistentClass":  # type: ignore[name-defined]  # noqa: F821
            """Method with reference to non-existent class."""
            return None  # noqa: F821

    # This should not crash - the unresolvable annotation should be handled gracefully
    mock_obj = mock(LocalClass)

    # Since the type can't be resolved, it should accept any value with a warning
    when(mock_obj.get_unknown).any_call().then_return("any value")  # type: ignore[arg-type]
    assert mock_obj.get_unknown() == "any value"


def test_forward_reference_in_local_scope():
    """Test that forward references work in function local scope."""

    def inner_test():
        class InnerClass:
            """Class defined inside function."""

            def get_self(self) -> "InnerClass":
                """Method returning same class type."""
                return InnerClass()

        mock_obj = mock(InnerClass)
        result = InnerClass()

        when(mock_obj.get_self).any_call().then_return(result)
        assert mock_obj.get_self() is result

        return mock_obj.get_self()

    # Call the inner function to test local scope resolution
    inner_result = inner_test()
    assert inner_result is not None


def test_complex_generic_forward_reference():
    """Test handling of complex generic forward references."""

    # pylint: disable=import-outside-toplevel
    from typing import Generic, TypeVar

    T = TypeVar("T")  # noqa: N806

    class ComplexClass(Generic[T]):
        """Class with complex generic type annotations."""

        def complex_method(self) -> "ComplexClass[T]":
            """Method with complex forward reference."""
            return ComplexClass()

    # This should work despite the complex generic type
    mock_obj = mock(ComplexClass)
    result: Any = ComplexClass()

    when(mock_obj.complex_method).any_call().then_return(result)
    assert mock_obj.complex_method() is result


def test_builtin_type_string_annotation():
    """Test that built-in types as string annotations work correctly."""

    class BuiltinStringTypes:
        """Class with built-in types as string annotations."""

        def get_int(self) -> "int":
            """Method returning int via string annotation."""
            return 42

        def get_str(self) -> "str":
            """Method returning str via string annotation."""
            return "hello"

    mock_obj = mock(BuiltinStringTypes)

    when(mock_obj.get_int).any_call().then_return(100)
    assert mock_obj.get_int() == 100

    when(mock_obj.get_str).any_call().then_return("mocked")
    assert mock_obj.get_str() == "mocked"


def test_frame_stack_resolution():
    """Test that frame stack traversal works for finding types."""

    # Define a type at module level that will be in frame globals
    global ModuleLevelClass  # pylint: disable=global-variable-undefined

    class ModuleLevelClass:
        """Class defined at module level."""

    class ClassWithModuleRef:
        """Class referencing module-level class."""

        def get_module_class(self) -> "ModuleLevelClass":
            """Method that returns module-level class."""
            return ModuleLevelClass()

    mock_obj = mock(ClassWithModuleRef)
    result = ModuleLevelClass()

    when(mock_obj.get_module_class).any_call().then_return(result)
    assert mock_obj.get_module_class() is result


def test_frame_locals_resolution():
    """Test that forward references can find classes in local frame scope."""

    def function_with_local_classes():
        """Function containing local class definitions."""

        class LocalDefinedClass:
            """Class defined in function local scope."""

        class RefersToLocal:
            """Class that refers to locally defined class."""

            def get_local(self) -> "LocalDefinedClass":
                """Method that returns locally defined class."""
                return LocalDefinedClass()

        # Test that this resolves correctly
        mock_obj = mock(RefersToLocal)
        result = LocalDefinedClass()

        when(mock_obj.get_local).any_call().then_return(result)
        return mock_obj.get_local()

    # This should work - the forward reference should be resolved from function locals
    result = function_with_local_classes()
    assert result is not None
