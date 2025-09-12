"""Black-box functional test for class method cls parameter behavior.

This test verifies that custom side effects for class methods receive
the correct 'cls' parameter, focusing on externally visible behavior.
"""

from __future__ import annotations

from mocksafe import mock, when


class ExampleService:
    """Example service with class methods that use the cls parameter."""

    @classmethod
    def get_service_name(cls) -> str:  # type: ignore[no-untyped-def]
        """Returns the class name - uses cls parameter."""
        return cls.__name__

    @classmethod
    def create_with_prefix(cls, prefix: str) -> str:  # type: ignore[no-untyped-def]
        """Creates a string using both cls and the argument."""
        return f"{prefix}-{cls.__name__}"

    @classmethod
    def factory_method(cls, config: str) -> ExampleService:  # type: ignore[no-untyped-def]
        """Factory method that would typically return an instance."""
        instance = cls()
        instance.config = config
        return instance

    def __init__(self):
        self.config = "default"


def test_class_method_custom_side_effect_receives_cls_parameter():
    """Test that custom side effects for class methods get the cls parameter."""
    mock_service: ExampleService = mock(ExampleService)

    # Custom side effect that expects to receive cls as first argument
    def custom_name_generator(cls) -> str:  # type: ignore[no-untyped-def]
        """Side effect that uses the cls parameter."""
        return f"Custom-{cls.__name__}-Service"

    when(mock_service.get_service_name).any_call().then(custom_name_generator)

    # This should work - the side effect should receive the class as 'cls'
    result = mock_service.get_service_name()
    assert result == "Custom-ExampleService-Service"


def test_class_method_custom_side_effect_with_additional_args():
    """Test custom side effects with cls plus additional arguments."""
    mock_service: ExampleService = mock(ExampleService)

    # Custom side effect expecting cls + additional args
    def custom_creator(cls, prefix: str) -> str:  # type: ignore[no-untyped-def]
        """Side effect that uses both cls and the prefix argument."""
        return f"Created-{prefix}-by-{cls.__name__}"

    when(mock_service.create_with_prefix).any_call().then(custom_creator)

    # This should work - side effect gets both cls and the prefix argument
    result = mock_service.create_with_prefix("test")
    assert result == "Created-test-by-ExampleService"


def test_class_method_factory_pattern_with_cls():
    """Test factory method pattern where side effect uses cls."""
    mock_service: ExampleService = mock(ExampleService)

    # Factory side effect that creates instances using cls
    def custom_factory(cls, config: str) -> ExampleService:  # type: ignore[no-untyped-def]
        """Factory that creates instances using the cls parameter."""
        instance = cls()  # Use the cls to create instance
        instance.config = f"factory-{config}"
        return instance

    when(mock_service.factory_method).any_call().then(custom_factory)

    # This should work - factory gets cls and can create instances
    result = mock_service.factory_method("test-config")
    assert hasattr(result, "config")
    assert result.config == "factory-test-config"


def test_class_method_conditional_stubbing_with_cls():
    """Test conditional stubbing where side effect logic depends on cls."""
    mock_service: ExampleService = mock(ExampleService)

    # Conditional side effect based on both cls and arguments
    def conditional_processor(cls, prefix: str) -> str:  # type: ignore[no-untyped-def]
        """Side effect with conditional logic using cls."""
        if cls.__name__ == "ExampleService":
            return f"Special-{prefix}-Service"
        return f"Generic-{prefix}-Service"

    when(mock_service.create_with_prefix).called_with(
        mock_service.create_with_prefix("special")
    ).then(conditional_processor)

    # The side effect should receive cls and make decisions based on it
    result = mock_service.create_with_prefix("special")
    assert result == "Special-special-Service"


def test_multiple_class_method_calls_preserve_cls():
    """Test that cls parameter is consistently passed across multiple calls."""
    mock_service: ExampleService = mock(ExampleService)

    # Track calls to verify cls is always passed correctly
    call_log = []

    def logging_side_effect(cls, prefix: str) -> str:  # type: ignore[no-untyped-def]
        """Side effect that logs the cls it receives."""
        call_log.append(cls.__name__)
        return f"Call-{len(call_log)}-{prefix}-{cls.__name__}"

    when(mock_service.create_with_prefix).any_call().then(logging_side_effect)

    # Make multiple calls
    result1 = mock_service.create_with_prefix("first")
    result2 = mock_service.create_with_prefix("second")

    # Verify cls was passed correctly for both calls
    assert result1 == "Call-1-first-ExampleService"
    assert result2 == "Call-2-second-ExampleService"
    assert call_log == ["ExampleService", "ExampleService"]
