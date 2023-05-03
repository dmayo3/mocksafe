from typing import TypeVar, Any, cast
from collections import defaultdict
from collections.abc import Callable


T = TypeVar("T")
F = TypeVar("F", bound=Callable)

MethodName = str
StubResult = Any
Args = tuple
Call = tuple[tuple, dict]


class SafeMock:
    def __init__(self, class_type):
        self._class_type = class_type
        self._calls: dict[MethodName, list[Call]] = defaultdict(list)
        self._stubs: dict[MethodName, Callable] = {}

    # This is a bit of a hack to fool isinstance checks.
    # Is there a better way?
    @property  # type: ignore
    def __class__(self):
        return self._class_type

    def __getattr__(self, method_name: str):
        def mock_func(*args, **kwargs):
            # Record call
            self._calls[method_name].append((tuple(args), kwargs.copy()))

            if implementation := self._stubs.get(method_name):
                return implementation(*args, **kwargs)

            # Get a default return type value
            original_method: Callable = self._class_type.__dict__[method_name]
            return_type = original_method.__annotations__["return"]
            default_value = return_type()
            return default_value

        return mock_func


def safe_mock(class_type: type[T]) -> T:
    # Is there a more type safe / proper way to do this?
    return cast(T, SafeMock(class_type))


def stub(mock_func: Callable[..., T], return_value: T) -> None:
    # pylint: disable=unused-argument
    def stub_return(*args, **kwargs) -> T:
        return return_value

    stub_implementation(mock_func, stub_return)


def stub_implementation(mock_func: F, implementation: F) -> None:
    method_name = _get_method_name(mock_func)
    mock: SafeMock = _get_mock_instance(mock_func)
    mock._stubs[method_name] = implementation


def called(mock_func: Callable) -> bool:
    return num_calls(mock_func) > 0


def num_calls(mock_func: Callable) -> int:
    return len(_get_mock_calls(mock_func))


def nth_call(mock_func: Callable, n: int) -> Args | Call:
    calls: list[Call] = _get_mock_calls(mock_func)
    call = calls[n]

    args, kwargs = call

    if kwargs:
        return call
    return args


def last_call(mock_func: Callable) -> Args | Call:
    return nth_call(mock_func, -1)


def _get_mock_calls(mock_func: Callable) -> list[Call]:
    method_name = _get_method_name(mock_func)
    mock_instance = _get_mock_instance(mock_func)

    return mock_instance._calls[method_name]


def _get_method_name(mock_func: Callable) -> MethodName:
    if mock_func.__closure__ is None:
        raise ValueError(f"Not a SafeMocked method: {mock_func}")
    return mock_func.__closure__[0].cell_contents


def _get_mock_instance(mock_func: Callable) -> SafeMock:
    if mock_func.__closure__ is None:
        raise ValueError(f"Not a SafeMocked method: {mock_func}")
    return mock_func.__closure__[1].cell_contents
