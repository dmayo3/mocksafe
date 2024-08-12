from mocksafe.plugin import Patcher
from mocksafe import when


class TestClass:
    def method(self) -> str:
        return "original"


def test_plugin(patch: Patcher):
    instance = TestClass()
    mock_object = patch(instance, "method", TestClass)

    when(mock_object.method).any_call().then_return("mocked")

    assert mock_object.method() == "mocked", "Method was not mocked properly."
