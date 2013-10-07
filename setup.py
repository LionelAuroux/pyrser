#!/usr/bin/env python3.3

import setuptools

version = '0.2'
release = '0.2.1'

setuptools.setup(
    name='pyrser',
    version=release,
    url='https://code.google.com/p/pyrser/',
    license='GPLv3',
    maintainer='Lionel Auroux',
    maintainer_email='lionel.auroux@gmail.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Software Development :: Compilers',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=['pyrser', 'pyrser.directives', 'pyrser.hooks', 'pyrser.parsing',
              'pyrser.passes'],
#    test_loader='unittest:TestLoader',
#    test_suite='tests'
)
