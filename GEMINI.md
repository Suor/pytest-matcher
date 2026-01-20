# Project Overview

This project is a Python library called `assert-matcher`. Its purpose is to simplify asserts containing objects and nested data structures in tests.

It will work with any test framework by overloaing equality, it also provides pytest plugin to show nice diffs with its matcher objects.

The project is structured as a standard Python package with a `setup.py` file and a `assert_matcher` module.

# Building and Running

**Installation:**

```bash
pip install -r test_requirements.txt
```

**Running tests:**

To run tests with the default python version:

```bash
pytest
```

To run tests for a specific python version with `tox`:

```bash
tox -e py310
```

To run linting checks:

```bash
flake8
```

# Development Conventions

*   The code is formatted with a maximum line length of 100 characters.
*   The project uses `flake8` for linting.
*   Tests are located in the `tests/` directory.
*   The project uses `tox` to automate testing in different python environments.
