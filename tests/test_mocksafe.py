import pytest
from mocksafe import mock, when, that


class MyClass:
    def foo(self, bar: str, baz: int = 123) -> int:
        return baz + len(bar)

    def quux(self) -> str | None:
        return "something"


def test_mock_isinstance_of_mocked_class():
    mock_object: MyClass = mock(MyClass)

    assert isinstance(mock_object, MyClass)


def test_mock_default_int_return_type():
    mock_object: MyClass = mock(MyClass)

    assert mock_object.foo("hello") == 0


def test_assert_last_call_args():
    mock_object: MyClass = mock(MyClass)

    mock_object.foo("hello")

    assert that(mock_object.foo).last_call == ("hello",)


def test_assert_last_call_kwargs():
    mock_object: MyClass = mock(MyClass)

    mock_object.foo(bar="hello", baz=456)

    assert that(mock_object.foo).last_call == ((), {"bar": "hello", "baz": 456})


def test_assert_last_call_mixed_args():
    mock_object: MyClass = mock(MyClass)

    mock_object.foo("hello", baz=456)

    assert that(mock_object.foo).last_call == (("hello",), {"baz": 456})


def test_assert_number_of_calls():
    mock_object: MyClass = mock(MyClass)

    mock_object.foo("hello")
    mock_object.foo("world")
    mock_object.foo("!")

    assert that(mock_object.foo).num_calls == 3


def test_assert_nth_call():
    mock_object: MyClass = mock(MyClass)

    mock_object.foo("hello")
    mock_object.foo("world")
    mock_object.foo("!")

    assert that(mock_object.foo).nth_call(1) == ("world",)


def test_assert_mock_was_called():
    mock_object: MyClass = mock(MyClass)
    mock_object.foo("hi")
    assert that(mock_object.foo).was_called


def test_assert_mock_not_called():
    mock_object: MyClass = mock(MyClass)
    assert that(mock_object.foo).was_not_called


def test_stub_return_value():
    mock_object: MyClass = mock(MyClass)

    when(mock_object.foo).any_call().then_return(123456)

    assert mock_object.foo("hello") == 123456


def test_stub_return_none():
    mock_object: MyClass = mock(MyClass)

    when(mock_object.quux).any_call().then_return(None)

    assert mock_object.quux() is None


def test_uncalled_any_call_stub_does_not_increment_call_count():
    mock_object: MyClass = mock(MyClass)

    when(mock_object.foo).any_call().then_return(123)

    assert that(mock_object.foo).num_calls == 0


def test_stub_return_when_args_passed():
    mock_object: MyClass = mock(MyClass)

    when(mock_object.foo).called_with(mock_object.foo("hi", baz=3)).then_return(678)

    assert mock_object.foo("hi", baz=3) == 678

    assert mock_object.foo("hi") == 0
    assert mock_object.foo("hi", baz=1) == 0
    assert mock_object.foo("hello") == 0


def test_stub_return_when_kwargs_passed():
    mock_object: MyClass = mock(MyClass)

    when(mock_object.foo).called_with(mock_object.foo(bar="hi", baz=3)).then_return(678)

    assert mock_object.foo(bar="hi", baz=3) == 678

    assert mock_object.foo("hi") == 0
    assert mock_object.foo("hello") == 0
    assert mock_object.foo("hi", baz=1) == 0
    assert mock_object.foo("hi", baz=3) == 0


def test_uncalled_called_with_stub_does_not_increment_call_count():
    mock_object: MyClass = mock(MyClass)

    when(mock_object.foo).called_with(mock_object.foo("bar")).then_return(123)

    assert that(mock_object.foo).num_calls == 0


def test_stub_consecutive_calls():
    mock_object: MyClass = mock(MyClass)
    when(mock_object.foo).any_call().then_return(123, 456, 789)

    assert mock_object.foo("a") == 123
    assert mock_object.foo("b") == 456
    assert mock_object.foo("c") == 789
    assert mock_object.foo("d") == 789


def test_stub_raises_error():
    mock_object: MyClass = mock(MyClass)

    when(mock_object.foo).any_call().then_raise(ValueError("Invalid argument"))

    with pytest.raises(ValueError):
        mock_object.foo("hello")


def test_stub_custom_result():
    mock_object: MyClass = mock(MyClass)

    when(mock_object.foo).any_call().then(lambda bar, baz=10: len(bar) + baz)

    assert mock_object.foo("hi") == 12
    assert mock_object.foo("hello") == 15
    assert mock_object.foo("hello", baz=10) == 15
    assert mock_object.foo("hello", baz=15) == 20


def test_stub_call_matching():
    mock_object: MyClass = mock(MyClass)

    when(mock_object.foo).call_matching(lambda bar, baz=1: baz % 2 == 0).then_return(5)

    assert mock_object.foo("a", 0) == 5
    assert mock_object.foo("b", 1) == 0
    assert mock_object.foo("c", 2) == 5
    assert mock_object.foo("d", 3) == 0


@pytest.mark.xfail(strict=True, reason="Not yet implemented")
def test_stub_call_with_raises_error():
    assert False


@pytest.mark.xfail(strict=True, reason="Not yet implemented")
def test_stub_called_with_args_and_custom_result():
    assert False


@pytest.mark.xfail(strict=True, reason="Not yet implemented")
def test_stub_consecutive_calls_with_error():
    assert False


@pytest.mark.xfail(strict=True, reason="Not yet implemented")
def test_stub_return_when_arg_matches():
    assert False
