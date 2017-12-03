# -*- coding: utf-8 -*-
from setuptools import setup
from setuptools import find_packages


setup(
    name="SQLiteTestRunner",
    version="0.0.1",
    description="SQLite Test Runner for Python",
    long_description=open("README.md", encoding="utf8").read(),
    author="JoTsai",
    author_email="joecai1990@gmail.com",
    url="https://github.com/JoTsaiCN/SQLiteTestRunner",
    license="MIT license",
    packages=find_packages(exclude=("tests",)),
    test_suite="tests"
)
