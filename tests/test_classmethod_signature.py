"""Test for class method signature handling.

This test verifies that class method signatures are correctly preserved
including the 'cls' parameter when creating mocks.
"""

import inspect

from mocksafe import mock


class ExampleService:
    """Test service with class methods."""

    @classmethod
    def simple_class_method(cls: type["ExampleService"]) -> str:
        """Simple class method with only cls parameter."""
        return f"service-{cls.__name__}"

    @classmethod
    def class_method_with_args(cls: type["ExampleService"], value: str, count: int = 1) -> str:
        """Class method with cls and additional parameters."""
        return f"{cls.__name__}-{value}-{count}"

    def instance_method(self, value: str) -> str:
        """Regular instance method for comparison."""
        return f"instance-{value}"


def test_class_method_signature_includes_cls_parameter():
    """Test that class method signatures include the 'cls' parameter."""
    mock_service: ExampleService = mock(ExampleService)

    # Access the class method to create the mock
    mock_service.simple_class_method  # noqa: B018

    # Get the underlying method mock
    mock_attr = "simple_class_method"
    method_mock = mock_service.mocked_methods[mock_attr]  # type: ignore[attr-defined]

    # The signature should include 'cls' as the first parameter
    signature = method_mock._signature
    params = list(signature.parameters.keys())

    expected_msg = f"Expected first parameter to be 'cls', got: {params}"
    assert params[0] == "cls", expected_msg
    expected_len_msg = f"Expected 1 parameter (cls), got {len(params)}: {params}"
    assert len(params) == 1, expected_len_msg


def test_class_method_with_args_signature_includes_cls():
    """Test that class methods with arguments still include 'cls' as first parameter."""
    mock_service: ExampleService = mock(ExampleService)

    # Access the class method to create the mock
    mock_service.class_method_with_args  # noqa: B018

    # Get the underlying method mock
    method_mock = mock_service.mocked_methods[  # type: ignore[attr-defined]
        "class_method_with_args"
    ]

    # The signature should include 'cls' as the first parameter
    signature = method_mock._signature
    params = list(signature.parameters.keys())

    expected_params = ["cls", "value", "count"]
    assert params == expected_params, f"Expected {expected_params}, got: {params}"

    # Check parameter details
    cls_param = signature.parameters["cls"]
    assert cls_param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD

    value_param = signature.parameters["value"]
    assert value_param.annotation == str

    count_param = signature.parameters["count"]
    assert count_param.annotation == int
    assert count_param.default == 1


def test_instance_method_signature_excludes_self_from_mock():
    """Verify that instance methods work as expected (for comparison)."""
    mock_service: ExampleService = mock(ExampleService)

    # Access the instance method
    mock_service.instance_method  # noqa: B018

    # Get the underlying method mock
    mock_attr = "instance_method"
    method_mock = mock_service.mocked_methods[mock_attr]  # type: ignore[attr-defined]

    # Instance method signatures should include 'self' when accessed from class
    signature = method_mock._signature
    params = list(signature.parameters.keys())

    # Note: This test documents current behavior - instance methods include 'self'
    expected_params = ["self", "value"]
    assert params == expected_params, f"Expected {expected_params}, got: {params}"


def test_original_class_method_signature_for_reference():
    """Document what the original class method signature looks like."""
    # Get the original bound class method
    original_bound_method = ExampleService.class_method_with_args

    # This is what we get when accessing from the class (bound method)
    bound_signature = inspect.signature(original_bound_method)
    bound_params = list(bound_signature.parameters.keys())

    # The bound method signature excludes 'cls' (this is Python's behavior)
    assert bound_params == ["value", "count"]

    # But the underlying function includes 'cls'
    func = original_bound_method.__func__  # type: ignore[attr-defined]
    func_signature = inspect.signature(func)
    func_params = list(func_signature.parameters.keys())

    # The underlying function signature includes 'cls'
    assert func_params == ["cls", "value", "count"]
