"""
Tests for the custom exception classes in mocksafe.exceptions module.
"""

import pytest
from mocksafe.exceptions import (
    MockSafeError,
    MockTypeError,
    MockSetupError,
    MockUsageError,
    MockCallError,
    StubError,
    PropertyMockError,
    format_call_args,
    format_type_path,
)


class TestMockSafeError:
    """Test the base MockSafeError class."""

    def test_basic_initialization(self):
        """Test basic exception initialization."""
        exc = MockSafeError("Test error message")
        assert str(exc) == "Test error message"
        assert exc.message == "Test error message"
        assert exc.suggestion is None

    def test_initialization_with_suggestion(self):
        """Test exception initialization with suggestion."""
        exc = MockSafeError("Test error", suggestion="Try this instead")
        assert "Test error" in str(exc)
        assert "💡 Suggestion: Try this instead" in str(exc)
        assert exc.suggestion == "Try this instead"

    def test_inheritance(self):
        """Test that MockSafeError inherits from Exception."""
        exc = MockSafeError("Test")
        assert isinstance(exc, Exception)


class TestMockTypeError:
    """Test the MockTypeError class."""

    def test_basic_initialization(self):
        """Test basic MockTypeError initialization."""
        exc = MockTypeError("Type mismatch error")
        assert "Type mismatch error" in str(exc)
        assert isinstance(exc, TypeError)
        assert isinstance(exc, MockSafeError)

    def test_with_expected_and_actual_types(self):
        """Test MockTypeError with type information."""
        exc = MockTypeError(
            "Type error",
            expected_type=int,
            actual_type=str,
        )
        assert "Type error" in str(exc)
        assert "Expected type <class 'int'>, but got <class 'str'>" in str(exc)

    def test_with_custom_suggestion(self):
        """Test MockTypeError with custom suggestion."""
        exc = MockTypeError(
            "Type error", expected_type=int, actual_type=str, suggestion="Use an integer value"
        )
        assert "Use an integer value" in str(exc)
        assert "Expected type" not in str(exc)  # Custom suggestion overrides default

    def test_inheritance_chain(self):
        """Test that MockTypeError has correct inheritance."""
        exc = MockTypeError("Test")
        assert isinstance(exc, TypeError)
        assert isinstance(exc, MockSafeError)
        assert isinstance(exc, Exception)


class TestMockSetupError:
    """Test the MockSetupError class."""

    def test_basic_initialization(self):
        """Test basic MockSetupError initialization."""
        exc = MockSetupError("Setup failed")
        assert "Setup failed" in str(exc)
        assert isinstance(exc, ValueError)
        assert isinstance(exc, MockSafeError)

    def test_with_mock_object_and_attribute(self):
        """Test MockSetupError with context information."""
        mock_obj = "MockObject"
        exc = MockSetupError("Setup error", mock_object=mock_obj, attribute="test_attr")
        assert "Setup error" in str(exc)
        assert "Ensure that 'test_attr' exists on the original object" in str(exc)

    def test_with_custom_suggestion(self):
        """Test MockSetupError with custom suggestion."""
        exc = MockSetupError(
            "Setup error", mock_object="obj", attribute="attr", suggestion="Custom fix"
        )
        assert "Custom fix" in str(exc)
        assert "Ensure that" not in str(exc)  # Custom suggestion overrides default


class TestMockUsageError:
    """Test the MockUsageError class."""

    def test_basic_initialization(self):
        """Test basic MockUsageError initialization."""
        exc = MockUsageError("Usage error")
        assert "Usage error" in str(exc)
        assert isinstance(exc, ValueError)
        assert isinstance(exc, MockSafeError)

    def test_with_method_name(self):
        """Test MockUsageError with method name."""
        exc = MockUsageError("Error", method_name="test_method")
        assert "Error" in str(exc)
        assert "Make sure to mock or stub 'test_method' before using it" in str(exc)

    def test_with_custom_suggestion(self):
        """Test MockUsageError with custom suggestion."""
        exc = MockUsageError("Error", method_name="method", suggestion="Do this instead")
        assert "Do this instead" in str(exc)


class TestMockCallError:
    """Test the MockCallError class."""

    def test_basic_initialization(self):
        """Test basic MockCallError initialization."""
        exc = MockCallError("Call error")
        assert "Call error" in str(exc)
        assert isinstance(exc, ValueError)
        assert isinstance(exc, MockSafeError)

    def test_with_call_counts(self):
        """Test MockCallError with call count information."""
        exc = MockCallError(
            "Wrong number of calls", expected_calls=3, actual_calls=1, method_name="test_method"
        )
        assert "Wrong number of calls" in str(exc)
        assert "Expected 3 calls, but got 1" in str(exc)

    def test_with_zero_calls(self):
        """Test MockCallError when method was never called."""
        exc = MockCallError(
            "Method not called", expected_calls=1, actual_calls=0, method_name="test_method"
        )
        assert "Method not called" in str(exc)
        assert "The method 'test_method' was never called" in str(exc)

    def test_with_custom_suggestion(self):
        """Test MockCallError with custom suggestion."""
        exc = MockCallError("Error", expected_calls=2, actual_calls=1, suggestion="Check your test")
        assert "Check your test" in str(exc)


class TestStubError:
    """Test the StubError class."""

    def test_basic_initialization(self):
        """Test basic StubError initialization."""
        exc = StubError("Stub configuration error")
        assert "Stub configuration error" in str(exc)
        assert isinstance(exc, ValueError)
        assert isinstance(exc, MockSafeError)

    def test_with_stub_target(self):
        """Test StubError with stub target."""
        exc = StubError("Error", stub_target="test_method")
        assert "Error" in str(exc)
        assert "Check your stub configuration for 'test_method'" in str(exc)

    def test_with_custom_suggestion(self):
        """Test StubError with custom suggestion."""
        exc = StubError("Error", stub_target="target", suggestion="Fix it this way")
        assert "Fix it this way" in str(exc)


class TestPropertyMockError:
    """Test the PropertyMockError class."""

    def test_basic_initialization(self):
        """Test basic PropertyMockError initialization."""
        exc = PropertyMockError("Property error")
        assert "Property error" in str(exc)
        assert isinstance(exc, ValueError)
        assert isinstance(exc, MockSafeError)

    def test_with_property_name(self):
        """Test PropertyMockError with property name."""
        exc = PropertyMockError("Error", property_name="test_prop")
        assert "Error" in str(exc)
        assert "Ensure 'test_prop' is a property (decorated with @property)" in str(exc)

    def test_with_custom_suggestion(self):
        """Test PropertyMockError with custom suggestion."""
        exc = PropertyMockError("Error", property_name="prop", suggestion="Use @property decorator")
        assert "Use @property decorator" in str(exc)


class TestHelperFunctions:
    """Test helper functions in the exceptions module."""

    def test_format_call_args_empty(self):
        """Test formatting empty call arguments."""
        result = format_call_args((), {})
        assert result == "()"

    def test_format_call_args_only_positional(self):
        """Test formatting positional arguments only."""
        result = format_call_args((1, "test", None), {})
        assert result == "(1, 'test', None)"

    def test_format_call_args_only_kwargs(self):
        """Test formatting keyword arguments only."""
        result = format_call_args((), {"key": "value", "num": 42})
        assert result == "(key='value', num=42)"

    def test_format_call_args_mixed(self):
        """Test formatting mixed arguments."""
        result = format_call_args((1, "test"), {"key": "value"})
        assert result == "(1, 'test', key='value')"

    def test_format_type_path_builtin(self):
        """Test formatting builtin types."""
        assert format_type_path(int) == "int"
        assert format_type_path(str) == "str"
        assert format_type_path(list) == "list"

    def test_format_type_path_custom_class(self):
        """Test formatting custom class types."""

        class CustomClass:
            pass

        result = format_type_path(CustomClass)
        assert "CustomClass" in result

    def test_format_type_path_fallback(self):
        """Test formatting with fallback to str()."""
        # Test with something that doesn't have __module__ or __qualname__
        result = format_type_path(42)  # int instance, not type
        assert result == "42"


class TestBackwardCompatibility:
    """Test backward compatibility aliases."""

    def test_mocksafe_type_error_alias(self):
        """Test that MockSafeTypeError is an alias for MockTypeError."""
        from mocksafe.exceptions import MockSafeTypeError

        assert MockSafeTypeError is MockTypeError

    def test_mocksafe_value_error_alias(self):
        """Test that MockSafeValueError is an alias for MockUsageError."""
        from mocksafe.exceptions import MockSafeValueError

        assert MockSafeValueError is MockUsageError


class TestExceptionCatching:
    """Test that exceptions can be caught at different levels."""

    def test_catch_specific_exception(self):
        """Test catching specific exception types."""
        with pytest.raises(MockTypeError):
            raise MockTypeError("Test")

    def test_catch_as_base_exception(self):
        """Test catching as MockSafeError base class."""
        with pytest.raises(MockSafeError):
            raise MockTypeError("Test")

        with pytest.raises(MockSafeError):
            raise MockSetupError("Test")

    def test_catch_as_builtin_exception(self):
        """Test catching as builtin exception types."""
        with pytest.raises(TypeError):
            raise MockTypeError("Test")

        with pytest.raises(ValueError):
            raise MockUsageError("Test")

    def test_exception_attributes(self):
        """Test that exception attributes are accessible."""
        exc = MockCallError("Test", expected_calls=5, actual_calls=3, method_name="test_method")
        assert exc.expected_calls == 5
        assert exc.actual_calls == 3
        assert exc.method_name == "test_method"
        assert exc.message == "Test"
