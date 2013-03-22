from pyrser import dsl
from pyrser import parsing


class MetaGrammar(type):
    """Metaclass for all grammars."""
    def __new__(metacls, name, bases, namespace):
        cls = type.__new__(metacls, name, bases, namespace)
        rules = {}
        for base in reversed(bases):
            rules.update(getattr(base, 'rules', {}))
        grammar = namespace.get('grammar')
        if grammar is not None:
            parser = cls.dsl_parser(grammar)
            rules.update(parser.parse())
        cls.rules = rules
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
        parser = parsing.Parser(source)
        parser.setRules(self.rules)
        return parser.evalRule(self.entry)
