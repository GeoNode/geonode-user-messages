#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name="geonode-user-messages",
    version="2.0.2",
    author="Eldarion",
    author_email="development@eldarion.com",
    description="Fork of user-messages: a reusable private user messages application for Django",
    long_description=open("README.rst").read(),
    license="BSD",
    url="http://github.com/GeoNode/geonode-user-messages",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Framework :: Django",
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ]
)
