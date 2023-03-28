Pytest Matcher |Build Status|
==============

The purpose of this library is to simplify asserts containing objects and nested data structures, i.e.:

.. code:: python

    def test_smth(M):  # A special Matcher fixture
        # ...
        assert result.errors == [
            M(message=M.re("^Smth went wrong:"), extensions=M.dict(code=523)),
            M(message=M.any, tags=M.unordered("one", "two")),
        ]

Here all the structures like lists and dicts are followed as usual both outside and inside
a mather object, while the matcher object and other helpers provide their own equality. These could be freely intermixed.


Installation
-------------

.. code:: bash

    pip install git+https://github.com/Suor/pytest-matcher.git@master
    # pip install pytest-matcher  # not released yet


Overview
--------------

...


Running tests
--------------

To run the tests using your default python:

::

    pip install -r test_requirements.txt
    pytest

To fully run ``tox`` you need all the supported pythons to be installed. These are
3.7+ and PyPy3. You can run it for particular environment even in absense
of all of the above::

    tox -e py310
    tox -e pypy3
    tox -e lint


.. |Build Status| image:: https://github.com/Suor/pytest-matcher/actions/workflows/ci.yml/badge.svg
   :target: https://github.com/Suor/pytest-matcher/actions/workflows/test.yml?query=branch%3Amaster
