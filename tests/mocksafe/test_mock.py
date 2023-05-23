from __future__ import annotations
from mocksafe.mock import SafeMock, MethodMock, mock_reset


class TestClass:
    def foo(self: TestClass):
        ...

    @property
    def bar(self: TestClass) -> int:
        return -1


def test_mock_reset():
    mock_object = SafeMock(TestClass)

    mock_object.foo()

    foo: MethodMock = mock_object.mocked_methods["foo"]

    assert len(foo.calls) == 1

    mock_reset(mock_object)

    assert len(foo.calls) == 0
