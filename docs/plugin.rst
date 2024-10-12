Pytest Plugin (optional)
========================

This plugin provides a Pytest fixture that can be used to monkeypatch
attributes on objects with mocks.

This is a convenience that builds on top of pytest's `monkeypatch`
(`pytest.MonkeyPatch`) fixture.

To use this plugin, a compatible version of pytest (>=6.2) must be installed.

Here's an example of using the patch fixture to mock out the default
Random number generator in the `random` module:

.. doctest::

    >>> import pytest
    >>> import random
    >>> from mocksafe.plugin import Patcher

    >>> @pytest.fixture
    ... def mock_random(patch: Patcher) -> random.Random:
    ...     return patch(random, "_inst", random.Random)

For more information see: :mod:`mocksafe.plugin`
