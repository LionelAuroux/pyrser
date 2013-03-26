from pyrser import dsl
from pyrser import parsing


class MetaGrammar(parsing.MetaBasicParser):
    """Metaclass for all grammars."""
    def __new__(metacls, name, bases, namespace):
        cls = parsing.MetaBasicParser.__new__(metacls, name, bases, namespace)
        grammar = namespace.get('grammar')
        if grammar is not None:
            dsl_object = cls.dsl_parser(grammar)
            cls._rules.new_child()
            cls._rules.update(dsl_object.get_rules())
        return cls

class Grammar(parsing.Parser, metaclass=MetaGrammar):
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
    dsl_parser = dsl.EBNF

    def __init__(self):
        if getattr(self, 'entry', None) is None:
            raise ValueError("No entry rule name defined for {}".format(
                self.__class__.__name__))

    def parse(self, source):
        """Parse the grammar"""
        parser = self.dsl_parser(source)
        parser.set_rules(self._rules)
        return parser.eval_rule(self.entry)
