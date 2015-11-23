#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

description = """
PostgreSQL json field support for Django.
"""

setup(
    name="django-pgjson",
    version="0.3.1",
    url="https://github.com/djangonauts/django-pgjson",
    license="BSD",
    platforms=["OS Independent"],
    description=description.strip(),
    author="Andrey Antukh",
    author_email="niwi@niwi.be",
    keywords="django, postgresql, pgsql, json, field",
    maintainer="Andrey Antukh",
    maintainer_email="niwi@niwi.be",
    packages=find_packages(),
    include_package_data=False,
    install_requires=[],
    zip_safe=False,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Topic :: Internet :: WWW/HTTP",
    ]
)
