#!/usr/bin/env python3

import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='hydration',
    version='1.0.1',
    description='A module for serialization of structs into binary data',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/shustinm/hydration',
    author='Michael Shustin',
    author_email='michaelshustin@gmail.com',
    packages=setuptools.find_packages(),
    install_requires=['pyhooks>=1.0.3'],
    classifiers=[
        'Programming Language :: Python :: 3'
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent'
    ],
    python_requires='>=3.6',
)
