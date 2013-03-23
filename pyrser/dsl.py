from pyrser import parsing
from pyrser import meta
from pyrser.parsing.node import Node

class Parser(parsing.Parser):
    """Basic class for BNF DSL PARSING."""
    def parse(self, text: str) -> parsing.Node:
        return self.evalRule('bnf_dsl')

    def __init__(self, stream=''):
        super().__init__(stream)
        #TODO(iopi): allow comment, so ignoreCxx
        self.setRules({
            #
            # bnf_dsl ::= [rule: r #add_rules(bnf_dsl, r) ]+ Base.eof
            # ;
            #
            'bnf_dsl':  parsing.Seq(
                            parsing.CallTrue(print, "HERE0"),
                            parsing.Rep1N(parsing.Seq(
                                parsing.Capture("r", parsing.Rule('rule')),
                                parsing.Hook('add_rules', [("bnf_dsl", Node), ("r", Node)])
                                )
                            ),
                            parsing.Rule('Base.eof')
                        ),

            #
            # rule ::= ns_name : rn "::=" alternatives : alts #add_rule(rule, rn, alts) ';'
            # ;
            #
            'rule': parsing.Seq(
                        parsing.Capture("rn", parsing.Rule('ns_name')),
                        parsing.Call(parsing.Parser.readText, "::="),
                        parsing.Capture("alts", parsing.Rule('alternatives')),
                        parsing.Hook('add_rule', [("rule", Node), ("rn", Node), ("alts", Node)]),
                        parsing.Call(parsing.Parser.readChar, ';')
                    ),

            #
            # alternatives ::= sequences : alt #add_alt(alternatives, alt)
            #                   ['|' sequences : alt #add_alt(alternatives, alt) ]*
            # ;
            #
            'alternatives': parsing.Seq(
                                parsing.Capture('alt', parsing.Rule('sequences')),
                                parsing.Hook('add_alt', [("alternatives", Node), ("alt", Node)]),
                                parsing.Rep0N(
                                    parsing.Seq(
                                        parsing.Call(parsing.Parser.readChar, '|'),
                                        parsing.Capture('alt', parsing.Rule('sequences')),
                                        parsing.Hook('add_alt', [("alternatives", Node), ("alt", Node)])
                                    )
                                )
                            ),

            #
            # sequences ::= [ sequence : cla #add_sequences(sequences, cla) ]+
            #;
            #
            'sequences':  parsing.Rep1N(
                            parsing.Seq(
                                parsing.Capture('cla', parsing.Rule('sequence')),
                                parsing.Hook('add_sequences', [("sequences", Node), ("cla", Node)])
                            )
                        ),

            #
            # sequence ::= [
            #               ns_name : rid #add_ruleclause_name(sequence, rid)
            #               | Base.string : txt #add_text(sequence, txt)
            #               | Base.char : begin ".." Base.char : end #add_range(sequence, begin, end)
            #               | Base.char : c #add_char(sequence, c)
            #               | '[' alternatives : subsequence ']'  #add_subsequence(sequence, subsequence)
            #            ]
            #           [repeat : rpt #add_rpt(sequence, rpt) ]?
            #           [':' Base.id : cpt #add_capture(sequence, cpt) ]?
            #           | hook : h #add_hook(sequence, h)
            #           | directive : d sequence : s #add_directive(sequence, d, s)
            # ;
            #
            'sequence':   parsing.Alt(
                            parsing.Seq(
                                parsing.Alt(
                                    parsing.Seq(
                                            parsing.Capture('rid', parsing.Rule('ns_name')), 
                                            parsing.Hook('add_ruleclause_name', [("sequence", Node), ("rid", Node)])
                                        ),
                                    parsing.Seq(
                                            parsing.Capture('txt', parsing.Rule('Base.string')), 
                                            parsing.Hook('add_text', [("sequence", Node), ("txt", Node)])
                                        ),
                                    parsing.Seq(
                                        parsing.Capture('begin', parsing.Rule('Base.char')),
                                        parsing.Call(parsing.Parser.readText, ".."),
                                        parsing.Capture('end', parsing.Rule('Base.char')),
                                        parsing.Hook('add_range', [("sequence", Node), ("begin", Node), ("end", Node)])
                                    ),
                                    parsing.Seq(
                                        parsing.Capture('c', parsing.Rule('Base.char')), 
                                        parsing.Hook('add_char', [("sequence", Node), ("c", Node)])
                                    ),
                                    parsing.Seq(
                                        parsing.Call(parsing.Parser.readChar, "["),
                                        parsing.Capture('subsequence', parsing.Rule('alternatives')), 
                                        parsing.Call(parsing.Parser.readChar, "]"),
                                        parsing.Hook('add_subsequence', [("sequence", Node), ("subsequence", Node)]),
                                    )
                                ),
                                parsing.RepOptional(
                                    parsing.Seq(
                                        parsing.Capture('rpt', parsing.Rule('repeat')),
                                        parsing.Hook('add_rpt', [("sequence", Node), ("rpt", Node)])
                                    )
                                ),
                                parsing.RepOptional(
                                    parsing.Seq(
                                        parsing.Call(parsing.Parser.readText, ":"),
                                        parsing.Capture('cpt', parsing.Rule('Base.id')),
                                        parsing.Hook('add_capture', [('sequence', Node), ('cpt', Node)])
                                    )
                                )
                            ),
                            parsing.Seq(
                                parsing.Capture('h', parsing.Rule('hook')),
                                parsing.Hook('add_hook', [('sequence', Node), ('h', Node)])
                            ),
                            parsing.Seq(
                                parsing.Capture('d', parsing.Rule('directive')),
                                parsing.Capture('s', parsing.Rule('sequence')),
                                parsing.Hook('add_directive', [('sequence', Node), ('d', Node), ('s', Node)])
                            )
                        ),

            # TODO: add directive hooks
            # ns_name ::= @ignore("null") [ Base.id ['.' Base.id]* ]: rid #add_ruleclause_name(ns_name, rid)
            # ;
            #
            'ns_name':  parsing.Seq(
                            parsing.Capture('rid',
                                parsing.Scope(
                                    parsing.Call(parsing.Parser.pushIgnore, parsing.Parser.ignore_null),
                                    parsing.Call(parsing.Parser.popIgnore),
                                    parsing.Seq(
                                        parsing.Rule('Base.id'),
                                        parsing.Rep0N(
                                            parsing.Seq(
                                                parsing.Call(parsing.Parser.readText, "."),
                                                parsing.Rule('Base.id')
                                            )
                                        )
                                    )
                                )
                            ), 
                            parsing.Hook('add_ruleclause_name', [("ns_name", Node), ("rid", Node)])
                        ),

            #
            # repeat ::= '?' #add_optional(repeat) | '*' #add_0N(repeat) | '+' #add_1N(repeat)
            # ;
            #
            'repeat':   parsing.Alt(
                            parsing.Seq(
                                parsing.Call(parsing.Parser.readChar, '?'),
                                parsing.Hook('add_optional', [("repeat", Node)])
                            ),
                            parsing.Seq(
                                parsing.Call(parsing.Parser.readChar, '*'),
                                parsing.Hook('add_0N', [("repeat", Node)])
                            ),
                            parsing.Seq(
                                parsing.Call(parsing.Parser.readChar, '+'),
                                parsing.Hook('add_1N', [("repeat", Node)])
                            ),
                        ),

            #
            # hook ::= '#' ns_name : n #hook_name(hook, n) ['(' param : p #hook_param(hook, p) [',' param : p #hook_param(hook, p)]* ')']?
            # ;
            #
            'hook': parsing.Seq(
                        parsing.Call(parsing.Parser.readChar, '#'),
                        parsing.Capture('n', parsing.Rule('ns_name')),
                        parsing.Hook('hook_name', [('hook', Node), ('n', Node)]),
                        parsing.RepOptional(
                            parsing.Seq(
                                parsing.Call(parsing.Parser.readChar, '('),
                                parsing.Capture('p', parsing.Rule('param')),
                                parsing.Hook('hook_param', [('hook', Node), ('p', Node)]),
                                parsing.Rep0N(
                                    parsing.Seq(
                                        parsing.Call(parsing.Parser.readChar, ','),
                                        parsing.Capture('p', parsing.Rule('param')),
                                        parsing.Hook('hook_param', [('hook', Node), ('p', Node)]),
                                    )
                                ),
                                parsing.Call(parsing.Parser.readChar, ')')
                            )
                        ),
                    ),

            #
            # directive ::= '@' ns_name : n #hook_name(directive, n) ['(' param : p #hook_param(directive, p) [',' param : p #hook_param(directive, p)]* ')']?
            # ;
            'directive':    parsing.Seq(
                                parsing.CallTrue(print, "HERE"),
                                parsing.Call(parsing.Parser.readChar, '@'),
                                parsing.CallTrue(print, "HERE"),
                                parsing.Capture('n', parsing.Rule('ns_name')),
                                parsing.Hook('hook_name', [('directive', Node), ('n', Node)]),
                                parsing.RepOptional(
                                    parsing.Seq(
                                        parsing.Call(parsing.Parser.readChar, '('),
                                        parsing.Capture('p', parsing.Rule('param')),
                                        parsing.Hook('hook_param', [('directive', Node), ('p', Node)]),
                                        parsing.Rep0N(
                                            parsing.Seq(
                                                parsing.Call(parsing.Parser.readChar, ','),
                                                parsing.Capture('p', parsing.Rule('param')),
                                                parsing.Hook('hook_param', [('directive', Node), ('p', Node)]),
                                            )
                                        ),
                                        parsing.Call(parsing.Parser.readChar, ')')
                                    )
                                ),
                            ),

            #
            # param ::= Base.num :n #param_num(param, n) | Base.string : s #param_str(param, s) | Base.char : c #param_str(param, c) | Base.id : i #param_id(param, i)
            # ;
            #
            'param' : parsing.Alt(
                        parsing.Seq(
                            parsing.Capture('n', parsing.Rule('Base.num')),
                            parsing.Hook('param_num', [('param', Node), ('n', Node)])
                        ),
                        parsing.Seq(
                            parsing.Capture('s', parsing.Rule('Base.string')),
                            parsing.Hook('param_str', [('param', Node), ('s', Node)])
                        ),
                        parsing.Seq(
                            parsing.Capture('c', parsing.Rule('Base.char')),
                            parsing.Hook('param_str', [('param', Node), ('c', Node)])
                        ),
                        parsing.Seq(
                            parsing.Capture('i', parsing.Rule('Base.id')),
                            parsing.Hook('param_id', [('param', Node), ('i', Node)])
                        ),
                    ),
        })


@meta.hook(Parser)
def add_ruleclause_name(self, ns_name, rid) -> bool:
    ns_name.value = rid.value
    ns_name.parser_tree = parsing.Rule(ns_name.value)
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
def add_sequences(self, sequences, cla) -> bool:
    if not hasattr(sequences, 'parser_tree'):
        # forward sublevel of sequence as is
        sequences.parser_tree = cla.parser_tree
    else:
        oldnode = sequences
        if isinstance(oldnode.parser_tree, parsing.Seq):
            oldpt = list(oldnode.parser_tree.ptlist)
        else:
            oldpt = [oldnode.parser_tree]
        oldpt.append(cla.parser_tree)
        sequences.parser_tree = parsing.Seq(*tuple(oldpt))
    return True

@meta.hook(Parser)
def add_alt(self, alternatives, alt) -> bool:
    if not hasattr(alternatives, 'parser_tree'):
        # forward sublevel of alt as is
        if hasattr(alt, 'parser_tree'):
            alternatives.parser_tree = alt.parser_tree
        else:
            alternatives.parser_tree = alt
    else:
        oldnode = alternatives
        if isinstance(oldnode.parser_tree, parsing.Alt):
            oldpt = list(oldnode.parser_tree.ptlist)
        else:
            oldpt = [oldnode.parser_tree]
        oldpt.append(alt.parser_tree)
        alternatives.parser_tree = parsing.Alt(*tuple(oldpt))
    return True

@meta.hook(Parser)
def add_char(self, sequence, c):
    sequence.parser_tree = parsing.Call(parsing.Parser.readChar, c.value)
    return True

@meta.hook(Parser)
def add_text(self, sequence, txt):
    sequence.parser_tree = parsing.Call(parsing.Parser.readText, txt.value)
    return True

@meta.hook(Parser)
def add_range(self, sequence, begin, end):
    sequence.parser_tree = parsing.Call(parsing.Parser.readRange, begin.value, end.value)
    return True

@meta.hook(Parser)
def add_rpt(self, sequence, pt):
    oldnode = sequence
    sequence.parser_tree = pt.functor(oldnode.parser_tree)
    return True

@meta.hook(Parser)
def add_capture(self, sequence, cpt):
    sequence.parser_tree = parsing.Capture(cpt.value, sequence.parser_tree)
    return True

@meta.hook(Parser)
def add_subsequence(self, sequence, subsequence):
    sequence.parser_tree = subsequence.parser_tree
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

@meta.hook(Parser)
def add_hook(self, sequence, h):
    sequence.parser_tree = parsing.Hook(h.name, h.listparam)
    return True

@meta.hook(Parser)
def param_num(self, param, n):
    param.pair = (int(n.value), int)
    return True

@meta.hook(Parser)
def param_str(self, param, s):
    param.pair = (s.value, str)
    return True

@meta.hook(Parser)
def param_id(self, param, i):
    param.pair = (i.value, Node)
    return True

@meta.hook(Parser)
def hook_name(self, hook, n):
    print("HOOK_NAME %s" % n.value)
    hook.name = n.value
    hook.listparam = []
    return True

@meta.hook(Parser)
def hook_param(self, hook, p):
    hook.listparam.append(p.pair)
    return True

@meta.hook(Parser)
def add_directive(self, sequence, d, s):
    print("ADD DIRECTIVE")
    sequence.parser_tree = parsing.Directive()
    return True
