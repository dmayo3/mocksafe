"""
Custom exceptions for MockSafe with enhanced error messages and traceback filtering.

This module provides a hierarchy of exceptions specific to MockSafe operations,
making it easier for users to identify and handle mock-related errors.
"""

from typing import Any


class MockSafeError(Exception):
    """
    Base exception for all MockSafe-specific errors.

    This allows users to catch all MockSafe errors with a single except clause
    while maintaining backward compatibility with built-in exceptions.
    """

    def __init__(self, message: str, suggestion: str | None = None):
        """
        Initialize a MockSafe exception.

        :param message: The error message
        :param suggestion: Optional suggestion for how to fix the error
        """
        self.message = message
        self.suggestion = suggestion

        full_message = message
        if suggestion:
            full_message += f"\n💡 Suggestion: {suggestion}"

        super().__init__(full_message)

    def filter_traceback(self) -> None:
        """
        Filter the traceback to remove internal MockSafe frames.
        This makes error messages cleaner and more focused on user code.
        """
        if not hasattr(self, "__traceback__"):
            return

        tb = self.__traceback__
        frames_to_keep = []

        while tb is not None:
            frame = tb.tb_frame
            filename = frame.f_code.co_filename

            # Keep frames that are not from mocksafe internals
            # But always keep the frame where the exception was raised
            if not self._is_internal_frame(filename) or tb.tb_next is None:
                frames_to_keep.append(tb)

            tb = tb.tb_next

        # Note: In Python, we can't actually modify the traceback easily
        # This is more of a placeholder for potential future implementation
        # For now, we'll rely on good error messages

    def _is_internal_frame(self, filename: str) -> bool:
        """Check if a frame is from MockSafe internals."""
        return "mocksafe/core" in filename or "mocksafe/apis" in filename


class MockTypeError(MockSafeError, TypeError):
    """
    Raised when there's a type mismatch in mock operations.

    This includes:
    - Wrong argument types passed to mocked methods
    - Incompatible return types in stubs
    - Invalid MockProperty types
    """

    def __init__(
        self,
        message: str,
        expected_type: Any | None = None,
        actual_type: Any | None = None,
        suggestion: str | None = None,
    ):
        """
        Initialize a MockTypeError.

        :param message: The error message
        :param expected_type: The expected type (if applicable)
        :param actual_type: The actual type received (if applicable)
        :param suggestion: Optional suggestion for fixing the error
        """
        self.expected_type = expected_type
        self.actual_type = actual_type

        if expected_type and actual_type and not suggestion:
            suggestion = f"Expected type {expected_type}, but got {actual_type}"

        super().__init__(message, suggestion)


class MockSetupError(MockSafeError, ValueError):
    """
    Raised when there's an error in mock setup or configuration.

    This includes:
    - Trying to mock non-existent attributes
    - Invalid mock configurations
    - Stubbing errors
    """

    def __init__(
        self,
        message: str,
        mock_object: Any | None = None,
        attribute: str | None = None,
        suggestion: str | None = None,
    ):
        """
        Initialize a MockSetupError.

        :param message: The error message
        :param mock_object: The mock object involved (if applicable)
        :param attribute: The attribute being mocked (if applicable)
        :param suggestion: Optional suggestion for fixing the error
        """
        self.mock_object = mock_object
        self.attribute = attribute

        if not suggestion and mock_object and attribute:
            suggestion = f"Ensure that '{attribute}' exists on the original object"

        super().__init__(message, suggestion)


class MockUsageError(MockSafeError, ValueError):
    """
    Raised when a mock is used incorrectly.

    This includes:
    - Calling unmocked methods/properties
    - Accessing calls that haven't happened
    - Using mocks in unexpected ways
    """

    def __init__(self, message: str, method_name: str | None = None, suggestion: str | None = None):
        """
        Initialize a MockUsageError.

        :param message: The error message
        :param method_name: The method/property name (if applicable)
        :param suggestion: Optional suggestion for fixing the error
        """
        self.method_name = method_name

        if not suggestion and method_name:
            suggestion = f"Make sure to mock or stub '{method_name}' before using it"

        super().__init__(message, suggestion)


class MockCallError(MockSafeError, ValueError):
    """
    Raised when there's an error related to mock call verification.

    This includes:
    - Verifying calls that didn't happen
    - Wrong number of calls
    - Call order issues
    """

    def __init__(
        self,
        message: str,
        expected_calls: int | None = None,
        actual_calls: int | None = None,
        method_name: str | None = None,
        suggestion: str | None = None,
    ):
        """
        Initialize a MockCallError.

        :param message: The error message
        :param expected_calls: Expected number of calls (if applicable)
        :param actual_calls: Actual number of calls (if applicable)
        :param method_name: The method name (if applicable)
        :param suggestion: Optional suggestion for fixing the error
        """
        self.expected_calls = expected_calls
        self.actual_calls = actual_calls
        self.method_name = method_name

        if not suggestion and expected_calls is not None and actual_calls is not None:
            if actual_calls == 0:
                suggestion = f"The method '{method_name}' was never called. Check your test logic."
            else:
                suggestion = f"Expected {expected_calls} calls, but got {actual_calls}"

        super().__init__(message, suggestion)


class StubError(MockSafeError, ValueError):
    """
    Raised when there's an error in stub configuration.

    This includes:
    - Invalid stub configurations
    - Conflicting stub setups
    - Stub type mismatches
    """

    def __init__(self, message: str, stub_target: str | None = None, suggestion: str | None = None):
        """
        Initialize a StubError.

        :param message: The error message
        :param stub_target: What was being stubbed (if applicable)
        :param suggestion: Optional suggestion for fixing the error
        """
        self.stub_target = stub_target

        if not suggestion and stub_target:
            suggestion = f"Check your stub configuration for '{stub_target}'"

        super().__init__(message, suggestion)


class PropertyMockError(MockSafeError, ValueError):
    """
    Raised when there's an error with property mocking.

    This includes:
    - Trying to mock non-properties
    - Property type mismatches
    - Invalid property configurations
    """

    def __init__(
        self, message: str, property_name: str | None = None, suggestion: str | None = None
    ):
        """
        Initialize a PropertyMockError.

        :param message: The error message
        :param property_name: The property name (if applicable)
        :param suggestion: Optional suggestion for fixing the error
        """
        self.property_name = property_name

        if not suggestion and property_name:
            suggestion = f"Ensure '{property_name}' is a property (decorated with @property)"

        super().__init__(message, suggestion)


def format_call_args(args: tuple, kwargs: dict) -> str:
    """
    Format call arguments for display in error messages.

    :param args: Positional arguments
    :param kwargs: Keyword arguments
    :return: Formatted string representation
    """
    arg_parts: list[str] = []

    if args:
        arg_parts.extend(repr(arg) for arg in args)

    if kwargs:
        arg_parts.extend(f"{k}={repr(v)}" for k, v in kwargs.items())

    return f"({', '.join(arg_parts)})"


def format_type_path(type_obj: Any) -> str:
    """
    Format a type object for display in error messages.

    :param type_obj: The type object
    :return: Human-readable type representation
    """
    if hasattr(type_obj, "__module__") and hasattr(type_obj, "__qualname__"):
        if type_obj.__module__ in ("builtins", "__main__"):
            return type_obj.__qualname__
        return f"{type_obj.__module__}.{type_obj.__qualname__}"

    return str(type_obj)


# Backward compatibility aliases
MockSafeTypeError = MockTypeError
MockSafeValueError = MockUsageError


__all__ = [
    "MockSafeError",
    "MockTypeError",
    "MockSetupError",
    "MockUsageError",
    "MockCallError",
    "StubError",
    "PropertyMockError",
    "format_call_args",
    "format_type_path",
    # Compatibility aliases
    "MockSafeTypeError",
    "MockSafeValueError",
]
