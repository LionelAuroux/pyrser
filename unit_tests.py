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

# ------------------------------------------------------------------------------
# unit tests
# ------------------------------------------------------------------------

if __name__ == '__main__':

    import unittest
    from unit_tests.internal_parse import InternalParse_Test as _01
    from unit_tests.internal_dsl import InternalDsl_Test as _02
    #from unit_tests.capture import Capture_Test as _0X
    #from unit_tests.no_depth_generation import generatedCode as NoDepthGeneration
    #from unit_tests.multi_generation import generatedCode as MultiDepthGeneration
    #from unit_tests.rule_directives import generatedCode as RuleDirective
    #from unit_tests.composition import generatedCode as CompositionGeneration
    #from unit_tests.inheritance import generatedCode as InheritanceGeneration
    #from unit_tests.hooks import GenericHookTests

    unittest.main(failfast = True)
