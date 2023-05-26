from __future__ import annotations
import inspect
import pytest
from mocksafe.core.spy import MethodSpy


class TestClass:
    def foo(self: TestClass, bar: int, baz: str = "quux") -> int:
        return bar + len(baz)


INSTANCE = TestClass()
METHOD = INSTANCE.foo
NAME = METHOD.__name__
SIGNATURE = inspect.signature(INSTANCE.foo)


def test_spy_delegation():
    foo = MethodSpy(NAME, METHOD, SIGNATURE)
    assert foo(1, baz="a") == 2


def test_spy_calls():
    foo = MethodSpy(NAME, METHOD, SIGNATURE)

    assert not foo.calls

    foo(1, baz="a")

    assert foo.calls == [((1,), {"baz": "a"})]


def test_spy_nth_call():
    foo = MethodSpy(NAME, METHOD, SIGNATURE)

    with pytest.raises(ValueError):
        foo.nth_call(0)

    foo(2)

    assert foo.nth_call(0) == ((2,), {})

    with pytest.raises(ValueError):
        foo.nth_call(1)


def test_spy_pop_call():
    foo = MethodSpy(NAME, METHOD, SIGNATURE)

    foo(1, baz="a")

    assert foo.pop_call() == ((1,), {"baz": "a"})

    with pytest.raises(IndexError):
        foo.pop_call()


def test_spy_info():
    foo = MethodSpy(NAME, METHOD, SIGNATURE)

    foo(1)

    assert str(foo) == "MethodSpy[foo:1 call(s)]"
    assert foo.name == NAME
