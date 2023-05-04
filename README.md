# MockSafe

A mocking library developed to enable static type checking of your mocks.

It has a simple, fluent API and is designed to be used with Python's `assert` statement.

MockSafe was created out of disappointment with existing options such as `unittest.mock`.

## Usage

First import the following in your test:

```
from mocksafe import mock, when, that
```

Suppose you have a simple class that you want to mock that looks like this:

```
class MyClass:
    def foo(self, bar: str, baz: int = 123) -> int:
        return baz + len(bar)
```

Here's a few basic ways you can mock it:

```
mock_object: MyClass = mock(MyClass)

assert that(mock_object.foo).was_not_called

result = mock_object.foo("hello")

assert result == 0
assert that(mock_object.foo).was_called
assert that(mock_object.foo).num_calls == 1
assert that(mock_object.foo).last_call == ("hello",)
assert that(mock_object.foo).nth_call(0) == ("hello",)
```

Here we stub a result:

```
mock_object: MyClass = mock(MyClass)

when(mock_object.foo).called_with(bar="hi", baz=456).then_return(789)

assert mock_object.foo(bar="hello", baz=456) == 789

assert that(mock_object.foo).last_call == ((), dict(bar="hello", baz=456))
```

To stub multiple consecutive results:

```
mock_object: MyClass = mock(MyClass)

when(mock_object.foo).any_call().then_return(123, 456, 789)

assert mock_object.foo("a") == 123
assert mock_object.foo("b") == 456
assert mock_object.foo("c") == 789
assert mock_object.foo("d") == 789
```

## Development

To lint, type check, format, and run tests use [tox](https://tox.wiki/en/latest/):

```
pip install tox

tox [--parallel]
```

## Build

To build this package, use [pypa-build](https://github.com/pypa/build):

```
pip install build

python -m build
```

This will produce output under `dist/`.
