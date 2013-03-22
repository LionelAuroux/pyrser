import unittest
try:
    from unittest import mock
except ImportError:
    import mock

from pyrser import meta


@unittest.skipIf(not hasattr(meta.inspect, 'signature'),
                 "python3.2 inspect module does not support signature")
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
        class cls:
            pass
        method = mock.Mock(__name__='method')
        meta.hook(cls)(method)
        self.assertIs(method, cls.method)
        self.assertIn('method', cls.class_hook_list)
        self.assertIs(method, cls.class_hook_list['method'])

    def test_it_attach_method_as_hook_to_class_with_rulename(self):
        class cls:
            pass
        method = mock.Mock(__name__='method')
        meta.hook(cls, 'hookname')(method)
        self.assertIs(method, cls.method)
        self.assertIn('hookname', cls.class_hook_list)
        self.assertIs(method, cls.class_hook_list['hookname'])

    def test_it_does_not_attach_a_hook_if_method_already_exist(self):
        class cls:
            def method(self):
                pass
        method = mock.Mock(__name__='method')
        with self.assertRaises(AttributeError):
            meta.hook(cls, 'rulename')(method)


class TestRule(unittest.TestCase):
    def test_it_attach_method_as_rule_to_class(self):
        class cls:
            pass
        method = mock.Mock(__name__='method')
        meta.rule(cls)(method)
        self.assertIs(method, cls.method)
        self.assertIn('method', cls.class_rule_list)
        self.assertIs(method, cls.class_rule_list['method'])

    def test_it_attach_method_as_rule_to_class_with_rulename(self):
        class cls:
            pass
        method = mock.Mock(__name__='method')
        meta.rule(cls, 'rulename')(method)
        self.assertIs(method, cls.method)
        self.assertIn('rulename', cls.class_rule_list)
        self.assertIs(method, cls.class_rule_list['rulename'])

    def test_it_does_not_attach_a_rule_if_method_already_exist(self):
        class cls:
            def method(self):
                pass
        method = mock.Mock(__name__='method')
        with self.assertRaises(AttributeError):
            meta.rule(cls, 'rulename')(method)
