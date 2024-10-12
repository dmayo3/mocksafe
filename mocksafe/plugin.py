"""
This module provides an optional pytest plugin for mocksafe for
monkeypatching.

It is only available when the minimum required version of pytest
is installed, which should be >= 6.2.0.

When installed the plugin exposes a `patch` fixture that implements
the `Patcher` Protocol defined in this module.
"""
import logging
from typing import Protocol, TypeVar
from mocksafe import mock

try:
    import pytest

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
            """
            Patch an attribute on an object with a mock object.

            Args:
                obj: The object to patch.
                attr: The attribute to patch.
                class_type: The type of the class to mock.

            Returns:
                The mock object patched on to `obj`.
            """
            ...  # pylint: disable=unnecessary-ellipsis

    @pytest.fixture
    def patch(monkeypatch: pytest.MonkeyPatch) -> Patcher:
        return _Patcher(monkeypatch).patch

except (ImportError, AttributeError):
    logging.getLogger(__name__).debug(
        "pytest not importable so not installing mocksafe pytest plugin"
    )
