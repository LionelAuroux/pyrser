from pyrser.parsing.python.parserBase import *

### obsolete
def to_str(thing):
    if isinstance(thing, dict):
        return "{%s}" % (", ".join(["%s = %s" % (k, to_str(v)) for k, v in thing.items()]))
    return "not implemented"

class   ParserDsl(ParserBase):
    """
    Basic class for BNF DSL PARSING
    """

    def add_rule_name(self, ctx) -> bool:
        rule_name = Node()
        rule_name.value = ctx['rid'].value
        rule_name.parser_tree = Rule(self, rule_name.value)
        ctx['rule_name'] = rule_name
        return True

    def add_clause_name(self, ctx) -> bool:
        rule_name = Node()
        rule_name.value = ctx['rid'].value
        rule_name.parser_tree = Rule(self, rule_name.value)
        ctx['clause'] = rule_name
        return True

    def add_rules(self, ctx) -> bool:
        r = ctx['r']
        if 'bnf_dsl' not in ctx:
            ctx['bnf_dsl'] = Node()
        ctx['bnf_dsl'][r.rulename] = r.parser_tree
        return True

    def add_rule(self, ctx) -> bool:
        ctx['rule'] = Node()
        ctx['rule'].rulename = ctx['rn'].value
        ctx['rule'].parser_tree = ctx['alts'].parser_tree
        return True

    def add_clause(self, ctx) -> bool:
        ctx['clauses'] = Node()
        ctx['clauses'].parser_tree = Clauses(self, ctx['cla'].parser_tree)
        return True

    def add_clauses(self, ctx) -> bool:
        cla = ctx['cla']
        if 'clauses' not in ctx:
            ctx['clauses'] = Node()
            ctx['clauses'].parser_tree = cla.parser_tree
        else:
            oldnode = ctx['clauses']
            if isinstance(oldnode.parser_tree, Clauses):
                oldpt = list(oldnode.parser_tree.clauses)
            else:
                oldpt = [oldnode.parser_tree]
            oldpt.append(cla.parser_tree)
            ctx['clauses'].parser_tree = Clauses(self, *tuple(oldpt))
        return True

    def add_alt(self, ctx) -> bool:
        alt = ctx['alt']
        if 'alternatives' not in ctx:
            ctx['alternatives'] = Node()
            ctx['alternatives'].parser_tree = alt.parser_tree
        else:
            oldnode = ctx['alternatives']
            if isinstance(oldnode.parser_tree, Alt):
                oldpt = list(oldnode.parser_tree.clauses)
            else:
                oldpt = [oldnode.parser_tree]
            oldpt.append(alt.parser_tree)
            ctx['alternatives'].parser_tree = Alt(self, *tuple(oldpt))
        return True

    def add_char(self, ctx):
        ctx['clause'] = Node()
        ctx['clause'].parser_tree = Call(self.readChar, ctx['c'].value)
        return True

    def add_text(self, ctx):
        ctx['clause'] = Node()
        ctx['clause'].parser_tree = Call(self.readText, ctx['str'].value)
        return True

    def add_range(self, ctx):
        ctx['clause'] = Node()
        ctx['clause'].parser_tree = Call(self.readRange, ctx['begin'].value, ctx['end'].value)
        return True

    def __init__(self, sStream = ""):
        ParserBase.__init__(self, sStream)
        # TODO: allow comment, so ignoreCxx
        self.setRules({
            #
            # bnf_dsl ::= [rule : r #add_rules]+ Base::eof
            # ;
            #
            'bnf_dsl' : Clauses(self, 
                            Rep1N(self, Clauses(self, 
                                Capture(self, "r", Rule(self, 'rule')), 
                                Hook(self, 'add_rules'))
                            ),
                            Rule(self, 'Base::eof')
                        ),

            #
            # rule ::= rule_name : rn "::=" alternatives : alts #add_rule ';'
            # ;
            #
            'rule' : Clauses(self, 
                        Capture(self, "rn", Rule(self, 'rule_name')), 
                        Call(self.readText, "::="), 
                        Capture(self, "alts", Rule(self, 'alternatives')), 
                        Hook(self, 'add_rule'), 
                        Call(self.readChar, ';')
                    ),

            #
            # alternatives ::= clauses : alt #add_alt ['|' clauses : alt #add_alt ]*
            # ;
            #
            'alternatives' : Clauses(self, 
                            Capture(self, 'alt', Rule(self, 'clauses')),
                            Hook(self, 'add_alt'),
                            Rep0N(self,
                                Clauses(self,
                                    Call(self.readChar, '|'),
                                    Capture(self, 'alt', Rule(self, 'clauses')),
                                    Hook(self, 'add_alt')
                                )
                            )
                        ),

            #
            # clauses ::= [ clause : cla #add_clauses ]+ //| hook
            #;
            #
            'clauses' : Rep1N(self, 
                            Clauses(self, 
                                Capture(self, 'cla', Rule(self, 'clause')),
                                Hook(self, 'add_clauses')
                            )
                        ),
            #
            # clause ::= Base::id : rid #add_clause_name
            #           | Base::string : str #add_text
            #           | Base::char : begin ".." Base::char : end #add_range
            #           | Base::char : c #add_char
            # ;
            #
            'clause' : Alt(self,
                            Clauses(self, Capture(self, 'rid', Rule(self, 'Base::id')), Hook(self, 'add_clause_name')),
                            Clauses(self, Capture(self, 'str', Rule(self, 'Base::string')), Hook(self, 'add_text')),
                            Clauses(self, 
                                Capture(self, 'begin', Rule(self, 'Base::char')),
                                Call(self.readText, ".."),
                                Capture(self, 'end', Rule(self, 'Base::char')),
                                Hook(self, 'add_range')
                            ),
                            Clauses(self, Capture(self, 'c', Rule(self, 'Base::char')), Hook(self, 'add_char'))
                        ),

            #
            # rule_name ::= Base::id : rid #add_rule_name
            # ;
            #
            'rule_name' : Clauses(self, Capture(self, 'rid', Rule(self, 'Base::id')), Hook(self, 'add_rule_name')),
        })
        
        self.setHooks({
            'add_rule_name' : self.add_rule_name,
            'add_rules' : self.add_rules,
            'add_rule' : self.add_rule,
            'add_clause' : self.add_clause,
            'add_clause_name' : self.add_clause_name,
            'add_clauses' : self.add_clauses,
            'add_alt' : self.add_alt,
            'add_text' : self.add_text,
            'add_range' : self.add_range,
            'add_char' : self.add_char
        })

