#!/usr/bin/env python3

import setuptools

version = '0.0'
release = '0.0.6'

setuptools.setup(
    name='pyrser',
    version=release,
    url='https://code.google.com/p/pyrser/',
    license='GPLv3',
    maintainer='Lionel Auroux',
    maintainer_email='lionel.auroux@gmail.com',
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
        'Programming Language :: Python :: 3.3',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Software Development :: Compilers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: General',
    ],
    install_requires=['cython'],
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
