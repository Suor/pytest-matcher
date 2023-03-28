import pytest

from .matchers import Matcher
from .compare import pytest_assertrepr_compare  # noqa


@pytest.fixture
def M():
    return Matcher
