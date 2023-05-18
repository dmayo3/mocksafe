from __future__ import annotations
from typing import Union
from collections.abc import Callable
from mocksafe.custom_types import Call
from mocksafe.mock import MethodMock


Args = tuple


def that(mock_method: Callable) -> MockCalls:
    """
    Used to assert how a mocked method was called.

    :param mock_method: a method on a mock object
    :rtype: MockCalls

    :Example:
        >>> assert that(mock_random.random).was_not_called

    :Example:
        >>> that(mock_random.random)
        MockCalls[random();num_calls=0]
    """
    if not isinstance(mock_method, MethodMock):
        raise ValueError("Not a SafeMocked method: mock_method")
    return MockCalls(mock_method)


def spy(mock_method: Callable) -> MockCalls:
    """
    This is used to capture the arguments that were
    passed when the given ``mock_method`` was called,
    which is useful for making more detailed assertions
    on the contents.

    The ``spy()`` function is actually an alias for ``that()``.

    Both are just syntactic sugar to make your code flow more
    fluently, for example ``assert that(mock.foo).was_called``
    versus ``args = spy(mock.foo).last_call``.

    :param mock_method: a method on a mock object
    :rtype: MockCalls

    :Example:
        >>> spy(mock_random.random)
        MockCalls[random();num_calls=0]

    :Example:
        >>> spy(mock_random.random).was_not_called
        True

    :Example:
        >>> when(mock_random.random).any_call().then_return(0.123)
        >>> mock_random.random()
        0.123
        >>> spy(mock_random.random).last_call
        ()

    :Example:
        >>> when(mock_random.randint).any_call().then_return(5)
        >>> mock_random.randint(0, 10)
        5
        >>> spy(mock_random.randint).last_call
        (0, 10)
    """
    return that(mock_method)


class MockCalls:
    """
    Provides information about calls made to a mocked method.

    This object returned by both :meth:`mocksafe.that` and :meth:`mocksafe.spy`.

    There's no need to instantiate this class directly, just
    use those methods instead.

    :Example:
        >>> assert that(mock_random.random).was_not_called

    :Example:
        >>> spy(mock_random.random).was_not_called
        True
        >>> spy(mock_random.random).was_called
        False
        >>> spy(mock_random.random).num_calls
        0

    :Example:
        >>> spy(mock_random.random).last_call
        Traceback (most recent call last):
         ...
        ValueError: Mocked method random() was not called.

    :Example:
        >>> when(mock_random.randint).any_call().then_return(5, 13)
        >>> mock_random.randint(a=1, b=10)
        5
        >>> mock_random.randint(10, 20)
        13
        >>> assert that(mock_random.randint).last_call == (10, 20)
        >>> assert that(mock_random.randint).nth_call(0) == ((), {"a":1, "b":10})
    """

    def __init__(self: MockCalls, method_mock: MethodMock):
        self._method_mock = method_mock

    def __repr__(self: MockCalls) -> str:
        return f"MockCalls[{self._method_mock.name}();num_calls={self.num_calls}]"

    @property
    def was_called(self: MockCalls) -> bool:
        """Return whether the mocked method was called at least once."""
        return self.num_calls > 0

    @property
    def was_not_called(self: MockCalls) -> bool:
        """Return whether the mocked method was not called."""
        return not self.was_called

    @property
    def num_calls(self: MockCalls) -> int:
        """Returns the number of calls made to the mocked method."""
        return len(self._method_mock.calls)

    @property
    def last_call(self: MockCalls) -> Union[Args, Call]:
        """Returns details of the last call made to the mocked method."""
        return self.nth_call(-1)

    def nth_call(self: MockCalls, n: int) -> Union[Args, Call]:
        """Returns details of the Nth call made to the mocked method."""
        call = self._method_mock.nth_call(n)

        args, kwargs = call

        if kwargs:
            return call
        return args
