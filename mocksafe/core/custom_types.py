from collections.abc import Callable


MethodName = str
PropertyName = str
Call = tuple[tuple, dict]
CallMatcher = Callable[[Call], bool]
