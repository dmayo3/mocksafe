from typing import Protocol, TypeVar
import pytest
from mocksafe import mock


T = TypeVar("T")


class _Patcher:
    def __init__(self, monkeypatch: pytest.MonkeyPatch):
        self._monkeypatch = monkeypatch

    def patch(self, obj: object, attr: str, class_type: type[T]) -> T:
        mock_obj: T = mock(class_type)
        self._monkeypatch.setattr(obj, attr, mock_obj)
        return mock_obj


class Patcher(Protocol):
    def __call__(self, obj: object, attr: str, class_type: type[T]) -> T:
        ...


@pytest.fixture
def patch(monkeypatch: pytest.MonkeyPatch) -> Patcher:
    return _Patcher(monkeypatch).patch
