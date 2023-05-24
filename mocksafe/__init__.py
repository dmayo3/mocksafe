"""
The base mocksafe module.

See:

 - :meth:`mocksafe.mock`
 - :meth:`mocksafe.mock_module`
 - :meth:`mocksafe.mock_reset`
 - :meth:`mocksafe.when`
 - :meth:`mocksafe.that`
 - :meth:`mocksafe.spy`
"""
from mocksafe.mock import mock, mock_module, mock_reset
from mocksafe.when_then import when
from mocksafe.that import that, spy

from mocksafe.when_then import WhenStubber, MatchCallStubber, LastCallStubber
from mocksafe.that import MockCalls


__version__ = "0.5.0-alpha"
