from __future__ import annotations
from typing import Optional, Any
from mocksafe.core.spy import CallRecorder, Generic, TypeVar
from mocksafe.core.custom_types import MethodName, Call


T = TypeVar("T")


class MockProperty(CallRecorder, Generic[T]):
    """
    A `Descriptor <https://docs.python.org/3/howto/descriptor.html>`_ used
    to mock a getter property on a mock object.

    It holds a single stubbed value.

    You can assert calls the same as a mocked method.

    See the :doc:`../mocking` page for more details and an
    example of how to mock, stub, and verify a property.

    Apart from creating and stubbing values, you wouldn't
    normally interact with this object directly.

    See also:

     - :func:`mocksafe.stub`
     - :func:`mocksafe.that`
     - :func:`mocksafe.spy`
     - :class:`mocksafe.PropertyStubber`
    """

    def __init__(self: MockProperty, return_value: T):
        """
        Set the initial property value to stub, of generic type T.

        The generic type must match the type returned from the
        property being mocked.
        """
        self._calls: list[Call] = []
        self._return_value: T = return_value

    def __repr__(self: MockProperty) -> str:
        if (val := self.return_value) == "":
            val = "''"

        return f"MockProperty[{val}:{self.value_type}]"

    @property
    def value_type(self: MockProperty) -> type[T]:
        return type(self._return_value)

    @property
    def return_value(self: MockProperty) -> T:
        """
        Property used to stub the result to return when this mocked
        property value is retrieved.

        :Example:
            >>> from mocksafe import MockProperty
            >>> mock_prop: MockProperty[str] = MockProperty("")

            >>> mock_prop.return_value = "foo"
            >>> mock_prop.return_value
            'foo'
        """
        return self._return_value

    @return_value.setter
    def return_value(self: MockProperty, value: T) -> None:
        if not isinstance(value, self.value_type):
            raise TypeError(
                f"Return value '{value}' is incompatible with the MockProperty type"
                f" {self.value_type}"
            )
        self._return_value = value

    @property
    def name(self: MockProperty) -> MethodName:
        return str(self)

    @property
    def calls(self: MockProperty) -> list[Call]:
        return self._calls

    def nth_call(self: MockProperty, n: int) -> Call:
        if not self.calls:
            raise ValueError(f"The mocked property {self.name} was not called.")

        try:
            return self.calls[n]
        except IndexError:
            raise ValueError(
                (
                    f"Mocked property {self.name}() was not called {n+1} time(s). "
                    f"The actual number of calls was {len(self.calls)}."
                ),
            ) from None

    def __get__(self: MockProperty, obj: Any, objtype: Optional[type] = None) -> T:
        self._calls.append(((), {}))
        return self._return_value
