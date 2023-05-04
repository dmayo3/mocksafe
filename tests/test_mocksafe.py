import pytest
from mocksafe import mock, when, that


class MyClass:
    def foo(self, bar: str, baz: int = 123) -> int:
        return baz + len(bar)


def test_mock_isinstance_of_mocked_class():
    mock_object: MyClass = mock(MyClass)

    assert isinstance(mock_object, MyClass)


def test_mock_default_int_return_type():
    mock_object: MyClass = mock(MyClass)

    assert mock_object.foo("hello") == 0


def test_assert_last_call():
    mock_object: MyClass = mock(MyClass)

    mock_object.foo("hello")

    assert that(mock_object.foo).last_call == ("hello",)


def test_assert_number_of_calls():
    mock_object: MyClass = mock(MyClass)

    mock_object.foo("hello")
    mock_object.foo("world")
    mock_object.foo("!")

    assert that(mock_object.foo).num_calls == 3


def test_assert_mock_not_called():
    mock_object: MyClass = mock(MyClass)
    assert that(mock_object.foo).was_not_called


def test_stub_return_value():
    mock_object: MyClass = mock(MyClass)

    when(mock_object.foo).any_call().then_return(123456)

    assert mock_object.foo("hello") == 123456


def test_stub_return_when_args_passed():
    mock_object: MyClass = mock(MyClass)

    when(mock_object.foo).called_with(mock_object.foo("hi", baz=3)).then_return(678)

    assert mock_object.foo("hi", baz=3) == 678

    assert mock_object.foo("hi") == 0
    assert mock_object.foo("hi", baz=1) == 0
    assert mock_object.foo("hello") == 0


def test_stub_consecutive_calls():
    mock_object: MyClass = mock(MyClass)
    when(mock_object.foo).any_call().then_return(123, 456, 789)

    assert mock_object.foo("a") == 123
    assert mock_object.foo("b") == 456
    assert mock_object.foo("c") == 789
    assert mock_object.foo("d") == 789


@pytest.mark.xfail(strict=True, reason="Not yet implemented")
def test_stub_raises_error():
    assert False


@pytest.mark.xfail(strict=True, reason="Not yet implemented")
def test_stub_return_when_arg_matches():
    assert False
