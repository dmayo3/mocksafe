from __future__ import annotations
import inspect
from typing import Optional, Any, cast
from mocksafe.mock import SafeMock
from mocksafe.spy import CallRecorder, Generic, TypeVar
from mocksafe.custom_types import MethodName, Call
from mocksafe.call_type_validator import type_match


T = TypeVar("T")


class PropertyStubber:
    _mock_object: SafeMock

    def __init__(self: PropertyStubber, mock_object: SafeMock):
        super().__setattr__("_mock_object", mock_object)

    def __setattr__(self: PropertyStubber, prop_name: str, value: MockProperty):
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
    def __init__(self: MockProperty, return_value: T):
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
        return "meaning_of_life"

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
