from datetime import datetime, timedelta

import pytest
from _pytest.python_api import ApproxBase


def approx(expected, rel=None, abs=None, nan_ok=False):
    if isinstance(expected, datetime):
        if rel is not None:
            raise TypeError("rel doesn't make sense with a datetime")
        return ApproxDatetime(expected, abs=abs)

    return pytest.approx(expected, rel=rel, abs=abs, nan_ok=nan_ok)


class ApproxDatetime(ApproxBase):
    """Perform approximate comparisons between datetime."""
    default_abs = timedelta(seconds=1)

    def __init__(self, expected, abs=None):
        assert isinstance(expected, datetime)

        if abs is None:
            abs = self.default_abs
        elif isinstance(abs, int):
            abs = timedelta(seconds=abs)

        assert abs >= timedelta(0), f"absolute tolerance can't be negative: {abs}"
        super().__init__(expected, abs=abs)

    def __repr__(self):
        return f"approx({self.expected} ± {self.abs})"

    def __eq__(self, actual: object) -> bool:
        return abs(self.expected - actual) <= self.abs
