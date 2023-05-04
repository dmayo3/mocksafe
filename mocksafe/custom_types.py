from collections.abc import Callable


MethodName = str
Call = tuple[tuple, dict]
CallMatcher = Callable[[Call], bool]
