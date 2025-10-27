#!/usr/bin/env python
"""
Demonstration of MockSafe's improved error feedback with custom exceptions.

This file demonstrates the various error scenarios and the enhanced error
messages provided by the custom exception hierarchy.
"""

from mocksafe import mock, when, stub, MockProperty, spy
from mocksafe.exceptions import (
    MockTypeError,
    MockSetupError,
    MockUsageError,
    MockCallError,
    PropertyMockError,
)


class ExampleService:
    """Example service class for demonstration."""

    def process_data(self, value: int) -> str:
        """Process an integer and return a string."""
        return f"Processed: {value}"

    def get_items(self) -> list[str]:
        """Get a list of items."""
        return ["item1", "item2"]

    @property
    def status(self) -> str:
        """Get the service status."""
        return "active"

    @property
    def config(self) -> dict:
        """Get the service configuration."""
        return {"key": "value"}


def demonstrate_type_errors() -> None:
    """Demonstrate MockTypeError with enhanced messages."""
    print("\n=== MockTypeError Examples ===")

    service = mock(ExampleService)

    # Example 1: Wrong argument type
    when(service.process_data).any_call().then_return("result")
    try:
        service.process_data("wrong_type")  # type: ignore  # Expecting int, passing str
    except MockTypeError as e:
        print(f"Type Error 1:\n{e}\n")

    # Example 2: Wrong return type in stub
    try:
        # Should return List[str]
        when(service.get_items).any_call().then_return(123)  # type: ignore
    except MockTypeError as e:
        print(f"Type Error 2:\n{e}\n")


def demonstrate_setup_errors() -> None:
    """Demonstrate MockSetupError with enhanced messages."""
    print("\n=== MockSetupError Examples ===")

    # Example 1: Using when() on non-mocked object
    try:
        when("not_a_mock").any_call().then_return("value")  # type: ignore
    except MockSetupError as e:
        print(f"Setup Error 1:\n{e}\n")

    # Example 2: Using stub() on non-mocked object
    try:
        stub("not_a_mock").status = MockProperty("value")  # type: ignore
    except MockSetupError as e:
        print(f"Setup Error 2:\n{e}\n")


def demonstrate_usage_errors() -> None:
    """Demonstrate MockUsageError with enhanced messages."""
    print("\n=== MockUsageError Examples ===")

    service = mock(ExampleService)

    # Example: Using property without mocking it first
    try:
        _ = service.status
    except MockUsageError as e:
        print(f"Usage Error:\n{e}\n")


def demonstrate_call_errors() -> None:
    """Demonstrate MockCallError with enhanced messages."""
    print("\n=== MockCallError Examples ===")

    service = mock(ExampleService)
    when(service.process_data).any_call().then_return("result")

    # Example 1: Asserting on a method that wasn't called
    try:
        calls = spy(service.get_items)
        _ = calls.last_call
    except MockCallError as e:
        print(f"Call Error 1:\n{e}\n")

    # Example 2: Accessing nth call that doesn't exist
    service.process_data(1)  # Call it once
    try:
        calls = spy(service.process_data)
        _ = calls.nth_call(5)  # Try to get 6th call (index 5)
    except MockCallError as e:
        print(f"Call Error 2:\n{e}\n")


def demonstrate_property_errors() -> None:
    """Demonstrate PropertyMockError with enhanced messages."""
    print("\n=== PropertyMockError Examples ===")

    service = mock(ExampleService)

    # Example: Trying to mock a non-property attribute
    try:
        stub(service).process_data = MockProperty("value")
    except PropertyMockError as e:
        print(f"Property Error:\n{e}\n")


def demonstrate_type_validation_with_property() -> None:
    """Demonstrate type validation for MockProperty."""
    print("\n=== MockProperty Type Validation ===")

    service = mock(ExampleService)

    # Set up property mock with correct type
    stub(service).config = MockProperty({"initial": "config"})

    # Example: Trying to set incompatible type
    mock_prop = MockProperty(123)  # Initial value is int
    try:
        mock_prop.return_value = "string"  # Try to set string value
    except MockTypeError as e:
        print(f"Property Type Error:\n{e}\n")


def main() -> None:
    """Run all demonstrations."""
    print("=" * 60)
    print("MockSafe Enhanced Error Feedback Demonstration")
    print("=" * 60)

    demonstrate_type_errors()
    demonstrate_setup_errors()
    demonstrate_usage_errors()
    demonstrate_call_errors()
    demonstrate_property_errors()
    demonstrate_type_validation_with_property()

    print("\n" + "=" * 60)
    print("Demonstration Complete!")
    print("=" * 60)
    print("\nNotice how each error message includes:")
    print("1. A clear description of what went wrong")
    print("2. Context about the specific mock object/method involved")
    print("3. A helpful suggestion (💡) for how to fix the issue")
    print("\nThese custom exceptions make debugging mock-related issues")
    print("much easier and provide a better developer experience!")


if __name__ == "__main__":
    main()
