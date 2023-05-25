from __future__ import annotations
import inspect
from typing import Optional, Any, cast
from mocksafe.mock import SafeMock
from mocksafe.spy import CallRecorder, Generic, TypeVar
from mocksafe.custom_types import MethodName, Call
from mocksafe.call_type_validator import type_match


T = TypeVar("T")


class PropertyStubber:
    """
    Used to set a MockProperty on an existing mock object.

    You can obtain an instance of this class using
    :func:`mocksafe.stub`.

    Typically you wouldn't instantiate or use this class
    directly.

    :Example:
        >>> from mocksafe import PropertyStubber, MockProperty, mock, stub

        >>> class Philosopher:
        ...     @property
        ...     def meaning_of_life(self) -> str:
        ...         return "TODO: discover the meaning of life"

        >>> philosopher = mock(Philosopher)

        >>> # Contrived example showing intermediate step:
        >>> property_stubber: PropertyStubber = stub(philosopher)

        >>> # Set property attribute with a MockProperty[str]
        >>> property_stubber.meaning_of_life = MockProperty("")

        >>> # More usual example:
        >>> stub(philosopher).meaning_of_life = MockProperty("")

    See also: :class:`mocksafe.MockProperty`
    """

    _mock_object: SafeMock

    def __init__(self: PropertyStubber, mock_object: SafeMock):
        """
        Typically you wouldn't instantiate or use this class
        directly, use :func:`mocksafe.stub` to obtain an instance of
        this class instead.
        """
        super().__setattr__("_mock_object", mock_object)

    def __setattr__(self: PropertyStubber, prop_name: str, value: MockProperty):
        """
        Magic method for setting :class:`mocksafe.MockProperty` objects
        as class attributes on the mocked object.

        :raise AttributeError: if the attribute being set doesn't exist on the
                               original object
        :raise TypeError: if the :class:`mocksafe.MockProperty` type doesn't
                          match the type returned by the real property
        """
        prop_attr = self._mock_object.get_original_attr(prop_name)
        try:
            if cast(property, prop_attr).fget is None:
                raise TypeError
        except (AttributeError, TypeError):
            raise TypeError(
                (
                    f"{self._mock_object}.{prop_name} attribute is not a getter "
                    f"property. Actual attribute: {prop_attr} ({type(prop_attr)})."
                ),
            ) from None

        sig = inspect.signature(prop_attr.fget)
        has_type = sig.return_annotation != inspect.Signature.empty

        if has_type and not type_match(value.return_value, sig.return_annotation):
            raise TypeError(
                (
                    f"{self._mock_object}.{prop_name} property has return type"
                    f" {sig.return_annotation}, therefore it can't be stubbed with"
                    f" {value}."
                ),
            )

        setattr(type(self._mock_object), prop_name, value)


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
