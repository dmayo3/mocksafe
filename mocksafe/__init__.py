"""
The base mocksafe module.

See:

 - :meth:`mocksafe.mock`
 - :meth:`mocksafe.mock_module`
 - :meth:`mocksafe.mock_reset`
 - :class:`mocksafe.MockProperty`
 - :meth:`mocksafe.when`
 - :meth:`mocksafe.stub`
 - :meth:`mocksafe.that`
 - :meth:`mocksafe.spy`
"""

from mocksafe.core import (
    MockProperty,
    mock,
    mock_module,
    mock_reset,
)
from mocksafe.apis.bdd import (
    WhenStubber,
    MatchCallStubber,
    LastCallStubber,
    PropertyStubber,
    MockCalls,
    when,
    stub,
    that,
    spy,
)

__version__ = "0.10.0-beta"

__all__ = [
    "MockProperty",
    "mock",
    "mock_module",
    "mock_reset",
    "when",
    "stub",
    "that",
    "spy",
]
