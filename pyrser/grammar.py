from pyrser import dsl
from pyrser import parsing


class MetaGrammar(type):
    """Metaclass for all grammars."""
    def __new__(metaclass, classname, bases, classdict):
        cls = type.__new__(metaclass, classname, bases, classdict)
        rules = {}
        for base in reversed(bases):
            rules.update(getattr(base, 'rules', {}))
        grammar = classdict.get('grammar')
        if grammar is not None:
            dsl_parser = dsl.Parser(grammar)
            rules.update(dsl_parser.evalRule('bnf_dsl'))
        cls.rules = rules
        return cls


class Grammar(metaclass=MetaGrammar):
    """
    Base class for all grammars.

    This class turn any class A that inherit it into a grammar.
    Taking the description of the grammar in parameter it will add
    all what is what is needed for A to parse it.
    """

    grammar = None
    entry = None

    def parse(self, source):
        """Parse the grammar"""
        if not hasattr(self, 'entry') or self.entry is None:
            raise Exception("No entry rule name defined for {}".format(
                self.__class__.__name__))
        parser = parsing.Parser(source)
        parser.setRules(self.rules)
        return parser.evalRule(self.entry)
