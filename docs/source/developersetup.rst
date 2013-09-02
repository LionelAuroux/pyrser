Setup your environment
======================
Install setuptools and sphinx::

    pip install setuptools sphinx
	
Clone the pyrser repository::

	hg clone -b deviopi https://code.google.com/p/pyrser/

Prepare package and documentation
=================================
Test everything builds correctly::

    python setup.py build_sphinx sdist

Uploading a new package to pypi
===============================
Don't forget to upgrade the package number or delete the package you want to
replace on pypi before running the following command::

    python setup.py sdist upload