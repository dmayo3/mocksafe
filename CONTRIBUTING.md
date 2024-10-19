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

By participating in this project, you are expected to uphold the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). Please ensure your behavior aligns with our pledge for a welcoming and inclusive community.

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

   ```bash
   pip install -r requirements.txt
   ```

3. (Optional) Set up a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

## Coding Standards

We follow PEP 8 for Python coding standards. Ensure your code is well-documented and includes relevant tests.

- Write unit tests for your code
- Run tests using pytest before submitting your pull request

## License

By contributing to MockSafe, you agree that your contributions will be licensed under the MIT License. For more details, please see the [LICENSE] file.

Thank you for contributing to MockSafe! We appreciate your help in making this library better for everyone.
