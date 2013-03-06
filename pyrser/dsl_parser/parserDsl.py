# Copyright (C) 2013 Lionel Auroux
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from pyrser.parsing.python.parserBase import *
from pyrser import meta

### obsolete
def to_str(thing):
    if isinstance(thing, dict):
        return "{%s}" % (", ".join(["%s = %s" % (k, to_str(v)) for k, v in thing.items()]))
    return "not implemented"

class   ParserDsl(ParserBase):
    """
    Basic class for BNF DSL PARSING
    """
    def __init__(self, sStream = ""):
        ParserBase.__init__(self, sStream)
        # TODO: allow comment, so ignoreCxx
        self.setRules({
            #
            # bnf_dsl ::= [rule : r #add_rules(bnf_dsl, r) ]+ Base::eof
            # ;
            #
            'bnf_dsl' : Clauses(self, 
                            Rep1N(self, Clauses(self, 
                                Capture(self, "r", Rule(self, 'rule')), 
                                Hook(self, 'add_rules', [("bnf_dsl", Node), ("r", Node)]))
                            ),
                            Rule(self, 'Base::eof')
                        ),

            #
            # rule ::= rule_name : rn "::=" alternatives : alts #add_rule(rule, rn, alts) ';'
            # ;
            #
            'rule' : Clauses(self, 
                        Capture(self, "rn", Rule(self, 'rule_name')), 
                        Call(self.readText, "::="), 
                        Capture(self, "alts", Rule(self, 'alternatives')), 
                        Hook(self, 'add_rule', [("rule", Node), ("rn", Node), ("alts", Node)]), 
                        Call(self.readChar, ';')
                    ),

            #
            # alternatives ::= clauses : alt #add_alt(alternatives, alt) 
            #                   ['|' clauses : alt #add_alt(alternatives, alt) ]*
            # ;
            #
            'alternatives' : Clauses(self, 
                            Capture(self, 'alt', Rule(self, 'clauses')),
                            Hook(self, 'add_alt', [("alternatives", Node), ("alt", Node)]),
                            Rep0N(self,
                                Clauses(self,
                                    Call(self.readChar, '|'),
                                    Capture(self, 'alt', Rule(self, 'clauses')),
                                    Hook(self, 'add_alt', [("alternatives", Node), ("alt", Node)])
                                )
                            )
                        ),

            #
            # clauses ::= [ clause : cla #add_clauses(clauses, cla) ]+ //| hook
            #;
            #
            # TODO: choose between _rule_node or $$ for the result value of a rule
            'clauses' : Capture(self, '$$', 
                            Rep1N(self, 
                                Clauses(self, 
                                    Capture(self, 'cla', Rule(self, 'clause')),
                                    Hook(self, 'add_clauses', [("clauses", Node), ("cla", Node)])
                                )
                            )
                        ),

            #
            # clause ::= [
            #               Base::id : rid #add_ruleclause_name(clause, rid)
            #               | Base::string : txt #add_text(clause, txt)
            #               | Base::char : begin ".." Base::char : end #add_range(clause, begin, end)
            #               | Base::char : c #add_char(clause, c)
            #               | '[' alternatives : subclause ']'  #add_subclause(clause, subclause)
            #            ]
            #           [repeat : rpt #add_rpt(clause, rpt) ]?
            # ;
            #
            'clause' : Clauses(self,
                            Alt(self,
                                Clauses(self, 
                                        Capture(self, 'rid', Rule(self, 'Base::id')), 
                                        Hook(self, 'add_ruleclause_name', [("clause", Node), ("rid", Node)])
                                    ),
                                Clauses(self, 
                                        Capture(self, 'txt', Rule(self, 'Base::string')), 
                                        Hook(self, 'add_text', [("clause", Node), ("txt", Node)])
                                    ),
                                Clauses(self, 
                                    Capture(self, 'begin', Rule(self, 'Base::char')),
                                    Call(self.readText, ".."),
                                    Capture(self, 'end', Rule(self, 'Base::char')),
                                    Hook(self, 'add_range', [("clause", Node), ("begin", Node), ("end", Node)])
                                ),
                                Clauses(self, 
                                    Capture(self, 'c', Rule(self, 'Base::char')), 
                                    Hook(self, 'add_char', [("clause", Node), ("c", Node)])
                                ),
                                Clauses(self, 
                                    Call(self.readChar, "["),
                                    Capture(self, 'subclause', Rule(self, 'alternatives')), 
                                    Call(self.readChar, "]"),
                                    Hook(self, 'add_subclause', [("clause", Node), ("subclause", Node)]),
                                )
                            ),
                            RepOptional(self,
                                Clauses(self,
                                    Capture(self, 'rpt', Rule(self, 'repeat')),
                                    Hook(self, 'add_rpt', [("clause", Node), ("rpt", Node)])
                                )
                            )
                        ),

            # TODO: add rules hooks
            # rule_name ::= Base::id : rid #add_ruleclause_name(rule_name, rid)
            # ;
            #
            'rule_name' : Clauses(self, 
                            Capture(self, 'rid', Rule(self, 'Base::id')), 
                            Hook(self, 'add_ruleclause_name', [("rule_name", Node), ("rid", Node)])
                        ),
            #
            # repeat ::= '?' #add_optional(repeat) | '*' #add_0N(repeat) | '+' #add_1N(repeat)
            # ;
            #
            'repeat' : Alt(self,
                            Clauses(self, 
                                Call(self.readChar, '?'),
                                Hook(self, 'add_optional', [("repeat", Node)])
                            ),
                            Clauses(self, 
                                Call(self.readChar, '?*'),
                                Hook(self, 'add_0N', [("repeat", Node)])
                            ),
                            Clauses(self, 
                                Call(self.readChar, '+'),
                                Hook(self, 'add_1N', [("repeat", Node)])
                            ),
                        ),
        })
        

@meta.hook(ParserDsl)
def add_ruleclause_name(self, rule_name, rid) -> bool:
    rule_name.value = rid.value
    rule_name.parser_tree = Rule(self, rule_name.value)
    return True

@meta.hook(ParserDsl)
def add_rules(self, bnf, r) -> bool:
    bnf[r.rulename] = r.parser_tree
    return True

@meta.hook(ParserDsl)
def add_rule(self, rule, rn, alts) -> bool:
    rule.rulename = rn.value
    rule.parser_tree = alts.parser_tree
    return True

@meta.hook(ParserDsl)
def add_clauses(self, clauses, cla) -> bool:
    #print("add clauses: %s" % cla.parser_tree)
    if not hasattr(clauses, 'parser_tree'):
        # forward sublevel of clause as is
        clauses.parser_tree = cla.parser_tree
    else:
        oldnode = clauses
        #print("OLDCLA %s" % oldnode.parser_tree)
        if isinstance(oldnode.parser_tree, Clauses):
            oldpt = list(oldnode.parser_tree.clauses)
        else:
            oldpt = [oldnode.parser_tree]
        oldpt.append(cla.parser_tree)
        clauses.parser_tree = Clauses(self, *tuple(oldpt))
    return True

@meta.hook(ParserDsl)
def add_alt(self, alternatives, alt) -> bool:
    #print("add ALT %s" % alt.parser_tree)
    if not hasattr(alternatives, 'parser_tree'):
        # forward sublevel of alt as is
        if hasattr(alt, 'parser_tree'):
            alternatives.parser_tree = alt.parser_tree
        else:
            alternatives.parser_tree = alt
    else:
        oldnode = alternatives
        if isinstance(oldnode.parser_tree, Alt):
            oldpt = list(oldnode.parser_tree.clauses)
        else:
            oldpt = [oldnode.parser_tree]
        oldpt.append(alt.parser_tree)
        alternatives.parser_tree = Alt(self, *tuple(oldpt))
    return True

@meta.hook(ParserDsl)
def add_char(self, clause, c):
    clause.parser_tree = Call(self.readChar, c.value)
    return True

@meta.hook(ParserDsl)
def add_text(self, clause, txt):
    clause.parser_tree = Call(self.readText, txt.value)
    return True

@meta.hook(ParserDsl)
def add_range(self, clause, begin, end):
    clause.parser_tree = Call(self.readRange, begin.value, end.value)
    return True
