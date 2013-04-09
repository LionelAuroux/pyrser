import unittest
from unittest import mock

from pyrser import meta


class TestCheckTypes(unittest.TestCase):
    def test_it_calls_function_without_annotation_normally(self):
        @meta.checktypes
        def f(a):
            return [1, 2, 3]
        self.assertEqual([1, 2, 3], f(0))

    def test_it_calls_function_with_non_type_annotation_normally(self):
        @meta.checktypes
        def f(a: (lambda x: 5 < x < 11)):
            return [1, 2, 3]
        self.assertEqual([1, 2, 3], f(0))

    def test_it_calls_function_with_type_annotation_normally(self):
        @meta.checktypes
        def f(a: int, *args: int, b: str, **kwargs: str) -> [int]:
            return [1, 2, 3]
        self.assertEqual([1, 2, 3], f(0, 1, b='', c=''))

    def test_it_raises_valueerror_for_incorrect_default_value_type(self):
        with self.assertRaises(ValueError):
            @meta.checktypes
            def f(a: int='9'):
                pass

    def test_it_raises_valueerror_for_incorrect_parameter_type(self):
        with self.assertRaises(ValueError):
            @meta.checktypes
            def f(a: int):
                pass
            f('')

    def test_it_raises_valueerror_for_incorrect_variadic_type(self):
        with self.assertRaises(ValueError):
            @meta.checktypes
            def f(*args: int):
                pass
            f(1, 2, '')

    def test_it_raises_valueerror_for_incorrect_variadic_keyword_type(self):
        with self.assertRaises(ValueError):
            @meta.checktypes
            def f(**kwargs: int):
                pass
            f(a=1, b=2, c='')

    def test_it_raises_valueerror_for_incorrect_return_type(self):
        with self.assertRaises(ValueError):
            @meta.checktypes
            def f() -> int:
                return ''
            f()


class TestAddMethod(unittest.TestCase):
    def test_it_attach_method_to_class(self):
        class cls:
            pass
        method = mock.Mock(__name__='method', __doc__='doc string')
        meta.add_method(cls)(method)
        self.assertIs(method, cls.method)

    def test_it_does_not_attach_method_if_attribute_exists(self):
        class cls:
            def method(self):
                pass
        method = mock.Mock(__name__='method')
        with self.assertRaises(AttributeError):
            meta.add_method(cls)(method)


class TestHook(unittest.TestCase):
    def test_it_attach_method_as_hook_to_class(self):
        hooks = {}
        cls = mock.Mock(__name__='cls', _hooks=hooks)
        del cls.fn
        fn = mock.Mock(__name__='fn')
        meta.hook(cls)(fn)
        self.assertIs(fn, cls.fn)
        cls.set_one.assert_call_once_with(hooks, 'cls.fn', fn)

    def test_it_attach_method_as_hook_to_class_with_rulename(self):
        hooks = {}
        cls = mock.Mock(__name__='cls', _hooks=hooks)
        del cls.fn
        fn = mock.Mock(__name__='fn')
        meta.hook(cls, 'hookname')(fn)
        self.assertIs(fn, cls.fn)
        cls.set_one.assert_call_once_with(hooks, 'cls.hookname', fn)

    def test_it_does_not_attach_a_hook_if_method_already_exist(self):
        cls = mock.Mock(__name__='cls')
        method = mock.Mock(__name__='method')
        with self.assertRaises(AttributeError):
            meta.hook(cls, 'rulename')(method)


class TestRule(unittest.TestCase):
    def test_it_attach_method_as_rule_to_class(self):
        functioname = mock.Mock(__name__='functioname')
        cls = mock.Mock(**{'set_one.return_value': functioname,
                           '_rules': {}, '__name__': 'classname'})
        del cls.functioname
        meta.rule(cls)(functioname)
        self.assertIs(functioname, cls.functioname)
        cls.set_one.assert_call_once_with(
            cls._rules, 'functioname', functioname)

    def test_it_attach_method_as_rule_to_class_with_rulename(self):
        method = mock.Mock(__name__='method')
        cls = mock.Mock(**{'set_one.return_value': method,
                           '_rules': {'rulename': 42},
                           '__name__': 'classname'})
        del cls.method
        meta.rule(cls, 'rulename')(method)
        self.assertIs(method, cls.method)
        cls.set_one.assert_call_once_with(42, 'method', method)

    def test_it_does_not_attach_a_rule_if_method_already_exist(self):
        class cls:
            _rules = {}

            def method(self):
                pass

        method = mock.Mock(__name__='method')
        with self.assertRaises(AttributeError):
            meta.rule(cls, 'rulename')(method)
