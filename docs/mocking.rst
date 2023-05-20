Mocking
=======

Terminology
-----------

Mock Object
^^^^^^^^^^^

A mock object is a fake or double version of a real class or module that
implements the same type (interface/protocol/signature).

It can be used for :doc:`stubbing` results when its method calls.

Mock objects also *spy* on any calls they receive so that the unit
test can verify the mock was called in the expected way.
See :doc:`verification`.

.. note::

    Mock Object = Test Stub + Test Spy


Mocking Classes
---------------

This is the most straightforward case:

.. doctest::

    >>> from mocksafe import mock

    >>> class Lumberjack:
    ...     def chop(self, tree: str) -> str:
    ...        return "TODO"

    >>> mock_lumberjack: Lumberjack = mock(Lumberjack)

    >>> mock_lumberjack
    SafeMock[Lumberjack#...]


The generic mock function will return the same type of
object that you give it, allowing type safety to be
checked.

It does not directly allow you to stub results or
verify mocked calls, because that is incompatible
with the original type being mocked.

This is in contrast with :py:class:`unittest.mock.Mock`
as you **can't** do things like this::

    # ❌ This kind of thing is not valid!
    mock_lumberjack.chop.return_value = "I'm a lumberjack..."


Attempting to do something like this should generate a type
error.

Instead we pass the mock to functions that enable you to
perform :doc:`stubbing` or :doc:`verification`.

For example:

.. doctest::

    >>> from mocksafe import when
    >>> when(mock_lumberjack.chop).any_call().then_return("I'm a lumber...")


Mocking Modules
---------------

MockSafe is still under development and doesn't have first class
support for this yet, but it is still possible to do in a type
safe manner with a workaround.

In order to mock the module you need a class that mimics the
interface of the module that you wish to mock. You may need
to define this yourself in the test.

For convenience, here is an example of where a class already
exists corresponding to a module in the standard library:


.. doctest::

    >>> from random import Random
    >>> from mocksafe import mock, when

    >>> random: Random = mock(Random)

    >>> when(random.random).any_call().then_return(0.123)
    >>> random.random()
    0.123


It just happens that the :py:mod:`random` is implemented
by a hidden instance of the :py:class:`random.Random`.

This is often not the case however, so as mentioned above
you may need to create a class that mirrors the parts of the
module you need to mock.

For example:

.. doctest::

    >>> import gzip
    >>> from mocksafe import mock, when

    >>> class GZip:
    ...     def compress(self, data: bytes) -> bytes:
    ...         return gzip.compress(data)

    >>> mock_gzip: GZip = mock(GZip)

    >>> when(mock_gzip.compress).any_call().then_return(b"super compressed")

    >>> mock_gzip.compress(b"Lots of content here!")
    b'super compressed'


Mocking Functions
-----------------

This is another thing where first class support is not yet included.

To workaround this limitation you'll need to wrap the function in a
class for the time being, the same as the workaround above for
mocking modules.

.. doctest::

    >>> from math import factorial
    >>> from mocksafe import mock, when

    >>> class FactorialCalc:
    ...     def factorial(self, n: int) -> int:
    ...         return factorial(n)

    >>> mock_calc: FactorialCalc = mock(FactorialCalc)
    >>> mock_factorial = mock_calc.factorial

    >>> when(mock_factorial).called_with(mock_factorial(3)).then_return(6)

    >>> mock_factorial(3)
    6
