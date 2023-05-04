import itertools
from typing import Generic, TypeVar, Any, cast
from collections.abc import Callable


T = TypeVar("T")
F = TypeVar("F", bound=Callable)

MethodName = str
StubResult = Any
Args = tuple
Call = tuple[tuple, dict]
CallMatcher = Callable[[Call], bool]

MOCK_NUMBER = itertools.count()


class ExactCallMatcher:
    def __init__(self, exact: Call):
        self._exact = exact

    def __call__(self, actual: Call) -> bool:
        return actual == self._exact

    def __repr__(self) -> str:
        args, kwargs = self._exact
        fmt_args = ", ".join(args)
        fmt_kwargs = ", ".join(f"{k}={v}" for k, v in kwargs.items())
        call_sig = f"{fmt_args}, {fmt_kwargs}" if kwargs else fmt_args
        return f"call({call_sig})"


class AnyCallMatcher:
    def __call__(self, _: Call) -> bool:
        return True

    def __repr__(self) -> str:
        return "*"


class MethodStub(Generic[T]):
    def __init__(self, name: MethodName, result_type: type[T]):
        self._name = name
        self._stubs: list[tuple[CallMatcher, list[T]]] = []
        self._result_type = result_type

    def __call__(self, *args, **kwargs) -> T:
        call = (tuple(args), kwargs)
        for matcher, results in self._stubs:
            if matcher(call):
                if len(results) == 1:
                    return results[0]
                return results.pop(0)

        default_value = self._result_type()
        return default_value

    def __repr__(self) -> str:
        reps = []
        for matcher, result in self._stubs:
            reps.append(f"{matcher} -> {result}")
        return ";".join(reps)

    @property
    def name(self) -> MethodName:
        return self._name

    def add(self, matcher: CallMatcher, results: list[T]) -> None:
        self._stubs.append((matcher, results))


class MethodSpy(Generic[T]):
    def __init__(self, name: MethodName, delegate: Callable[..., T]):
        self._name = name
        self._delegate = delegate
        self._calls: list[Call] = []

    def __call__(self, *args, **kwargs) -> T:
        self._calls.append((tuple(args), kwargs.copy()))
        return self._delegate(*args, **kwargs)

    def __repr__(self) -> str:
        return f"MethodSpy[{self._name}:{len(self.calls)} call(s)]"

    @property
    def name(self) -> MethodName:
        return self._name

    @property
    def calls(self) -> list[Call]:
        return self._calls

    def pop_call(self) -> Call:
        return self._calls.pop()

    def nth_call(self, n: int) -> Call:
        return self._calls[n]


class MethodMock(Generic[T]):
    def __init__(self, name: MethodName, result_type: type[T]):
        self._stub = MethodStub(name, result_type)
        self._spy = MethodSpy(name, self._stub)

    def __call__(self, *args, **kwargs) -> T:
        return self._spy(*args, **kwargs)

    def __repr__(self) -> str:
        return f"MethodMock[{self._stub}]"

    @property
    def name(self) -> MethodName:
        return self._stub.name

    def add_stub(self, matcher: CallMatcher, results: list[T]) -> None:
        self._stub.add(matcher, results)

    def stub_last_call(self, results: list[T]) -> None:
        call = self._spy.pop_call()
        matcher = ExactCallMatcher(call)
        self._stub.add(matcher, results)

    @property
    def calls(self) -> list[Call]:
        return self._spy._calls

    def nth_call(self, n: int) -> Call:
        return self._spy.nth_call(n)


class SafeMock(Generic[T]):
    def __init__(self, class_type: type[T], name: str | None = None):
        self._class_type = class_type
        self._mocks: dict[MethodName, MethodMock] = {}
        self._name = name or next(MOCK_NUMBER)

    @property
    def mocked_methods(self) -> dict[MethodName, MethodMock]:
        return self._mocks.copy()

    # This is a bit of a hack to fool isinstance checks.
    # Is there a better way?
    @property  # type: ignore
    def __class__(self):
        return self._class_type

    def __repr__(self) -> str:
        return f"SafeMock[{self._class_type.__name__}#{self._name}]"

    def __getattr__(self, method_name: MethodName) -> MethodMock:
        if method_mock := self._mocks.get(method_name):
            return method_mock

        original_method: Callable = self._class_type.__dict__[method_name]
        return_type: type = original_method.__annotations__["return"]
        method_mock = MethodMock(method_name, return_type)
        self._mocks[method_name] = method_mock
        return method_mock


class MatchCallStubber(Generic[T]):
    def __init__(self, method_mock: MethodMock[T], matcher: CallMatcher):
        self._method_mock = method_mock
        self._matcher = matcher

    def then_return(self, result: T, *consecutive_results: T) -> None:
        results: list[T] = [result, *consecutive_results]
        self._method_mock.add_stub(self._matcher, results)


class LastCallStubber(Generic[T]):
    def __init__(self, method_mock: MethodMock[T]):
        self._method_mock = method_mock

    def then_return(self, result: T, *consecutive_results: T) -> None:
        results: list[T] = [result, *consecutive_results]
        self._method_mock.stub_last_call(results)


class WhenStubber(Generic[T]):
    def __init__(self, method_mock: MethodMock[T]):
        self._method_mock = method_mock

    def any_call(self) -> MatchCallStubber[T]:
        return MatchCallStubber(self._method_mock, AnyCallMatcher())

    def called_with(self, _: T) -> LastCallStubber[T]:
        return LastCallStubber(self._method_mock)


class CallSpy:
    def __init__(self, method_mock: MethodMock):
        self._method_mock = method_mock

    @property
    def was_called(self) -> bool:
        return self.num_calls > 0

    @property
    def was_not_called(self) -> bool:
        return not self.was_called

    @property
    def num_calls(self) -> int:
        return len(self._method_mock.calls)

    @property
    def last_call(self) -> Args | Call:
        return self.nth_call(-1)

    def nth_call(self, n: int) -> Args | Call:
        call = self._method_mock.nth_call(n)

        args, kwargs = call

        if kwargs:
            return call
        return args


def mock(class_type: type[T]) -> T:
    # Is there a more type safe / proper way to do this?
    return cast(T, SafeMock(class_type))


def when(mock_method: Callable[..., T]) -> WhenStubber[T]:
    if not isinstance(mock_method, MethodMock):
        raise ValueError("Not a SafeMocked method: mock_method")
    return WhenStubber(mock_method)


def that(mock_method: Callable) -> CallSpy:
    if not isinstance(mock_method, MethodMock):
        raise ValueError("Not a SafeMocked method: mock_method")
    return CallSpy(mock_method)
