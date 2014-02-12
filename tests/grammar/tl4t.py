# little grammar for test
import os
from pyrser import grammar
from pyrser import meta
from pyrser.parsing.node import *
from pyrser.hooks.echo import *
from pyrser.hooks.copy import *


### ABSTRACTION
class DeclVar(Node):
    def __init__(self, name: str, t: str, expr=None):
        super().__init__()
        self.name = name
        self.t = t
        if expr is not None:
            self.expr = expr


class DeclFun(DeclVar):
    def __init__(self, name: str, t: str, p: [], block=None):
        super().__init__(name, t)
        self.p = p
        if block is not None:
            self.block = block


class Param(Node):
    def __init__(self, n: str, t: str):
        self.name = n
        self.t = t


class Terminal(Node):
    def __init__(self, value):
        self.value = value


class Literal(Terminal):
    pass


class Id(Terminal):
    pass


class Raw(Terminal):
    pass


class Expr(Node):
    def __init__(self, ce: 'expr', p: ['expr']):
        self.call_expr = ce
        self.p = p


class Binary(Expr):
    def __init__(self, left: Expr, op: Raw, right: Expr):
        super().__init__(op, [left, right])


class Unary(Expr):
    def __init__(self, op: Raw, expr: Expr):
        super().__init__(op, [expr])


### PARSING

TL4T = grammar.from_file(os.getcwd() + "/tests/bnf/tl4t.bnf", 'source')


@meta.hook(TL4T)
def new_declvar(self, ast, n, t, e):
    expr = None
    if e is not None and hasattr(e, 'node'):
        expr = e.node
    ast.set(DeclVar(self.value(n), self.value(t), expr))
    return True


@meta.hook(TL4T)
def new_declfun(self, ast, n, t, p, b):
    param = None
    expr = None
    if b is not None and hasattr(b, 'node'):
        expr = b.node
    if hasattr(p, 'node'):
        param = p.node
    ast.set(DeclFun(self.value(n), self.value(t), param, expr))
    return True


@meta.hook(TL4T)
def new_stmt(self, block, s):
    if not hasattr(block, 'node'):
        block.node = []
    block.node.append(s)
    return True


@meta.hook(TL4T)
def add_param(self, params, p):
    if not hasattr(params, 'node'):
        params.node = []
    params.node.append(p)
    return True


@meta.hook(TL4T)
def new_param(self, ast, n, t):
    ast.set(Param(self.value(n), self.value(t)))
    return True


@meta.hook(TL4T)
def new_binary(self, left, op, right):
    left.set(Binary(left, op, right))
    return True


@meta.hook(TL4T)
def is_unary(self, ast, op):
    print("here isU %s" % op)
    return True


@meta.hook(TL4T)
def new_func_call(self, ast, fun, args):
    print("here FCALL %s %f" % (fun, args))
    return True


@meta.hook(TL4T)
def new_arg(self, ast, op):
    print("here ARG %s" % arg)
    return True


@meta.hook(TL4T)
def new_paren(self, ast, expr):
    print("here PAREN %s" % expr)
    return True


@meta.hook(TL4T)
def new_literal(self, ast, val):
    ast.set(Literal(self.value(val)))
    return True


@meta.hook(TL4T)
def new_id(self, ast, ident):
    ast.set(Id(self.value(ident)))
    return True


@meta.hook(TL4T)
def new_raw(self, ast, op):
    ast.set(Raw(self.value(op)))
    return True
