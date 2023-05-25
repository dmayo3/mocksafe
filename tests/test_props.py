from __future__ import annotations
import pytest
from mocksafe import MockProperty, mock, stub, that


class Philosopher:
    @property
    def meaning_of_life(self: Philosopher) -> str:
        return "42"


def test_mock_getter_prop():
    mock_meaning: MockProperty[str] = MockProperty("")

    philosopher: Philosopher = mock(Philosopher)

    stub(philosopher).meaning_of_life = mock_meaning

    with pytest.raises(TypeError):
        stub(philosopher).meaning_of_life = MockProperty(123)

    with pytest.raises(AttributeError):
        stub(philosopher).foobar = mock_meaning

    assert philosopher.meaning_of_life == ""

    mock_meaning.return_value = (
        "Try and be nice to people, avoid eating fat, "
        "read a good book every now and then, get "
        "some walking in, and try and live together "
        "in peace and harmony with people of all "
        "creeds and nations."
    )

    assert "be nice" in philosopher.meaning_of_life
    assert "live together in peace" in philosopher.meaning_of_life

    assert that(mock_meaning).was_called
    assert that(mock_meaning).num_calls == 3
    assert that(mock_meaning).last_call == ()
