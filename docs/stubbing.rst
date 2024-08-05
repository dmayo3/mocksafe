Stubbing
========

Terminology
-----------

Test Stub
^^^^^^^^^

A test stub is a fake version of a class or module.

It provides predetermined responses or data to mimic the behavior of real dependencies in order to isolate the unit under test and focus on specific scenarios or interactions.

A Mock Object can be thought of as a combination of a Test Stub and a Test Spy.

Stubbing
^^^^^^^^

Stubbing is the process of creating and using test stubs in unit testing.

It involves replacing real objects or components with stubs that emulate their behavior in a controlled manner.

By stubbing dependencies you can define specific responses, return values, or exceptions that facilitate predictable and controlled testing of the unit being tested.


Stub Conditions
---------------

In MockSafe you can define the circumstances under which a stubbed
result are triggered. The different ways you can do this are defined
in the subsections below.


Unconditional Stubbing
^^^^^^^^^^^^^^^^^^^^^^

This is used when you don't care how a method or function is called
and you always want to return the same result every time.

The format for this is::

    when(<stub>).any_call().<do-something>


Here's an example:

.. doctest::

    >>> from mocksafe import mock, when, that

    >>> class Lumberjack:
    ...     def chop(self, tree: str) -> str:
    ...        return "TODO"

    >>> mock_lumberjack: Lumberjack = mock(Lumberjack)

    >>> when(mock_lumberjack.chop).any_call().then_return(
    ...     "I sleep all night, I work all day."
    ... )

    >>> mock_lumberjack.chop("Blue Spruce")
    'I sleep all night, I work all day.'

    >>> mock_lumberjack.chop("Norwegian Pine")
    'I sleep all night, I work all day.'


Rehearsed Stubbing
^^^^^^^^^^^^^^^^^^

This is when you want to only return a result if the Test Stub
is called in a particular way. You specify the condition for
when you want to trigger the response by *rehearsing* what the
real call would look like, in a manner that can be statically
type checked.

The format for this is::

    when(<stub>).called_with(<stub>(<args>)).<do-something>


Here's an example:

.. doctest::

    >>> when(
    ...     mock_lumberjack.chop
    ... ).called_with(
    ...     mock_lumberjack.chop("Oak")  # The rehearsal
    ... ).then_return(
    ...     "I'm a lumberjack and I'm okay!"
    ... )

    >>> mock_lumberjack.chop("Oak")
    "I'm a lumberjack and I'm okay!"

    >>> mock_lumberjack.chop("Cherry")
    'I sleep all night, I work all day.'


Precondition Stubbing
^^^^^^^^^^^^^^^^^^^^^

If rehearsed or unconditional stubbing is not sufficient for your needs
then you can use a predicate i.e. a lambda, function, or method to
match incoming arguments and return a boolean.


The format for this is::

    when(<stub>).call_matching(<predicate>).<do-something>


Here's an example:

.. doctest::

    >>> # Stub the chop method again but conditionally
    >>> when(
    ...     mock_lumberjack.chop
    ... ).call_matching(
    ...     lambda tree: "oak" in tree.lower()
    ... ).then_return(
    ...     "I'm a lumberjack and I'm okay!"
    ... )

    >>> mock_lumberjack.chop("White Oak")
    "I'm a lumberjack and I'm okay!"

    >>> mock_lumberjack.chop("Swamp Spanish Oak")
    "I'm a lumberjack and I'm okay!"

    >>> # Our stub doesn't speak Latin
    >>> mock_lumberjack.chop("Quercus gravesii")
    'I sleep all night, I work all day.'


Lambda functions can't be annotated with types, but you
can always use a function or method instead.


.. doctest::

    >>> def oak_tree(tree: str) -> bool:
    ...     return "oak" in tree.lower() or "quercus" in tree.lower()

    >>> # Stub the chop method again but conditionally
    >>> when(mock_lumberjack.chop).call_matching(oak_tree).then_return(
    ...    "I'm a lumberjack and I'm okay!"
    ... )

    >>> # Our stub now understands the Latin name as well
    >>> mock_lumberjack.chop("Quercus chapmanii")
    "I'm a lumberjack and I'm okay!"


Stub Outcomes
-------------

Below are the various results or side effects that a stub
can perform when called.

Default Stubs
^^^^^^^^^^^^^

By default a test stub will return some sort of result
even if no stub has been explicitly been defined.

If a sensible default cannot be determined, it will
return `None`.

This will happen if for example the stubbed function
doesn't have a type annotation declaring its result
type, or if it has a result type that MockSafe doesn't
know how to produce a default result for.

Here are the list of types and values that will be
automatically returned when annotated as the return type:

.. table:: Default Stubs
    :widths: auto

    ========  ========
    Type      Value
    ========  ========
    `str`     `""`
    `int`     `0`
    `bool`    `False`
    `float`   `0.0`
    `dict`    `{}`
    `list`    `[]`
    `tuple`   `()`
    `set`     `set()`
    ========  ========


For example:

.. doctest::

    >>> class GrailSeeker:
    ...     def found_holy_grail_yet() -> bool:
    ...         raise NotImplementedError()
    ...
    ...     def shrubberies_posessed() -> set:
    ...         raise NotImplementedError()

    >>> mock(GrailSeeker).found_holy_grail_yet()
    False

    >>> len(mock(GrailSeeker).shrubberies_posessed())
    0


Return One Result
^^^^^^^^^^^^^^^^^

This is the simplest example we've already seen.

It's general form is::

    when(<stub>).<condition>.then_return(<result-value>)

Consecutive Results
^^^^^^^^^^^^^^^^^^^

You can use the same method to return different results on
successive calls. Once each result is cycled through the
last result will be repeated for every call beyond that.

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


Stub Fields
^^^^^^^^^^^

Fields in this instance means attributes that hold values, but that are not methods or properties.

MockSafe only knows about fields if they have type annotations defined on the class (as in the example below).
More technically this means an annotation (type hint) declared on a class attribute that has no value.
For more information see the `definition in the Python Glossary <https://docs.python.org/3/glossary.html#term-variable-annotation>`_.

There is also support for the non-standard `__attrs__` property that the `requests` library uses to store its own list of fields since this is such a common use case.

You need to set the field before the property can be accessed, otherwise you will get an error.

Example:

.. doctest::

    >>> from mocksafe import mock

    >>> class HolyHandGrenade:
    ...     countdown: int

    >>> mock_hhg: HolyHandGrenade = mock(HolyHandGrenade)

    >>> mock_hhg.countdown
    Traceback (most recent call last):
    ...
    AttributeError: SafeMock[HolyHandGrenade#6].countdown field value not stubbed.

    >>> mock_hhg.countdown = 3
    >>> mock_hhg.countdown
    3


Stub Properties
^^^^^^^^^^^^^^^

See the :doc:`mocking` page for how to do this.


Raise Error
^^^^^^^^^^^

It's general form for this is::

    when(<stub>).<condition>.then_raise(<exception>)


.. doctest::

    >>> class SpanishInquisition:
    ...     def surprise(self) -> str:
    ...         return "Our chief weapons: fear, surprise, ruthless efficiency, ..."

    >>> mock_inquisition = mock(SpanishInquisition)

    >>> when(mock_inquisition.surprise).any_call().then_raise(
    ...     Exception("NOBODY expects the Spanish Inquisition!")
    ... )

    >>> mock_inquisition.surprise()
    Traceback (most recent call last):
    ...
    Exception: NOBODY expects the Spanish Inquisition!


Mixed Side Effects
^^^^^^^^^^^^^^^^^^

To return a mixture of results and exceptions over consecutive calls
the general form is::

    when(<stub>).<condition>.use_side_effects(<result-or-exception>[, ...])

.. doctest::

    >>> class CheeseShop:
    ...     def check_stock(self, cheese: str) -> bool:
    ...         return False

    >>> cheese_shop: CheeseShop = mock(CheeseShop)

    >>> when(cheese_shop.check_stock).any_call().use_side_effects(
    ...    False,
    ...    False,
    ...    ValueError("The cat's eaten it."),
    ...    ValueError("Normally, sir, yes, but today the van broke down."),
    ...    False,
    ... )

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


Custom Side Effect
^^^^^^^^^^^^^^^^^^

For complete flexibility you can use a function to return
the results you want, throw an exception, or perform any
other side effect you might want.

The general form::

    when(<stub>).<condition>.then(<function>)


.. doctest::

    >>> class CheeseShop:
    ...     def ask_for_cheese(self, cheese: str) -> str:
    ...         return "Sorry."

    >>> mock_shop: CheeseShop = mock(CheeseShop)

    >>> when(mock_shop.ask_for_cheese).any_call().then(
    ...    lambda cheese: f"I'm afraid we're fresh out of {cheese}, sir."
    ... )

    >>> mock_shop.ask_for_cheese("Red Leicester")
    "I'm afraid we're fresh out of Red Leicester, sir."

    >>> mock_shop.ask_for_cheese("Gruyère")
    "I'm afraid we're fresh out of Gruyère, sir."
