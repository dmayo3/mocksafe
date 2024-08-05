from __future__ import annotations
import inspect
from typing import Generic, Union, TypeVar, Any, cast
from collections.abc import Callable
from mocksafe.core.custom_types import CallMatcher
from mocksafe.core.mock_property import MockProperty
from mocksafe.core.mock import SafeMock, MethodMock, ResultsProvider
from mocksafe.core.call_type_validator import type_match
from mocksafe.core.call_matchers import AnyCallMatcher, CustomCallMatcher


T = TypeVar("T")
ANY_CALL: CallMatcher = AnyCallMatcher()


def when(mock_method: Callable[..., T]) -> WhenStubber[T]:
    """
    Stub a mocked method.

    :param mock_method: a method on a mock object that returns generic type T
    :rtype: WhenStubber[T]

    :Example:
        >>> when(mock_random.random)
        <mocksafe.apis.bdd.when_then.WhenStubber object at 0x...>

    :Example:
        >>> when(mock_random.random).any_call().then_return(0.31)
    """
    if not isinstance(mock_method, MethodMock):
        raise ValueError(
            f"Not a SafeMocked method: {mock_method} ({type(mock_method)})"
        )
    return WhenStubber(mock_method)


def stub(mock_object: Any) -> PropertyStubber:
    """
    Prepare to stub a property on ``mock_object``.

    See the :doc:`../mocking` page for more details and an
    example of how to mock, stub, and verify a property.

    See also: :class:`mocksafe.PropertyStubber`
    See also: :class:`mocksafe.MockProperty`
    """
    if not isinstance(mock_object, SafeMock):
        raise ValueError(f"Not a SafeMocked object: {mock_object}")
    return PropertyStubber(mock_object)


class WhenStubber(Generic[T]):
    """
    Set up conditions for when a stub is to be used.

    :Example:
        >>> when(mock_random.random).any_call().then_return(0.31)

    See: :class:`mocksafe.MatchCallStubber`

    :Example:
        >>> when(
        ...     mock_random.randint
        ... ).called_with(
        ...     mock_random.randint(1, 10)
        ... ).then_return(7)

        >>> mock_random.randint(1, 10)
        7

    See: :class:`mocksafe.LastCallStubber`

    :Example:
        >>> when(
        ...     mock_random.randint
        ... ).call_matching(
        ...     lambda a, b: a <= 3 and b > 3
        ... ).then_return(3)

        >>> mock_random.randint(2, 6)
        3

    See: :class:`mocksafe.MatchCallStubber`
    """

    def __init__(self: WhenStubber, method_mock: MethodMock[T]):
        self._method_mock = method_mock

    def any_call(self: WhenStubber) -> MatchCallStubber[T]:
        """
        Matches any calls made to the mocked method.

        :rtype: MatchCallStubber[T]
        """
        return MatchCallStubber(self._method_mock, matcher=ANY_CALL)

    def called_with(self: WhenStubber, _: T) -> LastCallStubber[T]:
        """
        Matches specific calls made to the mocked method.

        :rtype: LastCallStubber[T]
        """
        return LastCallStubber(self._method_mock)

    def call_matching(
        self: WhenStubber, call_lambda: Callable[..., bool]
    ) -> MatchCallStubber[T]:
        """
        Use a lambda to determine whether to match a call.

        :rtype: MatchCallStubber[T]
        """
        return MatchCallStubber(self._method_mock, CustomCallMatcher(call_lambda))


class MatchCallStubber(Generic[T]):
    """
    Set up results or side effects to be used when for the stub the
    condition matches.

    :Example:
        >>> when(mock_random.random).any_call().then_return(0.31)

    :Example:
        >>> when(mock_random.random).any_call().then_return(0.1, 0.3, 0.2)

    :Example:
        >>> when(mock_random.random).any_call().then_raise(ValueError("..."))

    :Example:
        >>> when(mock_random.randint).any_call().then(lambda a, b: int((b - a) / 2))

    :Example:
        >>> when(
        ...     mock_random.randint
        ... ).any_call().use_side_effects(
        ...     1, 2, 3, ValueError("..."), 4
        ... )

    """

    def __init__(
        self: MatchCallStubber, method_mock: MethodMock[T], matcher: CallMatcher
    ):
        self._method_mock = method_mock
        self._matcher = matcher

    def then_return(self: MatchCallStubber, result: T, *consecutive_results: T) -> None:
        """
        Set one or more results to be returned by the method stub.
        """
        self.use_side_effects(result, *consecutive_results)

    def then_raise(self: MatchCallStubber, error: BaseException) -> None:
        """
        Raise an exception.
        """
        self.use_side_effects(error)

    def then(self: MatchCallStubber, result: ResultsProvider) -> None:
        """
        Use a custom lambda to produce stubbed results.
        """
        self._method_mock.custom_result(self._matcher, result)

    def use_side_effects(
        self: MatchCallStubber, *side_effects: Union[T, BaseException]
    ) -> None:
        """
        Specify an ordered sequence of results and/or exceptions to be returned/raised.
        """
        self._method_mock.add_stub(self._matcher, list(side_effects))


class LastCallStubber(Generic[T]):
    """
    Set up results or side effects to be used when for the stub the
    condition matches.

    :Example:
        >>> when(
        ...     mock_random.randint
        ... ).called_with(
        ...     mock_random.randint(1, 2)
        ... ).then_return(0.31)

    :Example:
        >>> when(
        ...     mock_random.randint
        ... ).called_with(
        ...     mock_random.randint(3, 4)
        ... ).then_return(0.1, 0.3, 0.2)

    :Example:
        >>> when(
        ...     mock_random.randint
        ... ).called_with(
        ...     mock_random.randint(5, 6)
        ... ).then_raise(ValueError("..."))

    :Example:
        >>> when(
        ...     mock_random.randint
        ... ).called_with(
        ...     mock_random.randint(7, 8)
        ... ).then(
        ...     lambda a, b: int((b - a) / 2)
        ... )

    :Example:
        >>> when(
        ...     mock_random.randint
        ... ).called_with(
        ...     mock_random.randint(9, 10)
        ... ).use_side_effects(
        ...     1, 2, 3, ValueError("..."), 4
        ... )
    """

    def __init__(self: LastCallStubber, method_mock: MethodMock[T]):
        self._method_mock = method_mock

    def then_return(self: LastCallStubber, result: T, *consecutive_results: T) -> None:
        self.use_side_effects(result, *consecutive_results)

    def then_raise(self: LastCallStubber, error: BaseException) -> None:
        self.use_side_effects(error)

    def then(self: LastCallStubber, result: ResultsProvider) -> None:
        self._method_mock.custom_result_for_last_call(result)

    def use_side_effects(
        self: LastCallStubber, *side_effects: Union[T, BaseException]
    ) -> None:
        if not self._method_mock.calls:
            raise ValueError(
                (
                    "Mocked methods do not match: "
                    f"when({self._method_mock.full_name})"
                    ".called_with(<different_method>)"
                ),
            )

        self._method_mock.stub_last_call(list(side_effects))


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

        self._mock_object._properties[prop_name] = value
