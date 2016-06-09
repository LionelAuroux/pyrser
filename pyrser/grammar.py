from pyrser import dsl
from pyrser import parsing
from pyrser import meta
from pyrser import error
from collections import ChainMap


class MetaGrammar(parsing.MetaBasicParser):
    """Metaclass for all grammars."""
    def __new__(metacls, name, bases, namespace):
        # for multi heritance we have a simple inheritance relation
        # from the first class in declaration order.
        metabp = parsing.MetaBasicParser
        if len(bases) <= 1:
            cls = metabp.__new__(metacls, name, bases, namespace)
        else:
            b = tuple([bases[0]])
            cls = metabp.__new__(metacls, name, b, namespace)
        # lookup for the metaclass of parsing.
        # Grammar magically inherit rules&hooks from Parser
        if 'Parser' in parsing.base._MetaBasicParser:
            clsbase = parsing.base._MetaBasicParser['Parser']
            # link rules&hooks
            cls._rules = clsbase._rules.new_child()
            cls._hooks = clsbase._hooks.new_child()
            # add rules from DSL
            if 'grammar' in namespace and namespace['grammar'] is not None:
                sname = None
                if 'source' in namespace and namespace['source'] is not None:
                    sname = namespace['source']
                rules = cls.dsl_parser(namespace['grammar'], sname).get_rules()
                if not rules:
                    return rules
                # namespace rules with module/classe name
                for rule_name, rule_pt in rules.items():
                    if '.' not in rule_name:
                        rule_name = cls.__module__ \
                            + '.' + cls.__name__ \
                            + '.' + rule_name
                    meta.set_one(cls._rules, rule_name, rule_pt)
            # add localy define rules (and thus overloads)
            if '_rules' in namespace and namespace['_rules'] is not None:
                cls._rules.update(namespace['_rules'])
            # add localy define hooks
            if '_hooks' in namespace and namespace['_hooks'] is not None:
                cls._hooks.update(namespace['_hooks'])
        # Manage Aggregation
        if len(bases) > 1:
            aggreg_rules = ChainMap()
            aggreg_hooks = ChainMap()
            for subgrammar in bases:
                if hasattr(subgrammar, '_rules'):
                    aggreg_rules = ChainMap(*(aggreg_rules.maps
                                            + subgrammar._rules.maps))
                if hasattr(subgrammar, '_hooks'):
                    aggreg_hooks = ChainMap(*(aggreg_hooks.maps
                                            + subgrammar._hooks.maps))
            # aggregate at toplevel the branch grammar
            cls._rules = ChainMap(*(cls._rules.maps + aggreg_rules.maps))
            cls._hooks = ChainMap(*(cls._hooks.maps + aggreg_hooks.maps))
            # clean redondant in chain for rules
            orderedunique_rules = []
            tocpy_rules = set([id(_) for _ in cls._rules.maps])
            for ch in cls._rules.maps:
                idch = id(ch)
                if idch in tocpy_rules:
                    orderedunique_rules.append(ch)
                    tocpy_rules.remove(idch)
            cls._rules = ChainMap(*orderedunique_rules)
            # clean redondant in chain for hooks
            orderedunique_hooks = []
            tocpy_hooks = set([id(_) for _ in cls._hooks.maps])
            for ch in cls._hooks.maps:
                idch = id(ch)
                if idch in tocpy_hooks:
                    orderedunique_hooks.append(ch)
                    tocpy_hooks.remove(idch)
            cls._hooks = ChainMap(*orderedunique_hooks)
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

    def after_parse(self, node: parsing.Node) -> parsing.Node:
        """
        If you want to do some stuff after parsing, overload this...
        """
        return node

    def _do_parse(self, entry: str) -> parsing.Node:
        if self.nstream == 0:
            raise ValueError("No opened stream for reading."
                             + " Check if you provide something "
                             + "to read for method parse()"
                             + " or a correct file for method parse_file()"
                             )
        res = None
        self.diagnostic = error.Diagnostic()
        try:
            res = self.eval_rule(entry)
        except error.Diagnostic as d:
            # User put an error rule
            d.notify(
                error.Severity.ERROR,
                "Exception during the evaluation of '%s'" % self._lastRule,
                error.LocationInfo.from_stream(
                    self._stream,
                    is_error=self.from_string
                )
            )
            self.diagnostic = d
        if not res:
            # we fail to parse, but error is not set on the last rule
            self.diagnostic.notify(
                error.Severity.ERROR,
                "Parse error in '%s'" % self._lastRule,
                error.LocationInfo.from_maxstream(
                    self._stream,
                    is_error=self.from_string
                )
            )
            if self.raise_diagnostic:
                raise self.diagnostic
            else:
                return self
        # clear contexted variables
        self.rule_nodes.clear()
        # create a new Diagnostic object for the node result
        res.diagnostic = error.Diagnostic()
        # all is ok
        return self.after_parse(res)

    def parse(self, source: str=None, entry: str=None) -> parsing.Node:
        """Parse source using the grammar"""
        self.from_string = True
        if source is not None:
            self.parsed_stream(source)
        if entry is None:
            entry = self.entry
        if entry is None:
            raise ValueError("No entry rule name defined for {}".format(
                self.__class__.__name__))
        return self._do_parse(entry)

    def parse_file(self, filename: str, entry: str=None) -> parsing.Node:
        """Parse filename using the grammar"""
        self.from_string = False
        import os.path
        with open(filename, 'r') as f:
            self.parsed_stream(f.read(), os.path.abspath(filename))
        if entry is None:
            entry = self.entry
        if entry is None:
            raise ValueError("No entry rule name defined for {}".format(
                self.__class__.__name__))
        return self._do_parse(entry)


generated_class = 0


def build_grammar(inherit: tuple, scope: dict) -> Grammar:
    global generated_class
    class_name = "gen_class_" + str(generated_class)
    generated_class += 1
    return type(class_name, inherit, scope)


def from_string(bnf: str, entry=None, *optional_inherit) -> Grammar:
    """
    Create a Grammar from a string
    """
    inherit = [Grammar] + list(optional_inherit)
    scope = {'grammar': bnf, 'entry': entry}
    return build_grammar(tuple(inherit), scope)


def from_file(fn: str, entry=None, *optional_inherit) -> Grammar:
    """
    Create a Grammar from a file
    """
    import os.path
    if os.path.exists(fn):
        f = open(fn, 'r')
        bnf = f.read()
        f.close()
        inherit = [Grammar] + list(optional_inherit)
        scope = {'grammar': bnf, 'entry': entry, 'source': fn}
        return build_grammar(tuple(inherit), scope)
    raise Exception("File not Found!")
