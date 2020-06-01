#!/usr/bin/env python3

import setuptools
from pathlib import Path

with open(Path('docs') / 'README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='hydration',
    version='3.1.2',
    description='A module used to define python objects that can be converted to (and from) bytes.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/shustinm/hydration',
    author='Michael Shustin',
    author_email='michaelshustin@gmail.com',
    packages=setuptools.find_packages(),
    install_requires=['pyhooks>=1.0.3'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent'
    ],
    python_requires='>=3.6',
)
