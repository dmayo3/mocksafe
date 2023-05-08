Welcome to MockSafe
===================

This is a new Python mocking library that offers greater type safety,
to help keep your mocks in sync with your production code.


Why Choose MockSafe?
--------------------

1. **Type Safety:** it's designed to help you keep your mocks in sync
with your production code by ensuring type safety for both static type
checkers, as well as some built-in runtime checks. Just make sure you
add type hints to the code that you're mocking.

2. **Fluent API:** designed to make your mocking code easy to read,
write, and understand with BDD inspired method naming.

3. **Simple:** the API is intended to be relatively small, simple, and
easy to use.

4. **Just Assert**: there is no need to use awkward assertions methods
such as `assert_was_called_with()`. Just use Python's native `assert`
keyword.

5. **Less Magic**: you won't get unexpected, unpredictable behavior
caused by the kind of mocking you get with ``unittest.mock``.
Only the methods on the class you're mocking will be stubbed, and by
default these stubbed methods will return predictable defaults (such as 0,
False, or None).

6. **Python 3.10+**: MockSafe is free from any legacy constraints and uses
up-to-date Python typing and features.


MockSafe in Action
------------------

Let's summon a simple example to see MockSafe in action:


.. doctest::

   >>> from mocksafe import mock, when, that

   >>> class GrailSeeker:
   ...     def find_holy_grail(self) -> str:
   ...         # TODO: write production code here
   ...         raise NotImplementedError()

   >>> arthur = mock(GrailSeeker, name="King Arthur")

   >>> when(arthur.find_holy_grail).any_call().then_return("Ni!")

   >>> arthur.find_holy_grail()
   'Ni!'

   >>> assert that(arthur.find_holy_grail).was_called
   >>> assert that(arthur.find_holy_grail).num_calls == 1
   >>> assert that(arthur.find_holy_grail).last_call == ()


This is just a taste, there are plenty more Monty Python inspired
examples in the Usage section.


Contents
--------

.. toctree::

   usage
   api
