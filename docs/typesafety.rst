Type Safety
===========

Normally (most of) these issues would be caught by static type checkers
such as mypy, but for the sake of demonstration this shows the runtime
checks that are built in to MockSafe.

.. doctest::

    >>> from mocksafe import mock, when, that

    >>> class FishSlapper:
    ...     def slap_fish(self, fish: str) -> str:
    ...         return f"{self.name} slaps {fish}"

    >>> fish_slapper = mock(FishSlapper)

    >>> # Try calling the mocked method with the wrong type
    >>> fish_slapper.slap_fish(42)
    Traceback (most recent call last):
    ...
    TypeError: Invalid type passed to mocked method slap_fish() for parameter: 'fish: str'. Actual argument passed was: 42 (<class 'int'>).

    >>> # Or stubbing a method that doesn't exist
    >>> when(fish_slapper.fish_slap)
    Traceback (most recent call last):
    ...
    AttributeError: type object 'FishSlapper' has no attribute 'fish_slap'

    >>> # Or stubbing the method with a different arg type
    >>> when(fish_slapper.slap_fish).called_with(fish_slapper.slap_fish(42))
    Traceback (most recent call last):
    ...
    TypeError: Invalid type passed to mocked method slap_fish() for parameter: 'fish: str'. Actual argument passed was: 42 (<class 'int'>).

    >>> # Or a different return type
    >>> when(fish_slapper.slap_fish).any_call().then_return(None)
    Traceback (most recent call last):
    ...
    TypeError: blah blah
