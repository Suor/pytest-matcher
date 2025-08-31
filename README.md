# Pytest Matcher [![Build Status](https://github.com/Suor/pytest-matcher/actions/workflows/ci.yml/badge.svg)](https://github.com/Suor/pytest-matcher/actions/workflows/test.yml?query=branch%3Amaster)

The purpose of this library is to simplify asserts containing objects and nested data structures, i.e.:

```python
def test_smth(M):  # A special Matcher fixture
    # ...
    assert result.errors == [
        M(message=M.re("^Smth went wrong:"), extensions=M.dict(code=523)),
        M(message=M.any, tags=M.unordered("one", "two")),
    ]
```

Here all the structures like lists and dicts are followed as usual both outside and inside
a matcher object, while the matcher object and other helpers provide their own equality. These could be freely intermixed.

## Installation

```bash
pip install git+https://github.com/Suor/pytest-matcher.git@master
# pip install pytest-matcher  # not released yet
```

## Matchers

The `M` fixture provides a number of matchers to help you write more expressive assertions.

#### `M(**attrs)`

Matches an object's attributes.

```python
User = namedtuple("User", ["name", "email", "is_active"])

users = [User("Alice", "alice@example.com", True), User("Bob", "bob@example.com", False)]

assert users == [
    M(name="Alice", is_active=True),
    M(name="Bob", is_active=False),
]
```

#### `M.re(pattern, flags=0)`

Matches a string against a regular expression using `re.search`.

```python
assert "hello world" == M.re(r"h.*o")
```

#### `M.dict(d=None, **kwargs)`

Matches a dictionary against a subset of keys. It checks that the keys exist and their values match, but ignores other keys.

```python
assert {"a": 1, "b": 2} == M.dict(a=1)
```

#### M.any

Matches any value. This is useful when you want to ignore a particular field value in a larger data structure, but still want to test for a key presence.

```python
assert {"a": 1, "b": 2, "c": "hi"} == M.dict(a=1, b=M.any)
```

#### `M.any_of(*items)`

Matches if the value is one of the provided items.

```python
assert "a" == M.any_of("a", "b", "c")
```

#### `M.unordered(*items)`

Compares a list to the provided items, ignoring the order.

```python
assert [1, 2, 3] == M.unordered(3, 1, 2)
```

#### `M.isa(*types)`

Checks if an object is an instance of one of the provided types.

```python
assert "hello" == M.isa(str)
assert 42 == M.isa(int, float)
```

#### `M.approx(expected, rel=None, abs=None, nan_ok=False)`

Performs approximate comparison of numbers. It's a wrapper around `pytest.approx`.

```python
assert 0.1 + 0.2 == M.approx(0.3)
```

## Running tests

To run the tests using your default python:

```
pip install -r test_requirements.txt
pytest
```

To fully run `tox` you need all the supported pythons to be installed. These are
3.7+ and PyPy3. You can run it for particular environment even in absense
of all of the above:

```
tox -e py310
tox -e pypy3
tox -e lint
```
