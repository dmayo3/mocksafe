Usage
=====

Here are a few examples aided by the famous comedy troupe:
Mock Python's Flying Circus.


Example 1: basic stubbing & assertions
--------------------------------------

Here we demonstrate creating a mock object from a class,
stubbing a method result in response to a specific argument,
then check the result and assert the mocked method was called.

.. doctest::

    >>> from mocksafe import mock, when, that

    >>> class Lumberjack:
    ...     def chop(self, tree: str):
    ...        return "I'm a lumberjack and I'm OK. I sleep all night, I work all day."

    >>> mock_lumberjack: Lumberjack = mock(Lumberjack)
    >>> mock_lumberjack
    SafeMock[Lumberjack#...]

    >>> # Stub the chop method
    >>> when(mock_lumberjack.chop)\
    ...     .called_with(mock_lumberjack.chop("oak"))\
    ...     .then_return("I'm a lumberjack and I'm okay!")

    >>> mock_lumberjack.chop("oak")
    "I'm a lumberjack and I'm okay!"

    >>> assert that(mock_lumberjack.chop).was_called


Example 2: stubbing exceptions
------------------------------

Nobody expects the exception here!

.. doctest::

    >>> class SpanishInquisition:
    ...     def surprise(self) -> str:
    ...         return "Our chief weapons: fear, surprise, ruthless efficiency, ..."

    >>> mock_inquisition = mock(SpanishInquisition)

    >>> when(mock_inquisition.surprise)\
    ...     .any_call()\
    ...     .then_raise(Exception("NOBODY expects the Spanish Inquisition!"))

    >>> mock_inquisition.surprise()
    Traceback (most recent call last):
    ...
    Exception: NOBODY expects the Spanish Inquisition!


Example 3: more stubbing and assertions
---------------------------------------

Here we stub multiple different results and make more assertions
about the number of calls made.


.. doctest::

    >>> class SillyWalker:
    ...     def walk(self, leg_movement: str = "walk"): ...
    ...
    ...     def run(self): ...

    >>> mock_walker = mock(SillyWalker)

    >>> when(mock_walker.walk).any_call().then_return("Silly walk!")
    >>> when(mock_walker.walk).called_with(mock_walker.walk("skip")).then_return("Skip, skip, skip!")
    >>> when(mock_walker.walk).called_with(mock_walker.walk("hop")).then_return("Hop, hop, hop!")

    >>> mock_walker.walk()
    'Silly walk!'
    >>> mock_walker.walk("skip")
    'Skip, skip, skip!'
    >>> mock_walker.walk("hop")
    'Hop, hop, hop!'

    >>> assert that(mock_walker.walk).was_called
    >>> assert that(mock_walker.walk).num_calls == 3

    >>> assert that(mock_walker.run).was_not_called


Example 4: mock type safety
---------------------------

Normally (most of) these issues would be caught by static type checkers,
but for the purpose of this example we'll demonstrate what the runtime
errors would look like.

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


Example 5: multiple results
---------------------------

.. doctest::

    >>> class Waitress:
    ...     def get_next_menu_item(self) -> str:
    ...         return "Spam"

    >>> mock_waitress: Waitress = mock(Waitress)

    >>> when(mock_waitress.get_next_menu_item).any_call().then_return(
    ...     "Eggs and spam",
    ...     "Spam, bacon, sausage, and spam",
    ...     "Spam, egg, spam, spam, bacon, and spam",
    ...     "Spam, spam, spam, egg, and spam",
    ... )

    >>> mock_waitress.get_next_menu_item()
    'Eggs and spam'

    >>> mock_waitress.get_next_menu_item()
    'Spam, bacon, sausage, and spam'


Example 6: asserting multiple calls
-----------------------------------

.. doctest::

    >>> from typing import Optional

    >>> class PetShop:
    ...     def sell_pet(self, pet: str, price: int, status: Optional[dict[str, ...]] = None) -> None:
    ...         ...

    >>> parrot_shop: PetShop = mock(PetShop)
    >>> parrot_shop.sell_pet("Norwegian Blue", 50, status={"dead": True})
    >>> parrot_shop.sell_pet("Norwegian Blue", 100)
    >>> parrot_shop.sell_pet("Norwegian Blue", 150)

    >>> assert that(parrot_shop.sell_pet).last_call == ("Norwegian Blue", 150)

    >>> assert that(parrot_shop.sell_pet).nth_call(1) == ("Norwegian Blue", 100)

    >>> spy(parrot_shop.sell_pet).nth_call(0)
    (('Norwegian Blue', 50), {'status': {'dead': True}})

    >>> assert that(parrot_shop.sell_pet).nth_call(0) == (("Norwegian Blue", 50), {'status': {"dead": True}})


Example 7: multiple side effects
--------------------------------

To return a mixture of results and exceptions over consecutive calls:

.. doctest::

    >>> class CheeseShop:
    ...     def check_stock(self, cheese: str) -> bool:
    ...         return False

    >>> cheese_shop: CheeseShop = mock(CheeseShop)

    >>> when(cheese_shop.check_stock)\
    ...    .any_call()\
    ...    .use_side_effects(
    ...        False,
    ...        False,
    ...        ValueError("The cat's eaten it."),
    ...        ValueError("Normally, sir, yes, but today the van broke down."),
    ...        False,
    ...    )

    >>> cheese_shop.check_stock("Stilton")
    False

    >>> cheese_shop.check_stock("Norwegian Jarlsberg")
    False

    >>> cheese_shop.check_stock("Camembert")
    Traceback (most recent call last):
    ...
    ValueError: The cat's eaten it.

    >>> cheese_shop.check_stock("Venezuelan beaver cheese")
    Traceback (most recent call last):
    ...
    ValueError: Normally, sir, yes, but today the van broke down.

    >>> cheese_shop.check_stock("Gorgonzola")
    False

    >>> cheese_shop.check_stock("Any cheese at all")
    False


Example 8: custom result lambda
-------------------------------

To implement a custom result with a lambda function:

.. doctest::

    >>> class UpperClassTwit:
    ...     def perform_stunt(self, stunt_name: str) -> str:
    ...         raise NotImplementedError()
 
    >>> vivian = mock(UpperClassTwit, name="Vivian Smith-Smythe-Smith")
    >>> vivian
    SafeMock[UpperClassTwit#Vivian Smith-Smythe-Smith]

    >>> simon = mock(UpperClassTwit, "Simon Zinc-Trumpet-Harris")
    >>> simon
    SafeMock[UpperClassTwit#Simon ...]

    >>> mock_commentary = lambda stunt_name: f"{stunt_name.upper()}? Oh, how droll!"

    >>> when(vivian.perform_stunt).any_call().then(mock_commentary)
    >>> when(simon.perform_stunt).any_call().then(mock_commentary)

    >>> simon.perform_stunt("Walking into a Tree")
    'WALKING INTO A TREE? Oh, how droll!'

    >>> vivian.perform_stunt("Waking The Neighbour")
    'WAKING THE NEIGHBOUR? Oh, how droll!'


Example 9: capture call details
-------------------------------

To capture the details of a particular call:

.. doctest::

    >>> class SpanishInquisition:
    ...     def surprise(self, location: str, interrogator: str) -> str:
    ...         return f"The Spanish Inquisition surprises {location} with {interrogator}!"

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


.. note::

    The ``spy()`` function is just a synonym for ``that()``.
