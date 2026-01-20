# Assert Matcher [![Build Status](https://github.com/Suor/assert-matcher/actions/workflows/ci.yml/badge.svg)](https://github.com/Suor/assert-matcher/actions/workflows/test.yml?query=branch%3Amaster)

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

Alternatively may import Matcher directly this is more verbose but also more universal, i.e. works outside of pytest:

```python
from assert_matcher import M
```


## Installation

```bash
pip install assert-matcher
pip install git+https://github.com/Suor/assert-matcher.git@master  # the newest one
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

# May test class if that is important
assert user == M(__class__=User, name="Alice")
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
assert {"a": 1, "b": 2} == M.dict({"a": 1})  # same
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
assert end_time == M.approx(start_time + timedelta(seconds=1), abs=0.1)
```


## Running tests

To run the tests using your default python:

```
pip install -r test_requirements.txt
pytest
```

To fully run `tox` you need all the supported pythons to be installed. These are
3.9+ and PyPy3. You can run it for particular environment even in absense
of all of the above:

```
tox -e py314
tox -e pypy311
tox -e lint
```

## Pytest Plugin

`assert-matcher` provides enhanced assertion representation for pytest, making diffs for nested data structures more readable when using `Matcher` objects.

When a test fails, pytest usually prints a diff of the two objects that were compared. However, these diffs can be hard to read. `assert-matcher` plugin overrides the default diff representation to pinpoint an exact path and difference.

For example, consider the following failing test:

```python
def test_user(M):
    user = User("Alice", "alice@example.com", True)
    assert user == M(name="Bob", is_active=False)
```

Without the plugin, the diff would look something like this:

```
E   AssertionError: assert User(name='Alice', email='alice@example.com', is_active=True) == M(name='Bob', is_active=False)
E    +  where M(name='Bob', is_active=False) = <class 'assert_matcher.matchers.Matcher'>(name='Bob', is_active=False)
```

With the `assert-matcher` plugin enabled, the diff is much more readable:

```
E   AssertionError: assert User(name=...tive=True) == M(name='Bo...ive=False)
E     name: 'Alice' != 'Bob'
E     is_active: True != False
```

This is even more useful when you compare nested data structures. For example, consider the following test:

```python
def test_nested_structure(M):
    result = {
        "users": [alice, bob],
        "meta": ...
    }
    expected = {
        "users": [
            M(name="Alice", status="active"),
            M(name="Bob", email=M.re(r"@example\.com$")),
        ],
        "meta": M.any
    }
    assert result == expected
```

Without the plugin, the diff is hard to read (imagine these objects having 10+ fields):

```
E   AssertionError: assert {'meta': {'er... 'inactive'}]} == {'meta': M.di...ample.com$')]}
E
E     Omitting 1 identical items, use -vv to show
E     Differing items:
E     {'users': [{'email': 'alice@example.com', 'name': 'Alice', 'status': 'active'}, {'email': 'bob@invalid', 'name': 'Bob', 'status': 'inactive'}]} != {'users': [M.dict(name='Alice', status='active'), M.dict(name='Bob', email=r'@example.com$')]}
E     Use -v to get more diff
```

With the plugin, the diff is much more concise and points to the exact location of the error:

```
E   AssertionError: assert {'meta': {...active'}} == {'meta': M...e.com$')]}
E     users[1].email: 'bob@invalid' != r'@example.com$'
```
