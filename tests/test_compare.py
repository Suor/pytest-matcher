from itertools import takewhile
from unittest.mock import Mock
from assert_matcher.compare import compare, to_lines


_config = Mock()
_config.get_terminal_writer.return_value._highlight = lambda source, lexer="python": source
_config.get_verbosity.return_value = 0
_config.getoption.return_value = 0  # older pytest versions


def comp_eq(left, right):
    lines = to_lines(compare(_config, "==", left, right))
    # Filter out pytest's verbose hints that vary between local and CI environments
    # On CI: pytest shows "Full diff:" when running_on_ci() is True
    # Locally: pytest shows "Use -v to get more diff" when verbose is low
    return list(takewhile(
        lambda line: line.strip() not in ("Use -v to get more diff", "Full diff:"),
        # Also skip whitespace-only strings, these are pytest version dependent
        (line for line in lines if not line.isspace())
    ))


def test_list(M):
    assert comp_eq([1, 2], [1, 3]) == ["[1]: 2 != 3"]
    assert comp_eq([1, 2, 3], [1, 2]) == ["Left contains one more item: 3"]
    assert comp_eq([1, 2], [1, 2, 3, 4]) == ["Right contains 2 more items, first one: 3"]
    assert comp_eq([1, 2], [1, 0, 2]) == [
        "First mismatch:",
        "[1]: 2 != 0",
        "Right contains one more item: 2",
    ]
    assert comp_eq([1, [2, 3]], [1, [3, 3]]) == ["[1][0]: 2 != 3"]


def test_dict(M):
    assert comp_eq({"a": 1, "b": 2}, M.dict(a=2)) == ["a: 1 != 2"]
    assert comp_eq({"a": {"b": 1}}, M.dict(a={"b": 2})) == ["a.b: 1 != 2"]
    assert comp_eq({"a": {}}, M.dict(a={"b": 2, "c": 3})) == [
        "a:",
        "  Right contains 2 more items:",
        "  {'b': 2, 'c': 3}",
    ]

    assert comp_eq({"a": {"b.c": 1}}, M.dict(a={"b.c": 2})) == ["a.'b.c': 1 != 2"]


def test_nested_strings(M):
    result = {"data": {"text": "This is a long string with some content."}}
    expected = {"data": {"text": "This is a long string with different content."}}
    assert comp_eq(result, expected) == [
        "data.text:",
        "  'This is a lo...some content.' == 'This is a lo...rent content.'",
        "  - This is a long string with different content.",
        "  ?                            ^^^^ ----",
        "  + This is a long string with some content.",
        "  ?                            ^^^",
    ]


def test_nested_sets(M):
    result = {"data": {1, 2, 3}}
    expected = {"data": {1, 2, 4}}
    assert comp_eq(result, expected) == [
        "data:",
        "  {1, 2, 3} == {1, 2, 4}",
        "  Extra items in the left set:",
        "  3",
        "  Extra items in the right set:",
        "  4",
    ]


def test_nested_bytes(M):
    result = {"data": b"hello"}
    expected = {"data": b"world"}
    assert comp_eq(result, expected) == [
        "data:",
        "  b'hello' == b'world'",
        "  At index 0 diff: b'h' != b'w'",
    ]


# def test_nested_strings_demo(M):
#     result = {"data": {"text": "This is a long string with some content."}}
#     expected = {"data": {"text": "This is a long string with different content."}}
#     assert result == expected


# def test_nested_sets_demo(M):
#     result = {"data": {1, 2, 3}}
#     expected = {"data": {1, 2, 4}}
#     assert result == expected


# def test_nested_bytes_demo(M):
#     result = {"data": b"hello"}
#     expected = {"data": b"world"}
#     assert result == expected
