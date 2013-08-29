import setuptools


setuptools.setup(
    name='pyrser',
    version='0.0.1a',
	url='https://code.google.com/p/pyrser/',
	license='GPLv3',
	maintainer='Lionel Auroux',
	maintainer_email='lionel.auroux@gmail.com',
	classifiers=[
	    'Development Status :: 3 - Alpha',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
		'Programming Language :: Python :: 3.3',
		'Topic :: Software Development :: Code Generators',
		'Topic :: Software Development :: Compilers',
		'Topic :: Software Development :: Libraries :: Python Modules',
	],
    packages=['pyrser', 'pyrser.directives', 'pyrser.hooks', 'pyrser.parsing'],
#    test_loader='unittest:TestLoader',
#    test_suite='tests'
)
