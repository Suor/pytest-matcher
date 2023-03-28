import re
# from datetime import datetime, timedelta
from types import SimpleNamespace

# import pytest


def test_object(M):
    assert repr(M(foo="foo")) == "M(foo='foo')"

    obj = SimpleNamespace(foo="foo", bar="bar")
    assert obj == M(foo="foo")
    assert obj != M(bar="zoo")
    assert obj != M(missing=42)
    assert obj != M(foo="foo", more="bar")


def test_object_class(M):
    class A:
        pass

    assert repr(M(__class__=A, x=1, y=2)) == "M.A(x=1, y=2)"
    assert A() == M(__class__=A)
    assert A() != M(__class__=SimpleNamespace)


def test_dict(M):
    assert repr(M.dict(foo="foo", n=123)) == "M.dict(foo='foo', n=123)"

    # pytest needs len() to be there when there is no explanation
    assert len(M.dict({"a": 1, "b": 2})) == 2

    actual = {"base_url": "url", "verify": "bundle", "timeout": 10}
    assert actual == M.dict(verify="bundle", timeout=10)
    assert actual == M.dict(actual, verify="bundle")
    assert actual != M.dict(verify="bundle.pem")
    assert actual != M.dict(missing=42)


def test_dict_subclass(M):
    class SubDict(dict):
        pass

    assert SubDict(a=1) == M.dict()
    assert M.dict() == SubDict(a=1)


def test_re(M):
    assert repr(M.re(r"^plots\.csv-\w+$")) == r"r'^plots\.csv-\w+$'"
    assert repr(M.re(r"\w+\.csv", re.I)) == r"M.re(r'\w+\.csv', 2)"

    assert "500 Internal Error" == M.re(r"^500 Internal")
    assert "200 OK" != M.re(r"^500 Internal")
    assert "... 500" != M.re(r"^500")
    assert "... Hostname ..." == M.re(r"host", re.I)


def test_any(M):
    assert repr(M.any) == "M.any"
    assert "a" == M.any
    assert {"x": 1, "y": 2} == {"x": 1, "y": M.any}


def test_any_of(M):
    assert repr(M.any_of(3, 4)) == "M.any_of(3, 4)"

    assert 3 == M.any_of(3, 4)
    assert 'x' != M.any_of(3, 4)
    assert M.any_of(3, 4) in [0, 4]
    assert M.any_of(3, 4) not in [0, 2]


def test_isa(M):
    assert repr(M.isa(str)) == "M.isa(str)"
    assert repr(M.isa(str, bytes)) == "M.isa(str, bytes)"

    assert "5" == M.isa(str) == "5"
    assert 5 != M.isa(str) != 5

    assert 5 == M.isa(int, str) == "5"
    assert 5 != M.isa(str, bytes) == b"5"


def test_unordered(M):
    assert repr(M.unordered("foo", "bar")) == "M.unordered('bar', 'foo')"

    assert ["c", "b", "a"] == M.unordered("a", "b", "c")
    assert ("a", "c", "b") == M.unordered("b", "c", "a")
    assert ["a", "b"] != M.unordered("a", "c")


# def test_approx_datetime_repr(M):
#     obj = M.approx(datetime(2021, 11, 29))
#     assert repr(obj) == (
#         "approx_datetime(datetime.datetime(2021, 11, 29, 0, 0) "
#         "± datetime.timedelta(seconds=1))"
#     )


# def test_approx_datetime(M):
#     assert M.approx(datetime.now()) == datetime.now()
#     with pytest.raises(AssertionError):
#         expected = datetime.now() - timedelta(seconds=10)
#         assert M.approx(expected) == datetime.now()


# def test_approx_should_fallback_to_pytest(M):
#     assert M.approx(3.0 + 1e-6) == 3


# def test_M(M):
#     experiments = {
#         "b05eec": {
#             "baseline": {
#                 "data": {
#                     "timestamp": datetime(2021, 8, 2, 16, 48, 14),
#                     "params": {
#                         "params.yaml": {
#                             "data": {
#                                 "featurize": {
#                                     "max_features": 3000,
#                                     "ngrams": 1,
#                                 },
#                                 "parent": 20170428,
#                                 "train": {
#                                     "n_est": 100,
#                                     "min_split": 2,
#                                 },
#                             }
#                         }
#                     },
#                     "name": "master",
#                 }
#             }
#         }
#     }

#     assert experiments == {
#         "b05eec": {
#             "baseline": {
#                 "data": M.dict(
#                     timestamp=M.approx(datetime(2021, 8, 2, 16, 48, 15)),
#                     params={
#                         "params.yaml": M.dict(
#                             data=M.dict(
#                                 featurize=M.any,
#                                 parent=20170428,
#                                 train=M.dict(n_est=100),
#                             )
#                         ),
#                     },
#                     name=M.re(r"master"),
#                 )
#             }
#         }
#     }
