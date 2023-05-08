# MockSafe

A mocking library developed to enable static type checking of your mocks.

It has a simple, fluent API and is designed to be used with Python's `assert` statement.

MockSafe was created out of disappointment with existing options such as `unittest.mock`, but at the same time it also borrows some inspiration from
it.

It also borrows ideas from mocking libraries in staticly typed languages, such as
the `mockito` Java library, while at the same time striving to keep the code
reasonably ideomatic.

## Usage

Please read the docs.

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
