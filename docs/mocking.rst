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
    SafeMock(<class 'Lumberjack'>)


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

To mock a module you need to use a separate function, but otherwise
everything else is the same as for mocking a regular class / type.

One difference is that you can't use a module as a type hint in
Python, meaning you won't get static type checks. The calls are
still checked by MockSafe at runtime however.

However, it's possible to use :py:func:`unittest.mock.patch`
to swap real module calls for mocked module calls during test
runtime, and the static type checker should be able to verify
calls the same as usual.

Example:

.. doctest::

    >>> import gzip
    >>> from mocksafe import mock_module, when

    >>> mock_gzip = mock_module(gzip)

    >>> when(mock_gzip.compress).any_call().then_return(b"super compressed")

    >>> mock_gzip.compress(b"Lots of content here!")
    b'super compressed'

    # ❌ gzip.squash() does not exist
    >>> mock_gzip.squash(b"This is an invalid call")
    Traceback (most recent call last):
    ...
    AttributeError: type object <module 'gzip'> has no attribute 'squash'


Mocking Properties
------------------

Mocking properties is a bit more challenging in Python and so it's not as convenient to mock them in MockSafe compared to methods.

Example:

.. doctest::

    >>> from mocksafe import MockProperty, mock, stub, that

    >>> class Philosopher:
    ...     @property
    ...     def meaning_of_life(self) -> str:
    ...         return "TODO: discover the meaning of life"

    >>> # Define a MockProperty that holds a str value
    >>> # and set it's initial value to ""
    >>> mock_meaning: MockProperty[str] = MockProperty("")

    >>> philosopher: Philosopher = mock(Philosopher)

    >>> # Mock the meaning_of_life property
    >>> stub(philosopher).meaning_of_life = mock_meaning

    >>> philosopher.meaning_of_life
    ''

    >>> mock_meaning.return_value = "42"

    >>> philosopher.meaning_of_life
    '42'

    >>> assert that(mock_meaning).was_called
    >>> assert that(mock_meaning).num_calls == 2
    >>> assert that(mock_meaning).last_call == ()


For more information see :class:`mocksafe.MockProperty` and
:meth:`mocksafe.stub`.


Mocking Functions
-----------------

This is another thing where first class support is not yet included.

To workaround this limitation you'll need to wrap the function in a
class or module for the time being, the same as the workaround above for
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


You can also create an ad hoc type as a mockable specification:

.. doctest::

    >>> from math import factorial
    >>> from mocksafe import mock, when

    >>> def factorial(n: int) -> int:
    ...     return factorial(n)

    >>> fcalc = type('FactorialCalculator', (), {"factorial": factorial})

    >>> mock_factorial = mock(fcalc).factorial

    >>> when(mock_factorial).called_with(mock_factorial(3)).then_return(6)

    >>> mock_factorial(3)
    6


Mocking Callable Objects
------------------------

Callable objects are similar to functions.

Here is how to mock a Callable object:

.. doctest::

        >>> from collections.abc import Callable
        >>> from mocksafe import mock, when

        >>> # Here we define the (upper) class TwitOfTheYear to be mocked...
        ... class TwitOfTheYear:
        ...     def __call__(self, name: str) -> str:
        ...         return f"{name} is the Upper Class Twit of the Year!"

        >>> mock_twit: Callable[[str], str] = mock(TwitOfTheYear)
        >>> (
        ...     when(mock_twit)
        ...         .called_with(mock_twit("Gervaise Brook-Hampster"))
        ...         .then_return("Gervaise Brook-Hampster is the Upper Class Twit of the Year!")
        ... )

        >>> mock_twit("Gervaise Brook-Hampster")
        'Gervaise Brook-Hampster is the Upper Class Twit of the Year!'
