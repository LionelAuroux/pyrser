# little grammar for test
import os
from pyrser import grammar
from pyrser import meta
from pyrser import fmt
from pyrser.parsing.node import *
from pyrser.hooks.echo import *
from pyrser.hooks.vars import *
from pyrser.hooks.set import *
from pyrser.type_checking.inference import *
from pyrser.error import *
from pyrser.passes.to_yml import *

### ABSTRACTION


class NodeInfo(Node, Inference):
    def __init__(self):
        self.info = None


class BlockStmt(NodeInfo):
    def __init__(self, root=False):
        super().__init__()
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

    # to connect Inference
    def type_algos(self):
        return (self.infer_block, self.feedback_block, [self.body])


class DeclVar(NodeInfo):
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
    def __init__(self, name: str, t: str, p: [], block=None, variadic=False):
        super().__init__(name, t)
        self.variadic = variadic
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


class Param(NodeInfo):
    def __init__(self, n: str, t: str):
        super().__init__()
        self.name = n
        self.t = t

    def to_tl4t(self):
        return fmt.sep(" ", [self.name, ':', self.t])


class Terminal(NodeInfo):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def to_tl4t(self) -> fmt.indentable:
        return self.value


class Literal(Terminal):

    def __init__(self, value, t):
        self.value = value
        self.type = t

    # to connect Inference
    def type_algos(self):
        return (
            self.infer_literal, self.feedback_literal, [self.value, self.type]
        )


class Id(Terminal):

    # to connect Inference
    def type_algos(self):
        return (self.infer_id, self.feedback_id, [self.value])


class Operator(Terminal):

    # to connect Inference
    def type_algos(self):
        return (self.infer_operator, self.feedback_operator, [self.value])


class Expr(NodeInfo):
    def __init__(self, ce: 'expr', p: ['expr']):
        super().__init__()
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

    # to connect Inference
    def type_algos(self):
        return (self.infer_fun, self.feedback_fun, [self.call_expr, self.p])


class ExprStmt(NodeInfo):
    def __init__(self, e: Expr):
        super().__init__()
        self.expr = e

    def to_tl4t(self):
        return fmt.end(";\n", self.expr.to_tl4t())

    # to connect Inference
    def type_algos(self):
        return (self.infer_subexpr, self.feedback_subexpr, [self.expr])


class Binary(Expr):
    def __init__(self, left: Expr, op: Operator, right: Expr):
        super().__init__(op, [left, right])

    def to_tl4t(self):
        return fmt.sep(
            " ",
            [
                self.p[0].to_tl4t(),
                self.call_expr.to_tl4t(),
                self.p[1].to_tl4t()
            ]
        )


class Unary(Expr):
    def __init__(self, op: Operator, expr: Expr):
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
def info(self):
    n = Node()
    n.info = LocationInfo.from_stream(self._stream)
    return n


@meta.hook(TL4T)
def new_declvar(self, ast, n, t, e, i):
    expr = None
    if e is not None and hasattr(e, 'node'):
        expr = e.node
    ast.set(DeclVar(self.value(n), self.value(t), expr))
    ast.info = i.info
    return True


@meta.hook(TL4T)
def new_declfun(self, ast, n, t, p, b, i):
    param = None
    expr = None
    if b is not None and hasattr(b, 'body'):
        expr = b
    if hasattr(p, 'node'):
        param = p.node
    variadic = False
    if hasattr(p, 'variadic'):
        variadic = True
    ast.set(DeclFun(self.value(n), self.value(t), param, expr, variadic))
    ast.info = i.info
    return True


@meta.hook(TL4T)
def new_rootstmt(self, block, s, i):
    if not isinstance(block, BlockStmt):
        block.set(BlockStmt(True))
    block.body.append(s)
    block.info = i.info
    return True


@meta.hook(TL4T)
def new_stmt(self, block, s, i):
    if not isinstance(block, BlockStmt):
        block.set(BlockStmt())
    block.body.append(s)
    block.info = i.info
    return True


@meta.hook(TL4T)
def add_param(self, params, p):
    if not hasattr(params, 'node'):
        params.node = []
    params.node.append(p)
    return True


@meta.hook(TL4T)
def add_param_variadic(self, params):
    params.variadic = True
    return True


@meta.hook(TL4T)
def new_param(self, ast, n, t, i):
    ast.set(Param(self.value(n), self.value(t)))
    ast.info = i.info
    return True


@meta.hook(TL4T)
def new_expr_stmt(self, ast, e, i):
    ast.set(ExprStmt(e))
    ast.info = i.info
    return True


@meta.hook(TL4T)
def new_binary(self, ast, op, right, i):
    left = Node()
    left.set(ast)
    ast.set(Binary(left, op, right))
    ast.info = i.info
    return True


@meta.hook(TL4T)
def new_unary(self, ast, op, expr, i):
    ast.set(Unary(op, expr))
    ast.info = i.info
    return True


@meta.hook(TL4T)
def new_func_call(self, ast, fun, args, i):
    if hasattr(args, 'list'):
        ast.set(Expr(fun, args.list))
    else:
        ast.set(Expr(fun, []))
    ast.info = i.info
    return True


@meta.hook(TL4T)
def new_arg(self, ast, arg):
    if not hasattr(ast, 'list'):
        ast.list = []
    ast.list.append(arg)
    return True


@meta.hook(TL4T)
def new_paren(self, ast, expr, i):
    ast.set(Paren(expr))
    ast.info = i.info
    return True


@meta.hook(TL4T)
def new_literal(self, ast, val, t, i):
    ast.set(Literal(self.value(val), t.value))
    ast.info = i.info
    return True


@meta.hook(TL4T)
def new_id(self, ast, ident, i):
    ast.set(Id(self.value(ident)))
    ast.info = i.info
    return True


@meta.hook(TL4T)
def new_operator(self, ast, op, i):
    ast.set(Operator(self.value(op)))
    ast.info = i.info
    return True
