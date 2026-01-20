#!/usr/bin/bash

set -ex

NAME=assert_matcher
VERSION=`awk '/VERSION = /{gsub(/'\''/, "", $3); print $3}' assert_matcher/__init__.py`

echo "Publishing $NAME-$VERSION..."
python setup.py sdist bdist_wheel
twine check dist/$NAME-$VERSION*
twine upload --skip-existing -u__token__ dist/$NAME-$VERSION*
