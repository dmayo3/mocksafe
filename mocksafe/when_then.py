from __future__ import annotations
from typing import Generic, Union, TypeVar
from collections.abc import Callable
from mocksafe.custom_types import CallMatcher
from mocksafe.mock import MethodMock, ResultsProvider
from mocksafe.call_matchers import AnyCallMatcher, CustomCallMatcher


T = TypeVar("T")
ANY_CALL: CallMatcher = AnyCallMatcher()


def when(mock_method: Callable[..., T]) -> WhenStubber[T]:
    """
    Stub a mocked method.

    :param mock_method: a method on a mock object that returns generic type T
    :rtype: WhenStubber[T]

    :Example:
        >>> when(mock_random.random)
        <mocksafe.when_then.WhenStubber object at 0x...>

    :Example:
        >>> when(mock_random.random).any_call().then_return(0.31)
    """
    if not isinstance(mock_method, MethodMock):
        raise ValueError(
            f"Not a SafeMocked method: {mock_method} ({type(mock_method)})"
        )
    return WhenStubber(mock_method)


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
