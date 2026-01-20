import pprint
from collections import defaultdict
from collections.abc import Mapping, Set
from functools import partial
from itertools import count

from _pytest._io.saferepr import safeformat, saferepr
from _pytest.assertion.util import issequence, assertrepr_compare

from .matchers import Matcher, MatcherDict


def pytest_assertrepr_compare(config, op: str, left, right):
    import shutil
    import _pytest._code

    verbose = config.get_verbosity() if hasattr(config, "get_verbosity") \
        else config.getoption("verbose")
    if verbose > 1:
        left_repr = safeformat(left)
        right_repr = safeformat(right)
    else:
        hspace = max(80, shutil.get_terminal_size().columns - 10)
        hspace -= len("E       AssertionError: assert") + len(op) + 2  # 2 spaces
        left_repr = saferepr(left, maxsize=hspace // 2)
        right_repr = saferepr(right, maxsize=hspace - len(left_repr))

    try:
        explanation = to_lines(compare(config, op, left, right))
        # NOTE: not calling _compare_eq_iterable() anywhere for now
    except Exception:
        crash = _pytest._code.ExceptionInfo.from_current()._getreprcrash()
        explanation = [
            "assert_matcher comparison failed:",
            f"  {crash}",
            "Probably an object has a faulty __repr__.",
        ]

    if not explanation:
        return None

    summary = f"{left_repr} {op} {right_repr}"
    return [summary] + explanation


def compare(config, op, left, right):
    explanation = []
    for test, explain in EXPLAINERS[op]:
        if test(left, right):
            return explain(config, left, right)
    return explanation


def compare_eq(config, left, right):
    return compare(config, "==", left, right) or [f"{left!r} != {right!r}"]


# Explainers framework

EXPLAINERS = defaultdict(list)


def register_explainer(op, test, explain=None):
    if explain is None:
        return partial(register_explainer, op, test)
    EXPLAINERS[op].append((test, explain))
    return explain  # Return the function when we use this as a decorator


def both(test):
    return lambda left, right: test(left) and test(right)


def bothis(cls):
    return lambda left, right: isinstance(left, cls) and isinstance(right, cls)


def anyis(cls):
    return lambda left, right: isinstance(left, cls) or isinstance(right, cls)


@register_explainer("==", anyis(MatcherDict))
def _explain_m_dict(config, left, right):
    if isinstance(left, MatcherDict) and isinstance(right, MatcherDict):
        return ["Should not compare two M.dict() instances"]

    if isinstance(left, MatcherDict):
        matcher_side, val, matcher, left_d, right_d = "Left", right, left, left.d, right
    else:
        matcher_side, val, matcher, left_d, right_d = "Right", left, right, left, right.d

    explanation = _dict_extra(matcher_side, matcher.d, val)

    # NOTE: not using sets here to use the matchers keys order
    diff = _dict_diff(config, [k for k in matcher.d if k in val], left_d, right_d)
    return explanation + diff


@register_explainer("==", bothis(Mapping))
def _explain_dict(config, left, right):
    explanation = []

    for side, more, less in [("Left", left, right), ("Right", right, left)]:
        explanation.extend(_dict_extra(side, more, less))

    # NOTE: not using sets here to preserve keys order
    diff = _dict_diff(config, [k for k in right if k in left], left, right)
    return explanation + diff


def _dict_extra(side, more, less):
    explanation = []
    extra = {k: v for k, v in more.items() if k not in less}
    if extra:
        n = len(extra)
        explanation.append(f"{side} contains {n} more item{'' if n == 1 else 's'}:")
        explanation.extend(pprint.pformat(extra).splitlines())
    return explanation


def _dict_diff(config, keys, left, right):
    # NOTE: we use simple key with no ["..."] wrapping to make it cleaner
    items = {k: compare_eq(config, left[k], right[k]) for k in keys if left[k] != right[k]}
    return Explanation(prefix="Differing items:", items=items) if items else []


class Missing:
    def __str__(self):
        return "<missing>"

    __repr__ = __str__


missing = Missing()


@register_explainer("==", anyis(Matcher))
def _explain_m(config, left, right):
    if isinstance(left, Matcher) and isinstance(right, Matcher):
        return ["Should not compare two M() instances"]

    if isinstance(left, Matcher):
        matcher, left_d = left, left.attrs
        right_d = {k: getattr(right, k, missing) for k in left_d}
    else:
        matcher, right_d = right, right.attrs
        left_d = {k: getattr(left, k, missing) for k in right_d}

    return _dict_diff(config, matcher.attrs, left_d, right_d)


@register_explainer("==", bothis(Set))
def _explain_set(config, left, right):
    return assertrepr_compare(config, "==", left, right)


@register_explainer("==", bothis(str))
def _explain_str(config, left, right):
    return assertrepr_compare(config, "==", left, right)


# TODO: catch a situation when some item was removed in the middle?
#       what about swap?
@register_explainer("==", both(issequence))
def _explain_seq(config, left, right):
    if isinstance(left, bytes) and isinstance(right, bytes):
        return assertrepr_compare(config, "==", left, right)

    explanation = []
    for i, l, r in zip(count(), left, right):
        if l != r:  # noqa
            explanation = Explanation("First mismatch:", {f"[{i}]": compare_eq(config, l, r)})
            # NOTE: we are ignoring other mismatches, and "First mismatch:" above won't be shown
            #       if the below section will yield nothing
            break

    len_diff = len(left) - len(right)
    if len_diff:
        if len_diff > 0:
            side, extra = "Left", left[len(right)]
        else:
            side, extra = "Right", right[len(left)]
            len_diff = -len_diff

        if len_diff == 1:
            explanation += [f"{side} contains one more item: {extra!r}"]
        else:
            explanation += [f"{side} contains {len_diff} more items, first one: {extra!r}"]
    return explanation


class Explanation(dict):
    """An explanation of a diff for dicts and objects.

    Converted to lines of strings before returning to pytest. This delaying of rendering allows to
    join keys when we find differences in nested structures.

    Allows separating diff collection from rendering partially. We want to reuse some of
    the _pytest.assertion.util code, so we work with both this and list[str].
    """
    def __init__(self, prefix, items):
        self._prefix = prefix
        self.update(items)

    def add(self, other, reverse=False):
        if not other:
            return self
        elif isinstance(other, list):
            rendered = [self._prefix] + to_lines(self)
            return other + rendered if reverse else rendered + other
        raise NotImplementedError

    def __add__(self, other):
        return self.add(other)

    def __radd__(self, other):
        return self.add(other, reverse=True)


def to_lines(expl, path=""):
    """Coerce explanation to lines of strings"""
    if isinstance(expl, list):
        return expl

    # NOTE: we only escape string keys if they contain "." for readablity.
    #       This makes object attrs look the same as dict keys though.
    def escape_key(k):
        return repr(k) if not k.startswith("[") and "." in k else k

    explanation = []
    for k, lines in expl.items():
        # full_path = f"{path}.{escape_key(k)}" if path else escape_key(k)
        if path:
            full_path = path + k if k.startswith("[") else f"{path}.{escape_key(k)}"
        else:
            full_path = escape_key(k)
        if isinstance(lines, dict):
            explanation.extend(to_lines(lines, path=full_path))
        elif len(lines) == 1:
            explanation.append(f"{full_path}: " + lines[0])
        else:
            explanation.append(f"{full_path}:")
            explanation.extend(["  " + l for l in lines])  # noqa
    return explanation
