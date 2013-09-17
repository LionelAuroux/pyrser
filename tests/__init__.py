#import unittest
#
#from tests import internal_parse
#from tests import internal_dsl
#from tests import grammar_basic
#
#
## Use cases in order
#use_cases = (
#    internal_parse.InternalParse_Test,
#    internal_dsl.InternalDsl_Test,
#    grammar_basic.GrammarBasic_Test
#)
#
#
#def load_tests(loader, standard_tests, pattern):
#    standard_tests.addTest(loader.discover('tests/pyrser'))
#    for use_case in use_cases:
#        tests = loader.loadTestsFromTestCase(use_case)
#        standard_tests.addTests(tests)
#    return standard_tests
