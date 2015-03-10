#!/usr/bin/env python
# coding: utf-8
from __future__ import print_function

try:
    # python setup.py test
    import multiprocessing
except ImportError:
    pass

import mistune
from setuptools import setup, Extension

cmdclass = {}

try:
    from Cython.Distutils import build_ext
except ImportError:
    have_cython = False
else:
    have_cython = True
    import sys

    # Failsafe compilation originally from simplejson. Author: Bob Ippolito
    # Copied here from markupsafe
    from distutils.errors import CCompilerError, DistutilsExecError
    from distutils.errors import DistutilsPlatformError

    is_jython = 'java' in sys.platform
    is_pypy = hasattr(sys, 'pypy_version_info')

    ext_errors = (CCompilerError, DistutilsExecError, DistutilsPlatformError)
    if sys.platform == 'win32' and sys.version_info > (2, 6):
        # 2.6's distutils.msvc9compiler can raise an IOError when failing to
        # find the compiler
        ext_errors += (IOError,)

    class BuildFailed(Exception):
        pass

    class ve_build_ext(build_ext):
        """This class allows C extension building to fail."""
        def run(self):
            try:
                build_ext.run(self)
            except DistutilsPlatformError:
                raise BuildFailed()

        def build_extension(self, ext):
            try:
                build_ext.build_extension(self, ext)
            except ext_errors:
                raise BuildFailed()
            except ValueError as e:
                # this can happen on Windows 64 bit, see Python issue 7511
                if "'path'" in str(e):
                    raise BuildFailed()
                raise

    cmdclass['build_ext'] = ve_build_ext

# patch bdist_wheel
try:
    from wheel.bdist_wheel import bdist_wheel

    REPLACE = (
        'macosx_10_6_intel.'
        'macosx_10_9_intel.'
        'macosx_10_9_x86_64.'
        'macosx_10_10_intel.'
        'macosx_10_10_x86_64'
    )

    class _bdist_wheel(bdist_wheel):
        def get_tag(self):
            tag = bdist_wheel.get_tag(self)
            if tag[2] == 'macosx_10_6_intel':
                tag = (tag[0], tag[1], REPLACE)
            return tag

    cmdclass['bdist_wheel'] = _bdist_wheel
except ImportError:
    pass


def fread(filepath):
    with open(filepath, 'r') as f:
        return f.read()


def run_setup(with_binary):
    ext_modules = [Extension('mistune', ['mistune.py'])] if with_binary else []
    setup(
        name='mistune',
        version=mistune.__version__,
        url='https://github.com/lepture/mistune',
        author='Hsiaoming Yang',
        author_email='me@lepture.com',
        description='The fastest markdown parser in pure Python',
        long_description=fread('README.rst'),
        license='BSD',
        py_modules=['mistune'],
        cmdclass=cmdclass,
        ext_modules=ext_modules,
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
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: Implementation :: CPython',
            'Programming Language :: Python :: Implementation :: PyPy',
            'Topic :: Text Processing :: Markup',
            'Topic :: Software Development :: Libraries :: Python Modules'
        ]
    )


def try_building_extension():
    try:
        run_setup(True)
    except BuildFailed:
        LINE = '=' * 74
        BUILD_EXT_WARNING = 'WARNING: The C extension could not be ' \
                            'compiled, speedups are not enabled.'
        print(LINE)
        print(BUILD_EXT_WARNING)
        print('Failure information, if any, is above.')
        print('Retrying the build without the C extension now.')
        print()
        run_setup(False)
        print(LINE)
        print(BUILD_EXT_WARNING)
        print('Plain-Python installation succeeded.')
        print(LINE)


if have_cython and not(is_jython or is_pypy):
    try_building_extension()
else:
    run_setup(False)
