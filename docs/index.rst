Welcome to MockSafe
===================

This is a new Python mocking library that offers greater type safety,
to help keep your mocks in sync with your production code.


Why Use MockSafe?
-----------------

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

6. **No Dependencies**: MockSafe is currently free of dependencies other than pytest. If we decide to add any in future we'll try to keep it minimal if possible.


Installation
------------

::

   pip install mocksafe


Getting Started
---------------

For an example of the basics see the :doc:`usage` page.


Type Safety
-----------

To find out more about the main reason this library was
created, you can see the :doc:`typesafety` page.


Contents
--------

.. toctree::

   usage
   mocking
   stubbing
   verification
   typesafety
   api
