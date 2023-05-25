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
from mocksafe.mock import mock, mock_module, mock_reset
from mocksafe.when_then import when, stub
from mocksafe.that import that, spy

from mocksafe.when_then import WhenStubber, MatchCallStubber, LastCallStubber
from mocksafe.mock_property import MockProperty, PropertyStubber
from mocksafe.that import MockCalls


__version__ = "0.6.0-alpha"
