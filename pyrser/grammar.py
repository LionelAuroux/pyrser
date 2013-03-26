from pyrser import dsl
from pyrser import parsing


class MetaGrammar(parsing.MetaBasicParser):
    """Metaclass for all grammars."""
    def __new__(metacls, name, bases, namespace):
        import collections
        #cls = parsing.MetaBasicParser.__new__(metacls, name, bases, namespace)
        if '_MetaGrammar' not in globals():
            cls = type.__new__(metacls, name, bases, namespace)
            print("FIRST META %s" % id(cls))
            global _MetaGrammar
            _MetaGrammar = cls
        else:
            cls = globals()['_MetaGrammar']
        #global _MetaBasicParser
        #cls = _MetaBasicParser
        grammar = namespace.get('grammar')
        print("METAGRAMMAR %s!!!!" % cls.__name__)
        if grammar is not None:
            dsl_object = cls.dsl_parser(grammar)
            cls._rules.new_child()
            cls._rules.update(dsl_object.get_rules())
            print("from BasicParser %s" % id(parsing.Parser._hooks))
            #cls._hooks = parsing.Parser._hooks.new_child()
            cls._hooks = cls._hooks.new_child()
            print("CHILD name %s (%s)" % (cls.__name__, id(cls._hooks)))
            for ch in cls._hooks.maps:
                print("CHILD CH %d" % id(ch))
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
        if getattr(self, 'entry', None) is None and type(self) is not Grammar:
            raise ValueError("No entry rule name defined for {}".format(
                self.__class__.__name__))

    def parse(self, source):
        """Parse the grammar"""
        parser = self.__class__.dsl_parser(source)
        parser.__class__.set_rules(self.__class__._rules)
        print("ENTRY : %s" % self.__class__)
        return parser.eval_rule(self.__class__.entry)
