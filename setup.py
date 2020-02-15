#!/usr/bin/env python3

import setuptools

setuptools.setup(
    name='hydration',
    version='1.0.0',
    description='A module for serialization of structs into binary data',
    author='Michael Shustin',
    author_email='michaelshustin@gmail.com',
    packages=['hydration'],
    install_requires=['pyhooks>=1.0.3']
)
