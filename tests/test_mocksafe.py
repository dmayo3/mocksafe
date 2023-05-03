import pytest
from mocksafe import (
    safe_mock,
    stub,
    stub_implementation,
    num_calls,
    last_call,
    called,
)


class MyClass:
    def foo(self, bar: str, baz: int = 123) -> int:
        return baz + len(bar)


def test_safe_mock_isinstance_of_mocked_class():
    mock_object: MyClass = safe_mock(MyClass)

    assert isinstance(mock_object, MyClass)


def test_safe_mock_default_int_return_type():
    mock_object: MyClass = safe_mock(MyClass)

    assert mock_object.foo("hello") == 0


def test_assert_last_call():
    mock_object: MyClass = safe_mock(MyClass)

    mock_object.foo("hello")

    assert last_call(mock_object.foo) == ("hello",)


def test_assert_number_of_calls():
    mock_object: MyClass = safe_mock(MyClass)

    mock_object.foo("hello")
    mock_object.foo("world")
    mock_object.foo("!")

    assert num_calls(mock_object.foo) == 3


def test_assert_mock_not_called():
    assert not called(safe_mock(MyClass).foo)


def test_stub_return_value():
    mock_object: MyClass = safe_mock(MyClass)

    stub(mock_object.foo, 123456)

    assert mock_object.foo("hello") == 123456


def test_stub_with_lambda():
    mock_object: MyClass = safe_mock(MyClass)

    def stub_foo(bar: str, baz: int = 10) -> int:
        return baz + len(bar)

    stub_implementation(mock_object.foo, stub_foo)

    assert mock_object.foo("hello") == 15


@pytest.mark.xfail(strict=True, reason="Not yet implemented")
def test_stub_return_when_args_passed():
    assert False


@pytest.mark.xfail(strict=True, reason="Not yet implemented")
def test_stub_consecutive_calls():
    assert False


@pytest.mark.xfail(strict=True, reason="Not yet implemented")
def test_stub_raises_error():
    assert False


@pytest.mark.xfail(strict=True, reason="Not yet implemented")
def test_stub_return_when_arg_matches():
    assert False
