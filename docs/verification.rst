Mocked Call Verification
========================


Verify Last Call
----------------

The general form is::

    assert that(<mock>).last_call == (<args-tuple>)


Or if it was called with keyword arguments::

    assert that(<mock>).last_call == ((<args-tuple>), {<keyword-args>})


.. doctest::

   >>> class GrailSeeker:
   ...     def travel_to(self, place: str, when: str = "Someday"):
   ...         pass

   >>> arthur = mock(GrailSeeker)

   >>> arthur.travel_to("Camelot")

   >>> assert that(arthur.travel_to).last_call == ("Camelot",)

   >>> arthur.travel_to("Camelot", when="Now")

   >>> assert that(arthur.travel_to).last_call == (("Camelot",), {"when": "Now"})


Verify Nth Call
---------------

The general form is similar to checking for the last call::

    assert that(<mock>).nth_call(<N>) == (<args-tuple>)

Where `<N>` is a number from zero up to the number of calls made, exclusive.


Verify Number of Calls
----------------------

The general form is similar to checking for the last call::

    assert that(<mock>).num_calls ...


For example:

.. doctest::

    >>> assert that(arthur.travel_to).num_calls >= 1


Verify Mock Was/Not Called
--------------------------

The general form is similar to checking for the last call::

    assert that(<mock>).<was_called|was_not_called>


For example:

.. doctest::

    >>> assert that(arthur.travel_to).was_called

    >>> assert that(arthur.travel_to).was_not_called
    Traceback (most recent call last):
    ...
    AssertionError


Capture Call Details
--------------------

Sometimes it's useful to make more targetted or repeated
assertions about a subset of what a mocked method was called
with.

To make this easier you can retrieve call details and assign
them to a variable.

To capture the details of calls that were made you can use
expressions such as::

    <var> = spy(<mock>).last_call
    <var> = spy(<mock>).nth_call(<N>)
    etc.


.. note::

    The ``spy()`` function is just a synonym for ``that()``.


Example:

.. doctest::

    >>> class SpanishInquisition:
    ...     def surprise(self, location: str, interrogator: str) -> str:
    ...         raise NotImplementedError()

    >>> inquisitors = mock(SpanishInquisition)

    >>> when(inquisitors.surprise).any_call().then(
    ...     lambda location, interrogator: (
    ...         f"The Spanish Inquisition surprises {location} with {interrogator}!"
    ...     )
    ... )

    >>> inquisitors.surprise("the village", interrogator="Cardinal Biggles")
    'The Spanish Inquisition surprises the village with Cardinal Biggles!'

    >>> args, kwargs = spy(inquisitors.surprise).last_call

    >>> args
    ('the village',)
    >>> assert args[0] == "the village"

    >>> kwargs
    {'interrogator': 'Cardinal Biggles'}
    >>> assert kwargs.get("interrogator") == "Cardinal Biggles"


Capture Details for All Calls
-----------------------------

If you prefer to capture the details of all calls that were made for deeper
inspection you can use the ``all_calls`` attribute of the spy object using
expressions such as::

    <var> = spy(<mock>).all_calls

Example:

.. doctest::

    >>> class SpanishInquisition:
    ...     def surprise(self, location: str, interrogator: str) -> str:
    ...         raise NotImplementedError()

    >>> inquisitors = mock(SpanishInquisition)

    >>> when(inquisitors.surprise).any_call().then(
    ...     lambda location, interrogator: (
    ...         f"The Spanish Inquisition surprises {location} with {interrogator}!"
    ...     )
    ... )

    >>> inquisitors.surprise("the village", interrogator="Cardinal Biggles")
    'The Spanish Inquisition surprises the village with Cardinal Biggles!'

    >>> inquisitors.surprise("the castle", interrogator="Cardinal Fang")
    'The Spanish Inquisition surprises the castle with Cardinal Fang!'

    >>> inquisitors.surprise("the town square", interrogator="Cardinal Ximinez")
    'The Spanish Inquisition surprises the town square with Cardinal Ximinez!'

    >>> all_calls = spy(inquisitors.surprise).all_calls

    >>> locations = [call.args[0] for call in all_calls]
    >>> interrogators = [call.kwargs.get("interrogator") for call in all_calls]

    >>> assert locations == ["the village", "the castle", "the town square"]
    >>> assert interrogators == ["Cardinal Biggles", "Cardinal Fang", "Cardinal Ximinez"]
