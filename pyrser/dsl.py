from pyrser import parsing
from pyrser import meta

class EBNF(parsing.Parser):
    """Basic class for BNF DSL PARSING."""
    def get_rules(self) -> parsing.Node:
        return self.eval_rule('bnf_dsl')

    def __init__(self, stream=''):
        super().__init__(stream)
        #TODO(iopi): allow comment, so ignoreCxx
        self.set_rules({
            #
            # bnf_dsl ::= [rule: r #add_rules(bnf_dsl, r) ]+ Base.eof
            # ;
            #
            'bnf_dsl':  parsing.Seq(
                            parsing.Rep1N(parsing.Seq(
                                parsing.Capture("r", parsing.Rule('rule')),
                                parsing.Hook('add_rules', [("bnf_dsl", parsing.Node), ("r", parsing.Node)])
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
                        parsing.Call(parsing.Parser.read_text, "::="),
                        parsing.Capture("alts", parsing.Rule('alternatives')),
                        parsing.Hook('add_rule', [("rule", parsing.Node), ("rn", parsing.Node), ("alts", parsing.Node)]),
                        parsing.Call(parsing.Parser.read_char, ';')
                    ),

            #
            # alternatives ::= sequences : alt #add_alt(alternatives, alt)
            #                   ['|' sequences : alt #add_alt(alternatives, alt) ]*
            # ;
            #
            'alternatives': parsing.Seq(
                                parsing.Capture('alt', parsing.Rule('sequences')),
                                parsing.Hook('add_alt', [("alternatives", parsing.Node), ("alt", parsing.Node)]),
                                parsing.Rep0N(
                                    parsing.Seq(
                                        parsing.Call(parsing.Parser.read_char, '|'),
                                        parsing.Capture('alt', parsing.Rule('sequences')),
                                        parsing.Hook('add_alt', [("alternatives", parsing.Node), ("alt", parsing.Node)])
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
                                parsing.Hook('add_sequences', [("sequences", parsing.Node), ("cla", parsing.Node)])
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
                                            parsing.Hook('add_ruleclause_name', [("sequence", parsing.Node), ("rid", parsing.Node)])
                                        ),
                                    parsing.Seq(
                                            parsing.Capture('txt', parsing.Rule('Base.string')), 
                                            parsing.Hook('add_text', [("sequence", parsing.Node), ("txt", parsing.Node)])
                                        ),
                                    parsing.Seq(
                                        parsing.Capture('begin', parsing.Rule('Base.char')),
                                        parsing.Call(parsing.Parser.read_text, ".."),
                                        parsing.Capture('end', parsing.Rule('Base.char')),
                                        parsing.Hook('add_range', [("sequence", parsing.Node), ("begin", parsing.Node), ("end", parsing.Node)])
                                    ),
                                    parsing.Seq(
                                        parsing.Capture('c', parsing.Rule('Base.char')), 
                                        parsing.Hook('add_char', [("sequence", parsing.Node), ("c", parsing.Node)])
                                    ),
                                    parsing.Seq(
                                        parsing.Call(parsing.Parser.read_char, "["),
                                        parsing.Capture('subsequence', parsing.Rule('alternatives')), 
                                        parsing.Call(parsing.Parser.read_char, "]"),
                                        parsing.Hook('add_subsequence', [("sequence", parsing.Node), ("subsequence", parsing.Node)]),
                                    )
                                ),
                                parsing.RepOptional(
                                    parsing.Seq(
                                        parsing.Capture('rpt', parsing.Rule('repeat')),
                                        parsing.Hook('add_rpt', [("sequence", parsing.Node), ("rpt", parsing.Node)])
                                    )
                                ),
                                parsing.RepOptional(
                                    parsing.Seq(
                                        parsing.Call(parsing.Parser.read_text, ":"),
                                        parsing.Capture('cpt', parsing.Rule('Base.id')),
                                        parsing.Hook('add_capture', [('sequence', parsing.Node), ('cpt', parsing.Node)])
                                    )
                                )
                            ),
                            parsing.Seq(
                                parsing.Capture('h', parsing.Rule('hook')),
                                parsing.Hook('add_hook', [('sequence', parsing.Node), ('h', parsing.Node)])
                            ),
                            parsing.Seq(
                                parsing.Capture('d', parsing.Rule('directive')),
                                parsing.Capture('s', parsing.Rule('sequence')),
                                parsing.Hook('add_directive', [('sequence', parsing.Node), ('d', parsing.Node), ('s', parsing.Node)])
                            )
                        ),

            # TODO: add directive hooks
            # ns_name ::= @ignore("null") [ Base.id ['.' Base.id]* ]: rid #add_ruleclause_name(ns_name, rid)
            # ;
            #
            'ns_name':  parsing.Seq(
                            parsing.Capture('rid',
                                parsing.Scope(
                                    parsing.Call(parsing.Parser.push_ignore, parsing.Parser.ignore_null),
                                    parsing.Call(parsing.Parser.pop_ignore),
                                    parsing.Seq(
                                        parsing.Rule('Base.id'),
                                        parsing.Rep0N(
                                            parsing.Seq(
                                                parsing.Call(parsing.Parser.read_text, "."),
                                                parsing.Rule('Base.id')
                                            )
                                        )
                                    )
                                )
                            ), 
                            parsing.Hook('add_ruleclause_name', [("ns_name", parsing.Node), ("rid", parsing.Node)])
                        ),

            #
            # repeat ::= '?' #add_optional(repeat) | '*' #add_0N(repeat) | '+' #add_1N(repeat)
            # ;
            #
            'repeat':   parsing.Alt(
                            parsing.Seq(
                                parsing.Call(parsing.Parser.read_char, '?'),
                                parsing.Hook('add_optional', [("repeat", parsing.Node)])
                            ),
                            parsing.Seq(
                                parsing.Call(parsing.Parser.read_char, '*'),
                                parsing.Hook('add_0N', [("repeat", parsing.Node)])
                            ),
                            parsing.Seq(
                                parsing.Call(parsing.Parser.read_char, '+'),
                                parsing.Hook('add_1N', [("repeat", parsing.Node)])
                            ),
                        ),

            #
            # hook ::= '#' ns_name : n #hook_name(hook, n) ['(' param : p #hook_param(hook, p) [',' param : p #hook_param(hook, p)]* ')']?
            # ;
            #
            'hook': parsing.Seq(
                        parsing.Call(parsing.Parser.read_char, '#'),
                        parsing.Capture('n', parsing.Rule('ns_name')),
                        parsing.Hook('hook_name', [('hook', parsing.Node), ('n', parsing.Node)]),
                        parsing.RepOptional(
                            parsing.Seq(
                                parsing.Call(parsing.Parser.read_char, '('),
                                parsing.Capture('p', parsing.Rule('param')),
                                parsing.Hook('hook_param', [('hook', parsing.Node), ('p', parsing.Node)]),
                                parsing.Rep0N(
                                    parsing.Seq(
                                        parsing.Call(parsing.Parser.read_char, ','),
                                        parsing.Capture('p', parsing.Rule('param')),
                                        parsing.Hook('hook_param', [('hook', parsing.Node), ('p', parsing.Node)]),
                                    )
                                ),
                                parsing.Call(parsing.Parser.read_char, ')')
                            )
                        ),
                    ),

            #
            # directive ::= '@' ns_name : n #hook_name(directive, n) ['(' param : p #hook_param(directive, p) [',' param : p #hook_param(directive, p)]* ')']?
            # ;
            'directive':    parsing.Seq(
                                parsing.Call(parsing.Parser.read_char, '@'),
                                parsing.Capture('n', parsing.Rule('ns_name')),
                                parsing.Hook('hook_name', [('directive', parsing.Node), ('n', parsing.Node)]),
                                parsing.RepOptional(
                                    parsing.Seq(
                                        parsing.Call(parsing.Parser.read_char, '('),
                                        parsing.Capture('p', parsing.Rule('param')),
                                        parsing.Hook('hook_param', [('directive', parsing.Node), ('p', parsing.Node)]),
                                        parsing.Rep0N(
                                            parsing.Seq(
                                                parsing.Call(parsing.Parser.read_char, ','),
                                                parsing.Capture('p', parsing.Rule('param')),
                                                parsing.Hook('hook_param', [('directive', parsing.Node), ('p', parsing.Node)]),
                                            )
                                        ),
                                        parsing.Call(parsing.Parser.read_char, ')')
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
                            parsing.Hook('param_num', [('param', parsing.Node), ('n', parsing.Node)])
                        ),
                        parsing.Seq(
                            parsing.Capture('s', parsing.Rule('Base.string')),
                            parsing.Hook('param_str', [('param', parsing.Node), ('s', parsing.Node)])
                        ),
                        parsing.Seq(
                            parsing.Capture('c', parsing.Rule('Base.char')),
                            parsing.Hook('param_str', [('param', parsing.Node), ('c', parsing.Node)])
                        ),
                        parsing.Seq(
                            parsing.Capture('i', parsing.Rule('Base.id')),
                            parsing.Hook('param_id', [('param', parsing.Node), ('i', parsing.Node)])
                        ),
                    ),
        })


@meta.hook(EBNF, "EBNF.add_ruleclause_name")
def add_ruleclause_name(self, ns_name, rid) -> bool:
    ns_name.value = rid.value
    ns_name.parser_tree = parsing.Rule(ns_name.value)
    return True

@meta.hook(EBNF, "EBNF.add_rules")
def add_rules(self, bnf, r) -> bool:
    bnf[r.rulename] = r.parser_tree
    return True

@meta.hook(EBNF, "EBNF.add_rule")
def add_rule(self, rule, rn, alts) -> bool:
    rule.rulename = rn.value
    rule.parser_tree = alts.parser_tree
    return True

@meta.hook(EBNF, "EBNF.add_sequences")
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

@meta.hook(EBNF, "EBNF.add_alt")
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

@meta.hook(EBNF, "EBNF.add_char")
def add_char(self, sequence, c):
    sequence.parser_tree = parsing.Call(parsing.Parser.read_char, c.value)
    return True

@meta.hook(EBNF, "EBNF.add_text")
def add_text(self, sequence, txt):
    sequence.parser_tree = parsing.Call(parsing.Parser.read_text, txt.value)
    return True

@meta.hook(EBNF, "EBNF.add_range")
def add_range(self, sequence, begin, end):
    sequence.parser_tree = parsing.Call(parsing.Parser.read_range, begin.value, end.value)
    return True

@meta.hook(EBNF, "EBNF.add_rpt")
def add_rpt(self, sequence, pt):
    oldnode = sequence
    sequence.parser_tree = pt.functor(oldnode.parser_tree)
    return True

@meta.hook(EBNF, "EBNF.add_capture")
def add_capture(self, sequence, cpt):
    sequence.parser_tree = parsing.Capture(cpt.value, sequence.parser_tree)
    return True

@meta.hook(EBNF, "EBNF.add_subsequence")
def add_subsequence(self, sequence, subsequence):
    sequence.parser_tree = subsequence.parser_tree
    return True

@meta.hook(EBNF, "EBNF.add_optional")
def add_optional(self, repeat):
    repeat.functor = parsing.RepOptional
    return True

@meta.hook(EBNF, "EBNF.add_0N")
def add_0N(self, repeat):
    repeat.functor = parsing.Rep0N
    return True

@meta.hook(EBNF, "EBNF.add_1N")
def add_1N(self, repeat):
    repeat.functor = parsing.Rep1N
    return True

@meta.hook(EBNF, "EBNF.add_hook")
def add_hook(self, sequence, h):
    sequence.parser_tree = parsing.Hook(h.name, h.listparam)
    return True

@meta.hook(EBNF, "EBNF.param_num")
def param_num(self, param, n):
    param.pair = (int(n.value), int)
    return True

@meta.hook(EBNF, "EBNF.param_str")
def param_str(self, param, s):
    param.pair = (s.value, str)
    return True

@meta.hook(EBNF, "EBNF.param_id")
def param_id(self, param, i):
    param.pair = (i.value, parsing.Node)
    return True

@meta.hook(EBNF, "EBNF.hook_name")
def hook_name(self, hook, n):
    hook.name = n.value
    hook.listparam = []
    return True

@meta.hook(EBNF, "EBNF.hook_param")
def hook_param(self, hook, p):
    hook.listparam.append(p.pair)
    return True

@meta.hook(EBNF, "EBNF.add_directive")
def add_directive(self, sequence, d, s):
    if not hasattr(EBNF, '_directives'):
        raise TypeError("empty _directives dictionnary in dsl.EBNF")
    the_class = EBNF._directives[d.name]
    sequence.parser_tree = parsing.Directive(the_class(), d.listparam, s.parser_tree)
    return True
