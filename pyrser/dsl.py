from pyrser import parsing
from pyrser import meta


class Parser(parsing.Parser):
    """Basic class for BNF DSL PARSING."""
    def __init__(self, stream=''):
        super().__init__(stream)
        #TODO(iopi): allow comment, so ignoreCxx
        self.setRules({
            #
            # bnf_dsl ::= [rule: r #add_rules(bnf_dsl, r) ]+ Base::eof
            # ;
            #
            'bnf_dsl': parsing.Clauses(
                parsing.Rep1N(
                    parsing.Clauses(
                        parsing.Capture('r', parsing.Rule('rule')),
                        parsing.Hook('add_rules',
                                     [('bnf_dsl', parsing.Node),
                                      ('r', parsing.Node)]))),
                parsing.Rule('Base::eof')),
            #
            # rule ::= rule_name: rn "::=" alternatives : alts
            #     #add_rule(rule, rn, alts) ';'
            # ;
            #
            'rule': parsing.Clauses(
                parsing.Capture('rn', parsing.Rule('rule_name')),
                parsing.Call(self.readText, '::='),
                parsing.Capture('alts',
                                parsing.Rule('alternatives')),
                parsing.Hook('add_rule',
                             [('rule', parsing.Node),
                              ('rn', parsing.Node),
                              ('alts', parsing.Node)]),
                parsing.Call(self.readChar, ';')),
            #
            # alternatives ::=
            #     clauses: alt #add_alt(alternatives, alt)
            #     ['|' clauses: alt #add_alt(alternatives, alt) ]*
            # ;
            #
            'alternatives': parsing.Clauses(
                parsing.Capture('alt', parsing.Rule('clauses')),
                parsing.Hook('add_alt', [('alternatives', parsing.Node),
                                         ('alt', parsing.Node)]),
                parsing.Rep0N(
                    parsing.Clauses(
                        parsing.Call(self.readChar, '|'),
                        parsing.Capture('alt', parsing.Rule('clauses')),
                        parsing.Hook('add_alt',
                                     [('alternatives', parsing.Node),
                                      ('alt', parsing.Node)])))),
            #
            # clauses ::= [ clause: cla #add_clauses(clauses, cla) ]+ //| hook
            # ;
            #
            #TODO(iopi): choose between _rule_node or $$ for the result value
            # of a rule
            'clauses': parsing.Capture(
                '$$',
                parsing.Rep1N(
                    parsing.Clauses(
                        parsing.Capture('cla',
                                        parsing.Rule('clause')),
                        parsing.Hook('add_clauses',
                                     [('clauses', parsing.Node),
                                      ('cla', parsing.Node)])))),
            #
            # clause ::= [
            #     Base::id: rid #add_ruleclause_name(clause, rid)
            #     | Base::string: txt #add_text(clause, txt)
            #     | Base::char: begin ".." Base::char : end
            #         #add_range(clause, begin, end)
            #     | Base::char: c #add_char(clause, c)
            #     | '[' alternatives: subclause ']'
            #         #add_subclause(clause, subclause)
            # ]
            # [repeat: rpt #add_rpt(clause, rpt) ]?
            # ;
            #
            'clause': parsing.Clauses(
                parsing.Alt(
                    parsing.Clauses(
                        parsing.Capture('rid',
                                        parsing.Rule('Base::id')),
                        parsing.Hook('add_ruleclause_name',
                                     [('clause', parsing.Node),
                                      ('rid', parsing.Node)])),
                    parsing.Clauses(
                        parsing.Capture('txt',
                                        parsing.Rule('Base::string')),
                        parsing.Hook('add_text',
                                     [('clause', parsing.Node),
                                      ('txt', parsing.Node)])),
                    parsing.Clauses(
                        parsing.Capture('begin',
                                        parsing.Rule('Base::char')),
                        parsing.Call(self.readText, '..'),
                        parsing.Capture('end',
                                        parsing.Rule('Base::char')),
                        parsing.Hook('add_range',
                                     [('clause', parsing.Node),
                                      ('begin', parsing.Node),
                                      ('end', parsing.Node)])),
                    parsing.Clauses(
                        parsing.Capture('c', parsing.Rule('Base::char')),
                        parsing.Hook('add_char',
                                     [('clause', parsing.Node),
                                      ('c', parsing.Node)])),
                    parsing.Clauses(
                        parsing.Call(self.readChar, '['),
                        parsing.Capture('subclause',
                                        parsing.Rule('alternatives')),
                        parsing.Call(self.readChar, ']'),
                        parsing.Hook('add_subclause',
                                     [('clause', parsing.Node),
                                      ('subclause', parsing.Node)]))),
                parsing.RepOptional(
                    parsing.Clauses(
                        parsing.Capture('rpt', parsing.Rule('repeat')),
                        parsing.Hook('add_rpt',
                                     [('clause', parsing.Node),
                                      ('rpt', parsing.Node)])))),
            #TODO(iopi): add rules hooks
            # rule_name ::= Base::id: rid #add_ruleclause_name(rule_name, rid)
            # ;
            #
            'rule_name': parsing.Clauses(
                parsing.Capture('rid', parsing.Rule('Base::id')),
                parsing.Hook('add_ruleclause_name',
                             [('rule_name', parsing.Node),
                              ('rid', parsing.Node)])),
            #
            # repeat ::= '?' #add_optional(repeat)
            #     | '*' #add_0N(repeat)
            #     | '+' #add_1N(repeat)
            # ;
            #
            'repeat': parsing.Alt(
                parsing.Clauses(
                    parsing.Call(self.readChar, '?'),
                    parsing.Hook('add_optional', [('repeat', parsing.Node)])),
                parsing.Clauses(
                    parsing.Call(self.readChar, '*'),
                    parsing.Hook('add_0N', [('repeat', parsing.Node)])),
                parsing.Clauses(
                    parsing.Call(self.readChar, '+'),
                    parsing.Hook('add_1N', [('repeat', parsing.Node)])),),
        })


@meta.hook(Parser)
def add_ruleclause_name(self, rule_name, rid) -> bool:
    rule_name.value = rid.value
    rule_name.parser_tree = parsing.Rule(rule_name.value)
    return True


@meta.hook(Parser)
def add_rules(self, bnf, r) -> bool:
    bnf[r.rulename] = r.parser_tree
    return True


@meta.hook(Parser)
def add_rule(self, rule, rn, alts) -> bool:
    rule.rulename = rn.value
    rule.parser_tree = alts.parser_tree
    return True


@meta.hook(Parser)
def add_clauses(self, clauses, cla) -> bool:
    # print("add clauses: %s" % cla.parser_tree)
    if not hasattr(clauses, 'parser_tree'):
        # forward sublevel of clause as is
        clauses.parser_tree = cla.parser_tree
    else:
        oldnode = clauses
        # print("OLDCLA %s" % oldnode.parser_tree)
        if isinstance(oldnode.parser_tree, parsing.Clauses):
            oldpt = list(oldnode.parser_tree.clauses)
        else:
            oldpt = [oldnode.parser_tree]
        oldpt.append(cla.parser_tree)
        clauses.parser_tree = parsing.Clauses(*tuple(oldpt))
    return True


@meta.hook(Parser)
def add_alt(self, alternatives, alt) -> bool:
    # print("add ALT %s" % alt.parser_tree)
    if not hasattr(alternatives, 'parser_tree'):
        # forward sublevel of alt as is
        if hasattr(alt, 'parser_tree'):
            alternatives.parser_tree = alt.parser_tree
        else:
            alternatives.parser_tree = alt
    else:
        oldnode = alternatives
        if isinstance(oldnode.parser_tree, parsing.Alt):
            oldpt = list(oldnode.parser_tree.clauses)
        else:
            oldpt = [oldnode.parser_tree]
        oldpt.append(alt.parser_tree)
        alternatives.parser_tree = parsing.Alt(*tuple(oldpt))
    return True


@meta.hook(Parser)
def add_char(self, clause, c):
    clause.parser_tree = parsing.Call(self.readChar, c.value)
    return True


@meta.hook(Parser)
def add_text(self, clause, txt):
    clause.parser_tree = parsing.Call(self.readText, txt.value)
    return True


@meta.hook(Parser)
def add_range(self, clause, begin, end):
    clause.parser_tree = parsing.Call(self.readRange, begin.value, end.value)
    return True


@meta.hook(Parser)
def add_rpt(self, clause, pt):
    oldnode = clause
    clause.parser_tree = pt.functor(oldnode.parser_tree)
    return True


@meta.hook(Parser)
def add_subclause(self, clause, subclause):
    clause.parser_tree = subclause.parser_tree
    return True


@meta.hook(Parser)
def add_optional(self, repeat):
    repeat.functor = parsing.RepOptional
    return True


@meta.hook(Parser)
def add_0N(self, repeat):
    repeat.functor = parsing.Rep0N
    return True


@meta.hook(Parser)
def add_1N(self, repeat):
    repeat.functor = parsing.Rep1N
    return True
