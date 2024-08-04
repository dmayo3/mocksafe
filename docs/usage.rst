Usage
=====

Here's a basic example aided by the famous comedy troupe:
Mock Python's Flying Circus.

This example involves creating a mock object from a class,
stubbing a method result in response to a specific argument,
then check the result and assert the mocked method was called.

.. doctest::

    >>> from mocksafe import mock, when, that

    >>> class Lumberjack:
    ...     def chop(self, tree: str):
    ...        pass

    >>> mock_lumberjack: Lumberjack = mock(Lumberjack)
    >>> mock_lumberjack
    SafeMock(<class 'Lumberjack'>)

    >>> # Stub the chop method
    >>> when(
    ...     mock_lumberjack.chop
    ... ).called_with(
    ...     mock_lumberjack.chop("oak")
    ... ).then_return(
    ...     "I'm a lumberjack and I'm okay!"
    ... )

    >>> mock_lumberjack.chop("oak")
    "I'm a lumberjack and I'm okay!"

    >>> assert that(mock_lumberjack.chop).was_called


What's Next
-----------

You can learn more about stubbing results on the :doc:`stubbing` page.

To find more about verifying calls to mock objects you can go to the
:doc:`verification` page.

To learn about MockSafe's type safety you can visit the
:doc:`typesafety` page.

For the full API reference, see :doc:`api`.
