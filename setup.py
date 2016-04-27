#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


setup(
    name='kat',
    version='0.0.1',
    url='https://github.com/davidvuong/kat',

    author='David Vuong',
    author_email='david.vuong256@gmail.com',

    classifiers=[
        'Intended Audience :: Developers',

        'License :: OSI Approved :: MIT License',

        'Topic :: Utilities',

        'Programming Language :: Python :: 2 :: Only',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    license='MIT',

    packages=find_packages(exclude=['contrib', 'docs', 'test*']),
    install_requires=[
        'beautifulsoup4==4.3.2',
    ],
    include_package_data=True,
    package_data={'': ['README.md', 'LICENSE', 'CHANGELOG.txt']},
)
