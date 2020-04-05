#!/bin/bash
sudo -u www-data touch tests.log
sudo -u www-data chmod 666 tests.log
sudo -u www-data coverage run --source=monavenirapi ./manage.py test 2>&1 > tests.log
sudo -u www-data coverage html
