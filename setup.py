#!/usr/bin/env python
# coding: utf-8


try:
    # python setup.py test
    import multiprocessing
except ImportError:
    pass

import mistune
from setuptools import setup


def fread(filepath):
    with open(filepath, 'r') as f:
        return f.read()

setup(
    name='mistune',
    version=mistune.__version__,
    url='https://github.com/lepture/mistune',
    author='Hsiaoming Yang',
    author_email='me@lepture.com',
    description='Yet another markdown parser, inspired by marked.',
    long_description=fread('README.rst'),
    license='BSD',
    py_modules=['mistune'],
    zip_safe=False,
    platforms='any',
    tests_require=['nose'],
    test_suite='nose.collector',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Text Processing :: Markup',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
