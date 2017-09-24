"""
This module provide the Pyrser Selector Language
"""
import os
from pyrser import grammar
from pyrser import meta
from pyrser.ast.match import *
from pyrser.parsing import unquote_string

from pyrser.passes.to_yml import *

from pyrser.hooks.echo import *
from pyrser.hooks.vars import *

# PARSING
PSL = grammar.from_file(os.path.dirname(__file__) + "/psl.bnf", 'psl') 

def match(tree, compile_psl, hooks, user_data):
    #TODO: not complete
    from pyrser.ast.walk import walk
    from pyrser.parsing.node import normalize
    from pyrser.ast.stack_action import get_events_list, Checker

    tree = normalize(tree)
    stack = []
    for block in compile_psl:
        stack += [block.get_stack_action()]
    #print(repr(stack))
    chk = Checker(hooks, user_data)
    res = False

    class FakeList:
        def __init__(self, gen):
            self.gen = gen

        def __iter__(self):
            self.cache = []
            self.idx = 0
            return self

        def __next__(self):
            ev = self.gen.send(None)
            self.cache.append(ev)
            self.idx += 1
            return ev

        def __getitem__(self, k):
            if k not in self.cache and k > self.idx:
                while self.idx < k:
                    self.cache.append(self.gen.send(None))
                    self.idx += 1
            return self.cache[k]

    #ls = FakeList(walk(tree))
    ls = get_events_list(tree)
    for idx, ev in enumerate(ls):
        chk.check_event_and_action(idx, ls, stack)


# new methods
@meta.add_method(PSL)
def compile(self, txt) -> MatchExpr:
    res = self.parse(txt)
    return res.node

# hooks

@meta.hook(PSL)
def new_MatchBlock(self, ast, blck):
    if not hasattr(ast, 'node'):
        ast.node = []
    ast.node.append(MatchBlock(blck.node))
    return True

@meta.hook(PSL)
def new_MatchHook(self, blck, s):
    if not hasattr(blck, 'node'):
        blck.node = []
    blck.node.append(s.node)
    return True

@meta.hook(PSL)
def new_Hook(self, ast, h, ns):
    ast.node = MatchHook(h.node, ns.node)
    return True

@meta.hook(PSL)
def new_Event(self, ast, e, ns):
    ast.node = MatchEvent(e.node, ns.node)
    return True

@meta.hook(PSL)
def new_MatchAncestor(self, ast, n, depth, flags):
    d = 1
    f = False
    if self.value(depth) != "":
        d = int(self.value(depth))
    if self.value(flags) != "":
        f = True
    ast.node = MatchAncestor(ast.node, n.node, d, f)
    return True

@meta.hook(PSL)
def new_MatchSibling(self, ast, n):
    ast.node = MatchSibling(ast.node, n.node)
    return True

@meta.hook(PSL)
def new_MatchCapture(self, ast, i):
    ast.node = MatchCapture(self.value(i), ast.node)
    return True

@meta.hook(PSL)
def new_MatchCapturePair(self, ast, i):
    ast.node = MatchCapture(self.value(i), ast.node, capture_pair=True)
    return True

@meta.hook(PSL)
def new_text(self, ast, i):
    ast.node = self.value(i)
    return True


@meta.hook(PSL)
def new_MatchValue(self, ast, v):
    vnode = None
    if hasattr(v, 'node'):
        vnode = v.node
    elif self.value(v) == '*':
        vnode = None
    ast.node = MatchValue(vnode)
    return True

@meta.hook(PSL)
def is_num(self, ast, n):
    ast.node = int(self.value(n))
    return True

@meta.hook(PSL)
def is_float(self, ast, f):
    ast.node = float(self.value(f))
    return True

@meta.hook(PSL)
def is_str(self, ast, s):
    ast.node = unquote_string(self.value(s))
    return True

@meta.hook(PSL)
def new_MatchType(self, ast, n, nd, idef, strict, iskindof):
    tname = self.value(n)
    is_strict = True
    if len(self.value(strict)) > 0:
        is_strict = False
    iko = False
    if len(self.value(iskindof)) > 0:
        iko = True
    defsub = None
    if hasattr(idef, 'node') and type(idef.node[0]) in {MatchDict, MatchList}:
        defsub = idef.node[0]
    attrs = None
    if hasattr(nd, 'node'):
        attrs = nd.node
    ast.node = MatchType(tname, attrs, defsub, is_strict, iko)
    return True

@meta.hook(PSL)
def add_def_into(self, ast, it, strict):
    if not hasattr(ast, 'node'):
        ast.node = []
    is_strict = True
    if len(self.value(strict)) > 1:
        is_strict = False
    it.node.strict = is_strict
    ast.node.append(it.node)
    return True

@meta.hook(PSL)
def def_into(self, ast, it, strict):
    if not hasattr(ast, 'node'):
        ast.node = None
    is_strict = True
    if len(self.value(strict)) > 1:
        is_strict = False
    it.node.strict = is_strict
    ast.node = it.node
    return True

@meta.hook(PSL)
def add_into(self, ast, it):
    if not hasattr(ast, 'node'):
        ast.node = []
    if type(it.node) is list:
        ast.node += it.node
    else:
        ast.node.append(it.node)
    return True

@meta.hook(PSL)
def new_MatchAttr(self, ast, n, ns):
    attr = self.value(n)
    if attr == '*':
        attr = None
    ast.node = MatchAttr(attr, ns.node)
    return True

@meta.hook(PSL)
def new_MatchDict(self, ast, ls):
    ast.node = MatchDict(ls.node)
    return True

@meta.hook(PSL)
def new_MatchKey(self, ast, k, ns):
    key = self.value(k)
    if key == '*':
        key = None
    else:
        key = k.node
    ast.node = MatchKey(key, ns.node)
    return True

@meta.hook(PSL)
def new_MatchList(self, ast, ls):
    ast.node = MatchList(ls.node)
    return True

@meta.hook(PSL)
def new_MatchIndice(self, ast, i, ns):
    idx = self.value(i)
    if idx == '*':
        idx = None
    else:
        idx = int(idx)
    ast.node = MatchIndice(idx, ns.node)
    return True

@meta.hook(PSL)
def new_MatchPrecond(self, ast, expr, t):
    ast.node = MatchPrecond(expr.node, t.node)
    return True

@meta.hook(PSL)
def new_PrecondOr(self, ast, expr):
    ast.node = PrecondOr(ast.node, expr.node)
    return True

@meta.hook(PSL)
def new_PrecondXor(self, ast, expr):
    ast.node = PrecondXor(ast.node, expr.node)
    return True

@meta.hook(PSL)
def new_PrecondAnd(self, ast, expr):
    ast.node = PrecondAnd(ast.node, expr.node)
    return True

@meta.hook(PSL)
def new_PrecondNot(self, ast, expr):
    ast.node = PrecondNot(expr.node)
    return True

@meta.hook(PSL)
def new_PrecondParen(self, ast, expr):
    ast.node = PrecondParen(expr.node)
    return True

@meta.hook(PSL)
def new_PrecondEvent(self, ast, i):
    ast.node = PrecondEvent(self.value(i))
    return True
