from mocksafe.call_matchers import AnyCallMatcher, ExactCallMatcher, CustomCallMatcher
from mocksafe.custom_types import Call


ANY_CALL: Call = ((), {})


def test_any_call_matcher():
    matcher = AnyCallMatcher()

    assert matcher(ANY_CALL) is True

    assert str(matcher) == "*"


def test_exact_call_matcher():
    exact: Call = (("foo", "bar"), {"baz": "quux"})

    matcher = ExactCallMatcher(exact)

    assert matcher(ANY_CALL) is False
    assert matcher(exact) is True

    assert str(matcher) == "call(foo, bar, baz=quux)"


def test_custom_call_matcher():
    matcher = CustomCallMatcher(lambda x: x == 2)

    def call_maker(x: int) -> Call:
        return ((x,), {})

    assert matcher(call_maker(1)) is False
    assert matcher(call_maker(2)) is True
    assert matcher(call_maker(3)) is False

    assert str(matcher).startswith(
        "<function test_custom_call_matcher.<locals>.<lambda>"
    )
