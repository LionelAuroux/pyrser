import os
from os import path
import sys
import unittest

# Add parent directory in front of path to import pyrser and tests from sources
parent_dir = path.join(path.dirname(__file__), os.pardir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from tests import gen_dsl
from tests import grammar_basic
from tests import grammar_decorator
from tests import grammar_directive
from tests import grammar_file
from tests import hooks
from tests import psl
from tests import internal_dsl
from tests import internal_error
from tests import internal_fmt
from tests import internal_parse
from tests import unify


# Test cases in order
test_cases = (
    #gen_dsl.GenDsl_Test,
    grammar_basic.GrammarBasic_Test, #OK
    grammar_decorator.GrammarDecorator_Test, #OK
    grammar_directive.GrammarDirective_Test, #OK
    #grammar_file.GrammarFile_Test,
    hooks.Hooks_Test, #OK
    psl.PSL_Test, #OK
    internal_dsl.InternalDsl_Test, #OK
    internal_error.InternalError_Test, #OK
    internal_fmt.InternalFmt_Test, #OK
    internal_parse.InternalParse_Test, #OK
    unify.Unifying_Test, #OK
)


def load_tests(loader, standard_tests, pattern):
    loader = unittest.defaultTestLoader
    if test_unit:
        suite = loader.discover(parent_dir)
    else:
        suite = unittest.TestSuite()

    if test_integration:
        for test_case in test_cases:
            tests = loader.loadTestsFromTestCase(test_case)
            suite.addTests(tests)
    return suite

if __name__ == '__main__':
    test_unit, test_integration = False, True
    if 'all' in sys.argv[1:]:
        test_unit = True
        sys.argv.remove('all')
    elif 'unit' in sys.argv[1:]:
        test_integration, test_unit = test_unit, test_integration
        sys.argv.remove('unit')
    unittest.main()
