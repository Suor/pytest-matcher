#!/usr/bin/bash

set -ex

NAME=pytest-matcher
VERSION=`awk '/VERSION = /{gsub(/'\''/, "", $3); print $3}' pytest_matcher/__init__.py`

echo "Publishing $NAME-$VERSION..."
python setup.py sdist bdist_wheel
twine check dist/$NAME-$VERSION*
twine upload --skip-existing -uSuor dist/$NAME-$VERSION*
