from setuptools import setup


# Remove build status
README = open('README.rst').read().replace('|Build Status|', '', 1)

setup(long_description=README)
