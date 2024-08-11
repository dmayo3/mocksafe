from typing import Protocol


MethodName = str
PropertyName = str
Call = tuple[tuple, dict]


class CallMatcher(Protocol):
    def __call__(self, actual: Call) -> bool:
        ...
