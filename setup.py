#!/usr/bin/env python3

import setuptools

def read(fname):
    import os
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

long_desc = read('README.md')

version = '0.2'
release = '0.2.0'

setuptools.setup(
    name='pyrser',
    version=release,
    url='https://github.com/LionelAuroux/pyrser/',
    license='GPLv3',
    author='Lionel Auroux',
    author_email='lionel.auroux@gmail.com',
    description="Pyrser a pragmatic PEG parsing tool",
    long_description= long_desc,
    keywords="parse parser parsing peg packrat grammar language",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'License :: OSI Approved ::' +
            ' GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Software Development :: Compilers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: General',
    ],
    #install_requires=['cython'],
    # TODO: need some tests
    extras_require={
        'DOC': ['Sphinx', 'sphinxcontrib-programoutput'],
    },
    packages=[
        'pyrser',
        'pyrser.directives',
        'pyrser.hooks',
        'pyrser.parsing',
        'pyrser.passes',
        'pyrser.type_system'
    ],
    #    test_loader='unittest:TestLoader',
    #    test_suite='tests'
)
