# Copyright (C) 2012 Candiotti Adrien
# Copyright (C) 2013 Pascal Bertrand
# Copyright (C) 2013 Lionel Auroux
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest


def load_tests(loader, standard_tests, pattern):
    loader, suite = unittest.defaultTestLoader, unittest.TestSuite()
    for test_case in test_cases:
        tests = loader.loadTestsFromTestCase(test_case)
        suite.addTests(tests)
    return suite


if __name__ == '__main__':
    import os
    import sys
    from os import path
    # Add parent directory in front of path to import pyrser from sources
    sys.path.insert(0,
        path.abspath(path.join(path.dirname(__file__), os.pardir)))

    import internal_parse
    import internal_dsl
    import capture
    import no_depth_generation
    import multi_generation
    import rule_directives
    import composition
    import inheritance
    import hooks

    # Test cases in order
    test_cases = (
        internal_parse.InternalParse_Test,
        internal_dsl.InternalDsl_Test,
        #capture.Capture_Test,
        #no_depth_generation.generatedCode,
        #multi_generation.generatedCode,
        #rule_directives.generatedCode,
        #composition.generatedCode,
        #inheritance.generatedCode,
        #hooks.GenericHookTests,
    )


    unittest.main(failfast=True)
