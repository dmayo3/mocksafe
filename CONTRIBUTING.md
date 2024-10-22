# Contributing to MockSafe

Thank you for considering contributing to MockSafe! We welcome contributions of all kinds, including bug reports, feature requests, and code contributions. Please take a moment to review this guide to understand how to get started.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Features](#suggesting-features)
  - [Submitting Code](#submitting-code)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [License](#license)

## Code of Conduct

By participating in this project, you are expected to uphold the [Contributor Covenant Code of Conduct](https://github.com/dmayo3/mocksafe/blob/main/CODE_OF_CONDUCT.md). Please ensure your behavior aligns with our pledge for a welcoming and inclusive community.

## How to Contribute

### Reporting Bugs

If you find a bug in the library, please open an issue in our [GitHub Issues](https://github.com/dmayo3/mocksafe/issues) page. When reporting a bug, please include:

- A clear and descriptive title
- A description of the issue
- Steps to reproduce the issue
- Expected and actual results
- Any relevant code snippets or error messages

### Suggesting Features

We welcome feature requests! If you have an idea for a new feature, please open an issue in our [GitHub Issues](https://github.com/dmayo3/mocksafe/issues) page with:

- A clear and descriptive title
- A detailed description of the feature and its benefits
- Any relevant use cases or examples

### Submitting Code

If you would like to contribute code, please follow these steps:

1. **Fork the repository**: Click the "Fork" button at the top-right of the repository page.
2. **Clone your fork**: Use the following command to clone your fork to your local machine:

   ```bash
   git clone https://github.com/YOUR_USERNAME/mocksafe.git
   ```

3. Create a new branch: It's good practice to create a new branch for your changes:

   ```bash
   git checkout -b your-feature-branch
   ```

4. Make your changes: Implement your changes and ensure they align with our coding standards (see below).
5. Commit your changes: Write a clear and concise commit message:

   ```bash
   git clone https://github.com/YOUR_USERNAME/mocksafe.git
   ```

6. Push your changes: Push your changes to your fork:

   ```bash
   git push origin your-feature-branch
   ```

7. Create a Pull Request: Navigate to the original repository and click the "New Pull Request" button. Fill out the pull request template and describe your changes.

## Development Setup

To set up the development environment, follow these steps:

1. Clone the repository:

    ```bash
   git clone https://github.com/YOUR_USERNAME/mocksafe.git
   cd mocksafe
   ```

2. Install dependencies:
   Since this project uses pyproject.toml, you can install the dependencies using the following commands:

- For a regular installation:

   ```bash
   pip install .
   ```

- For an editable installation (recommended for development):

   ```bash
   pip install -e .
   ```

3. (Optional) Set up a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

4. Alternatively, you can use tox to manage your development environment and run tests. Install tox and run it in the project directory:

    ```bash
   pip install tox
   tox
   ```

This will automatically set up virtual environments and install dependencies for testing.

## Using Tox for Testing and Other Tasks

In addition to installing dependencies, tox can be used to manage various tasks like running tests, formatting code, linting, and building the documentation. This section is optional for contributors, but highly recommended for a streamlined workflow.

### Setting up Tox

1. First, ensure that tox is installed by running:

   ```bash
   pip install tox
   ```

2. Once tox is installed, you can run various tasks by executing tox in the project directory.

### Running Tests

- To run the test suite using tox, simply execute:

   ```bash
   tox
   ```

This will run the tests across the configured Python environments and ensure your changes don’t break existing functionality.

### Linting and Formatting

- tox can also be used to ensure that the code follows proper linting and formatting standards. To run linting and formatting checks, use:

   ```bash
   tox -e lint
   ```

This will run tools like flake8 and black (depending on your tox.ini setup) to check for any issues in the code.

### Building Documentation

- To build the Sphinx documentation using tox, run:

   ```bash
   tox -e docs
   ```

This will generate the documentation in HTML format and catch any errors during the build process.

### Running Individual Environments

- If you only want to run a specific environment, such as tests for Python 3.11 or formatting, you can specify the environment like this:

   ```bash
   tox -e py311   # Runs tests for Python 3.11
   tox -e format  # Runs code formatting
   tox -e docs    # Builds the documentation
   ```

This flexibility allows you to only run the environments you need during development.

## Coding Standards

We follow PEP 8 for Python coding standards. Ensure your code is well-documented and includes relevant tests.

- Write unit tests for your code
- Run tests using pytest before submitting your pull request

## License

By contributing to MockSafe, you agree that your contributions will be licensed under the MIT License. For more details, please see the [LICENSE](https://github.com/dmayo3/mocksafe/blob/main/LICENSE) file.

Thank you for contributing to MockSafe! We appreciate your help in making this library better for everyone.
