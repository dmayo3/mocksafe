# MockSafe

A mocking library developed to enable static type checking of your mocks.

It has a simple, fluent API and is designed to be used with Python's `assert` statement.

MockSafe was created out of disappointment with existing options such as `unittest.mock`.

## Usage

First import the following in your test:

```python
from mocksafe import mock, when, that, spy
```

Suppose you have a simple class that you want to mock that looks like this:

```python
class MyClass:
    def foo(self, bar: str, baz: int = 123) -> int:
        return baz + len(bar)
```

Here's how you would mock it, and as you can see it has
the original class as the type.

```python
mock_object: MyClass = mock(MyClass)
```

Here are some basic assertions on the mock object:

```python
assert that(mock_object.foo).was_not_called

result = mock_object.foo("hello")

assert result == 0
assert that(mock_object.foo).was_called
assert that(mock_object.foo).num_calls == 1
assert that(mock_object.foo).last_call == ("hello",)
assert that(mock_object.foo).nth_call(0) == ("hello",)
```

Here's the simplest way to stub a result that isn't dependent on
what the mocked method is called with:

```python
when(mock_object.foo).any_call().then_return(3)

assert mock_object.foo("anything") == 3
```

Here we stub a result that's conditional on the arguments it's called with:

```python
when(mock_object.foo)\
    .called_with(bar="hi", baz=456)\
    .then_return(789)

assert mock_object.foo(bar="hi", baz=456) == 789

assert mock_object.foo("something else") == 0
```

If the function is called with keywords, you can assert the call results like so:

```python
mock_object.foo(bar="hello", baz=456)

assert that(mock_object.foo).last_call == ((), dict(bar="hello", baz=456))
```

To stub multiple consecutive results:

```python
when(mock_object.foo).any_call().then_return(123, 456, 789)

assert mock_object.foo("a") == 123
assert mock_object.foo("b") == 456
assert mock_object.foo("c") == 789
assert mock_object.foo("d") == 789
```

To raise an exception:

```python
when(mock_object.foo)\
    .called_with(mock_object.foo("bad"))\
    .then_raise(ValueError("Invalid argument"))
```

To return a mixture of results and exceptions over consecutive calls:

```python
when(mock_object.foo)\
    .called_with(mock_object.foo("bad"))\
    .use_side_effects(1, 2, 3, ValueError("Invalid argument"), 5, 6)
```

To implement a custom result with a lambda function:

```python
when(mock_object.foo)\
    .called_with(mock_object.foo("custom"))\
    .then(lambda bar, baz=123: len(bar) + baz * 2)
```

To get the details of a particular call to make more precise assertions:

```python
args = spy(mock_object.foo).nth_call(1)

assert len(args) == 1

args, kwargs = spy(mock_object.foo).last_call

assert args[0] == "abc"
assert kwargs.get("baz") == 7
```

The `spy()` function is just a synonym for `that()`.

## Development

To lint, type check, format, and run tests use [tox](https://tox.wiki/en/latest/):

```
pip install tox

tox [--parallel]
```

If you want to use pyenv to manage and test with multiple python versions, install the `tox-pyenv` plugin:

```
pip install tox-pyenv
```

This should read from `.python-version`.

## Build

To build this package, use [pypa-build](https://github.com/pypa/build):

```
pip install build

python -m build
```

This will produce output under `dist/`.
