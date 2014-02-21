# little grammar for test
import os
from pyrser import grammar
from pyrser import meta
from pyrser import fmt
from pyrser.parsing.node import *
from pyrser.hooks.echo import *
from pyrser.hooks.vars import *


### ABSTRACTION


class BlockStmt(Node):
    def __init__(self, root=False):
        self.body = []
        # if root node (no brace when pprint)
        self.root = root
        
    def to_tl4t(self) -> fmt.indentable:
        lssub = []
        for s in self.body:
            lssub.append(s.to_tl4t())
        lsblock = None
        if self.root:
            lsblock = fmt.sep('', lssub)
        else:
            lsblock = fmt.block('{\n', '}', [fmt.tab(lssub)])
        return lsblock


class DeclVar(Node):
    def __init__(self, name: str, t: str, expr=None):
        super().__init__()
        self.name = name
        self.t = t
        if expr is not None:
            self.expr = expr

    def to_tl4t(self) -> fmt.indentable:
        lsdecl = [
            "var",
            self.name,
            ":",
            self.t
        ]
        if hasattr(self, 'expr'):
            lsdecl.append("=")
            lsdecl.append(self.expr.to_tl4t())
        return fmt.end(';\n', [fmt.sep(" ", lsdecl)])


class DeclFun(DeclVar):
    def __init__(self, name: str, t: str, p: [], block=None):
        super().__init__(name, t)
        self.p = p
        if block is not None:
            self.block = block

    def to_tl4t(self) -> fmt.indentable:
        params = []
        if self.p is not None:
            for p in self.p:
                params.append(p.to_tl4t())
        parenth = fmt.block('(', ')', fmt.sep(", ", params))
        lsdecl = fmt.sep(
            ' ',
            [
                "fun",
                fmt.sep('', [self.name, parenth]),
                ":",
                self.t
            ]
        )
        lsblock = None
        if hasattr(self, 'block'):
            lsblock = fmt.sep("\n", [lsdecl, self.block.to_tl4t()])
        else:
            lsblock = fmt.end(";\n", lsdecl)
        return lsblock


class Param(Node):
    def __init__(self, n: str, t: str):
        self.name = n
        self.t = t

    def to_tl4t(self):
        return fmt.sep(" ", [self.name, ':', self.t])


class Terminal(Node):
    def __init__(self, value):
        self.value = value

    def to_tl4t(self) -> fmt.indentable:
        return self.value


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

    def to_tl4t(self):
        params = []
        for p in self.p:
            params.append(p.to_tl4t())
        parenth = fmt.block('(', ')', fmt.sep(', ', params))
        lsblock = fmt.sep('', [
            self.call_expr.to_tl4t(),
            parenth
        ])
        return lsblock


class ExprStmt(Node):
    def __init__(self, e: Expr):
        self.expr = e

    def to_tl4t(self):
        return fmt.end(";\n", self.expr.to_tl4t())


class Binary(Expr):
    def __init__(self, left: Expr, op: Raw, right: Expr):
        super().__init__(op, [left, right])

    def to_tl4t(self):
        return fmt.sep(" ", [self.p[0].to_tl4t(), self.call_expr.to_tl4t(), self.p[1].to_tl4t()])


class Unary(Expr):
    def __init__(self, op: Raw, expr: Expr):
        super().__init__(op, [expr])

    def to_tl4t(self):
        return fmt.sep("", [self.call_expr.to_tl4t(), self.p[0].to_tl4t()])


class Paren(Expr):
    def __init__(self, expr: Expr):
        super().__init__(None, [expr])

    def to_tl4t(self):
        return fmt.block("(", ")", [self.p[0].to_tl4t()])


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
    if b is not None and hasattr(b, 'body'):
        expr = b
    if hasattr(p, 'node'):
        param = p.node
    ast.set(DeclFun(self.value(n), self.value(t), param, expr))
    return True


@meta.hook(TL4T)
def new_rootstmt(self, block, s):
    if not isinstance(block, BlockStmt):
        block.set(BlockStmt(True))
    block.body.append(s)
    return True


@meta.hook(TL4T)
def new_stmt(self, block, s):
    if not isinstance(block, BlockStmt):
        block.set(BlockStmt())
    block.body.append(s)
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
def new_expr_stmt(self, ast, e):
    ast.set(ExprStmt(e))
    return True


@meta.hook(TL4T)
def new_binary(self, ast, op, right):
    left = Node()
    left.set(ast)
    ast.set(Binary(left, op, right))
    return True


@meta.hook(TL4T)
def new_unary(self, ast, op, expr):
    ast.set(Unary(op, expr))
    return True


@meta.hook(TL4T)
def new_func_call(self, ast, fun, args):
    if hasattr(args, 'list'):
        ast.set(Expr(fun, args.list))
    else:
        ast.set(Expr(fun, []))
    return True


@meta.hook(TL4T)
def new_arg(self, ast, arg):
    if not hasattr(ast, 'list'):
        ast.list = []
    ast.list.append(arg)
    return True


@meta.hook(TL4T)
def new_paren(self, ast, expr):
    ast.set(Paren(expr))
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
