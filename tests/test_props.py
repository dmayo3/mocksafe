from __future__ import annotations
import pytest
from mocksafe import MockProperty, mock, stub, that


class Philosopher:
    inner_meaning: str = "42"

    @property
    def meaning_of_life(self: Philosopher) -> str:
        return self.inner_meaning

    @meaning_of_life.setter
    def meaning_of_life(self: Philosopher, new_meaning: str) -> None:
        self.inner_meaning = new_meaning


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


def test_mock_setter_prop():
    mock_meaning: MockProperty[str] = MockProperty("")

    philosopher: Philosopher = mock(Philosopher)

    stub(philosopher).meaning_of_life = mock_meaning

    philosopher.meaning_of_life = (
        "Try and be nice to people, avoid eating fat, "
        "read a good book every now and then, get "
        "some walking in, and try and live together "
        "in peace and harmony with people of all "
        "creeds and nations."
    )

    assert "be nice" in philosopher.meaning_of_life
    assert "live together in peace" in philosopher.meaning_of_life

    assert that(mock_meaning).was_called
    assert that(mock_meaning).num_calls == 2
    assert that(mock_meaning).last_call == ()


def test_mocking_props_across_instances():
    plato: Philosopher = mock(Philosopher)
    meaning: MockProperty[str] = MockProperty("")
    meaning.return_value = "wisdom and virtue and all that stuff"
    stub(plato).meaning_of_life = meaning

    descartes: Philosopher = mock(Philosopher)
    contemplation: MockProperty[str] = MockProperty("")
    stub(descartes).meaning_of_life = contemplation
    contemplation.return_value = "I think, therefore I like spam"

    assert "wisdom" in plato.meaning_of_life
    assert "think" in descartes.meaning_of_life

    assert that(meaning).was_called
    assert that(meaning).num_calls == 1
    assert that(meaning).last_call == ()

    assert that(contemplation).was_called
    assert that(contemplation).num_calls == 1
    assert that(contemplation).last_call == ()
