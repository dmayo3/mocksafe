Welcome to MockSafe
===================

This is a new Python mocking library that offers greater type safety,
to help keep your mocks in sync with your production code.


Why Use MockSafe?
-----------------

1. **Type Safety:** it's designed to help you keep your mocks in sync
with your production code by ensuring type safety for both static type
checkers, as well as some built-in runtime checks. For more information
see: :doc:`typesafety`.

2. **Fluent API:** designed to make your mocking code easy to read,
write, and understand with BDD inspired method naming.

3. **Simple:** the API is intended to be relatively small, simple, and
easy to use.

4. **Just Assert**: there is no need to use awkward assertions methods
such as `assert_was_called_with()`. Just use Python's native `assert`
keyword.

5. **Less Magic**: you won't get unexpected, unpredictable behavior
caused by the kind of mocking you get by default with
:py:mod:`unittest.mock`. It's even safer than using
:py:class:`unittest.mock.NonCallableMock` with the `spec_set`
parameter, which is the strictest mode that module provides.

6. **No Dependencies**: MockSafe is currently free of dependencies.
If we decide to add any in future we'll try to keep it minimal if possible.


Installation
------------

::

   pip install mocksafe


Getting Started
---------------

For an example of the basics see the :doc:`usage` page.


Contents
--------

.. toctree::

   usage
   mocking
   stubbing
   verification
   typesafety
   plugin
   api
