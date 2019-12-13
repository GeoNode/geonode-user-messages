#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name = "geonode-user-messages",
    version = "0.1.15",
    author = "Eldarion",
    author_email = "development@eldarion.com",
    description = "Fork of user-messages: a reusable private user messages application for Django",
    long_description = open("README.rst").read(),
    license = "BSD",
    url = "http://github.com/GeoNode/geonode-user-messages",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django",
    ]
)
