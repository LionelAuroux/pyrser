"""
This module provide the Pyrser Selector Language
"""
import os
from pyrser import grammar
from pyrser import meta
from pyrser.psl.match import *
from pyrser.parsing import unquote_string

# PARSING
PSL = grammar.from_file(os.path.dirname(__file__) + "/psl.bnf", 'psl') 

# PSL FUNCTIONS
@meta.add_method(PSL)
def set_psl_hooks(self, map_str_fun):
    if not hasattr(self, 'psl_hooks'):
        self.psl_hooks = {}
    self.psl_hooks.update(map_str_fun)

@meta.add_method(PSL)
def set_psl_types(self, map_str_type):
    if not hasattr(self, 'psl_types'):
        self.psl_types = {}
    self.psl_types.update(map_str_type)

# hooks

@meta.hook(PSL)
def new_MatchBlock(self, ast, blck):
    ast.node = MatchBlock(blck.node)
    return True

@meta.hook(PSL)
def new_MatchHook(self, blck, s):
    if not hasattr(blck, 'node'):
        blck.node = []
    blck.node.append(s.node)
    return True

@meta.hook(PSL)
def new_Action(self, ast, a, ns):
    if a.node not in self.psl_hooks:
        raise TypeError("PSL Hook '%s' is not defined! Use set_psl_hooks() before parse() an PSL Expression" % a.node)
    fun = self.psl_hooks[a.node]
    ast.node = MatchHook(fun, ns.node)
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
def new_MatchType(self, ast, n, nd):
    tname = self.value(n)
    if tname not in self.psl_types:
        raise TypeError("PSL Type '%s' is not defined! Use set_psl_types() before parse() an PSL Expression" % tname)
    t = self.psl_types[tname]
    ast.node = MatchType(t, nd.node)
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
