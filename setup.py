#!/usr/bin/env python
# coding: utf-8
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
    description='A sane Markdown parser with useful plugins and renderers',
    long_description=fread('README.rst'),
    license='BSD',
    packages=[
        'mistune', 'mistune.plugins', 'mistune.directives'
    ],
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
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Text Processing :: Markup',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
