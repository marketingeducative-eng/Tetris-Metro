#!/usr/bin/env python3

from setuptools import find_packages, setup

setup(
    name='metrotetris',
    version='0.1',
    install_requires=[
        'kivy',
        'setuptools',
        'Cython==0.29.36',
        'pyjnius==1.6.1',
    ],
    packages=find_packages(exclude=('tests', 'docs', 'scripts')),
    include_package_data=True,
    python_requires='>=3.10',
)
