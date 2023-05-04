# MockSafe

A mocking library developed to enable static type checking of your mocks.

It has a simple, fluent API and is designed to be used with Python's `assert` statement.

MockSafe was created out of disappointment with existing options such as `unittest.mock`.

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
