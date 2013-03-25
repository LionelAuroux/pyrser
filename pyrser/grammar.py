from pyrser import dsl
from pyrser import parsing


class MetaGrammar(type):
    """Metaclass for all grammars."""
    def __new__(metacls, name, bases, namespace):
        cls = type.__new__(metacls, name, bases, namespace)
        grammar = namespace.get('grammar')
        cls._rules = {}
        if grammar is not None:
            cls._rules = cls.dsl_parser(grammar)
        return cls


class Grammar(metaclass=MetaGrammar):
    """
    Base class for all grammars.

    This class turn any class A that inherit it into a grammar.
    Taking the description of the grammar in parameter it will add
    all what is what is needed for A to parse it.
    """
    # Text grammar to generate parsing rules for this class.
    grammar = None
    # Name of the default rule to parse the grammar.
    entry = None
    # DSL parsing class
    dsl_parser = dsl.Parser

    def __init__(self):
        if getattr(self, 'entry', None) is None:
            raise ValueError("No entry rule name defined for {}".format(
                self.__class__.__name__))

    def parse(self, source):
        """Parse the grammar"""
        parser = self.__class__.dsl_parser(source)
        parser.set_rules(self.__class__._rules)
        return parser.eval_rule(self.__class__.entry)
