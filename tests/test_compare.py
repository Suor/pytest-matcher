# from pytest_matcher.plugin import pytest_assertrepr_compare as comp
from pytest_matcher.compare import compare, to_lines

# class Config:
#     def getoption(self, name):
#         return 0


def comp_eq(left, right):
    return to_lines(compare("==", left, right))


def test_list(M):
    assert comp_eq([1, 2], [1, 3]) == ["[1]: 2 != 3"]
    assert comp_eq([1, 2, 3], [1, 2]) == ["Left contains one more item: 3"]
    assert comp_eq([1, 2], [1, 2, 3, 4]) == ["Right contains 2 more items, first one: 3"]
    assert comp_eq([1, 2], [1, 0, 2]) == [
        "First mismatch:",
        "[1]: 2 != 0",
        "Right contains one more item: 2",
    ]

    # assert compare("==", [1, [2, 3]], [1, [3, 3]]) == ""
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
