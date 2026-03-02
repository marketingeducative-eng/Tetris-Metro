#!/usr/bin/env python3
"""
Minimal setup.py for Metro Tetris app.
Essential for Cython compilation with correct language_level directive.

When p4a.setup_py = true in buildozer.spec, this setup.py will be used instead
of p4a's auto-generated setup.py, allowing us to set compiler_directives.

This ensures all .pyx files (including kivy's) are compiled with Python 3 syntax.
"""

from setuptools import setup
from Cython.Build import cythonize

setup(
    name='metrotetris',
    version='0.1',
    packages=['metrotetris'],
    install_requires=[
        'kivy',
        'Cython==0.29.36',
        'pyjnius==1.6.1',
    ],
    ext_modules=cythonize(
        '**/*.pyx',
        compiler_directives={'language_level': "3"},
        include_path=['.'],
        language_level='3',
    ),
    python_requires='>=3.6',
)
