"""
This module provide the Pyrser Selector Language
"""
import os
from pyrser import grammar
from pyrser import meta
from pyrser.ast.match import *
from pyrser.parsing import unquote_string

# PARSING
PSL = grammar.from_file(os.path.dirname(__file__) + "/psl.bnf", 'psl') 

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
def new_Action(self, ast, a, ns):
    ast.node = MatchHook(a.node, ns.node)
    return True

@meta.hook(PSL)
def new_MatchCapture(self, ast, i):
    ast.node = MatchCapture(self.value(i), ast.node)
    return True

@meta.hook(PSL)
def new_text(self, ast, i):
    ast.node = self.value(i)
    return True


@meta.hook(PSL)
def new_MatchValue(self, ast, v):
    ast.node = MatchValue(v.node)
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
def new_MatchType(self, ast, n, nd, idef, strict):
    tname = self.value(n)
    is_strict = True
    if len(self.value(strict)) > 1:
        is_strict = False
    defsub = None
    if type(idef) in {MatchDict, MatchList}:
        defsub = idef
    ast.node = MatchType(tname, nd.node, defsub, is_strict)
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
    ast.node = MatchAttr(self.value(n), ns.node)
    return True

@meta.hook(PSL)
def new_MatchDict(self, ast, ls):
    ast.node = MatchDict(ls.node)
    return True

@meta.hook(PSL)
def new_MatchKey(self, ast, k, ns):
    ast.node = MatchKey(k.node, ns.node)
    return True

@meta.hook(PSL)
def new_MatchList(self, ast, ls):
    ast.node = MatchList(ls.node)
    return True

@meta.hook(PSL)
def new_MatchIndice(self, ast, i, ns):
    ast.node = MatchIndice(int(self.value(i)), ns.node)
    return True