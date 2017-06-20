"""
This module provide classes for PSL (Pyrser Selectors Language) implementation.
"""

from weakref import *
from pyrser import fmt

################

class MatchExpr:
    """
    Ast Node for all match expression.
    """
    def get_match_tree(self, tree, idx, uid) -> []:
        raise TypeError("Not implemented")


class MatchIndice(MatchExpr):
    """
    Ast Node for matching one indice.
    """
    def __init__(self, idx: int, v=None):
        self.idx = idx
        if v is None:
            v = MatchValue()
        self.v = v

    def __eq__(self, other) -> bool:
        return self.idx == other.idx

    def to_fmt(self) -> fmt.indentable:
        index = '*'
        if self.idx is not None:
            index = str(self.idx)
        res = fmt.sep('', [index + ': ', self.v.to_fmt()])
        return res

    def __repr__(self) -> str:
        return str(self.to_fmt())

    def get_match_tree(self, tree, idx, uid) -> []:
        lastidx = 0
        if self.v is not None:
            lastidx = self.v.get_match_tree(tree, idx, uid)
        idx = lastidx + 1
        sz = len(tree)
        t = ('indice', self.idx, uid)
        if idx >= sz:
            tree.append(t)
            return idx
        elif type(tree[idx]) is not list:
            # add alternatives
            tree[idx] = [tree[idx]]
        if t not in tree[idx]:
            tree[idx].append(t)
        return idx

class MatchList(MatchExpr):
    """
    Ast Node for matching indices.
    """
    def __init__(self, ls: [MatchIndice]):
        self.ls = ls

    def __eq__(self, other) -> bool:
        return self.ls == other.ls

    def to_fmt(self) -> fmt.indentable:
        res = fmt.block('[', ']', [])
        subls = []
        for item in self.ls:
            subls.append(item.to_fmt())
        res.lsdata.append(fmt.sep(', ', subls))
        return res

    def __repr__(self) -> str:
        return str(self.to_fmt())

    def get_match_tree(self, tree, idx, uid) -> []:
        lastidx = idx
        for item in self.ls:
            lastidx = item.get_match_tree(tree, lastidx, uid)
        idx = lastidx + 1
        sz = len(tree)
        t = ('list', None, uid)
        if idx >= sz:
            tree.append(t)
            return idx
        elif type(tree[idx]) is not list:
            # add alternatives
            tree[idx] = [tree[idx]]
        if t not in tree[idx]:
            tree[idx].append(t)
        return idx

class MatchKey(MatchExpr):
    """
    Ast Node for matching one key.
    """
    def __init__(self, key: str, v=None):
        self.key = key
        if v is None:
            v = MatchValue()
        self.v = v

    def __eq__(self, other) -> bool:
        return self.key == other.key

    def to_fmt(self) -> fmt.indentable:
        key = '*'
        if self.key is not None:
            key = repr(self.key)
        res = fmt.sep('', [key + ': ', self.v.to_fmt()])
        return res

    def __repr__(self) -> str:
        return str(self.to_fmt())

    def get_match_tree(self, tree, idx, uid) -> []:
        if self.v is not None:
            idx = self.v.get_match_tree(tree, idx, uid)
        idx += 1
        sz = len(tree)
        t = ('key', self.key, uid)
        if idx >= sz:
            tree.append(t)
            return idx
        elif type(tree[idx]) is not list:
            # add alternatives
            tree[idx] = [tree[idx]]
        if t not in tree[idx]:
            tree[idx].append(t)
        return idx

class MatchDict(MatchExpr):
    """
    Ast Node for matching a Dict.
    """
    def __init__(self, d: [MatchKey]):
        self.d = d

    def __eq__(self, other) -> bool:
        return self.d == other.d

    def to_fmt(self) -> fmt.indentable:
        res = fmt.block('{', '}', [])
        subls = []
        for item in self.d:
            subls.append(item.to_fmt())
        res.lsdata.append(fmt.sep(', ', subls))
        return res

    def __repr__(self) -> str:
        return str(self.to_fmt())

    def get_match_tree(self, tree, idx, uid) -> []:
        lastidx = idx
        for item in self.d:
            lastidx = item.get_match_tree(tree, lastidx, uid)
        idx = lastidx + 1
        sz = len(tree)
        t = ('dict', None, uid)
        if idx >= sz:
            tree.append(t)
            return idx
        elif type(tree[idx]) is not list:
            # add alternatives
            tree[idx] = [tree[idx]]
        if t not in tree[idx]:
            tree[idx].append(t)
        return idx

class MatchAttr(MatchExpr):
    """
    Ast Node for matching one attribute.
    """
    def __init__(self, name: str=None, v=None):
        self.name = name
        if v is None:
            v = MatchValue()
        self.v = v

    def __eq__(self, other) -> bool:
        return self.name == other.name

    def to_fmt(self) -> fmt.indentable:
        n = '*'
        if self.name is not None:
            n = self.name
        n = '.' + n
        v = '*'
        if self.v is not None:
            v = self.v.to_fmt()
        res = fmt.sep('=', [n, v])
        return res

    def __repr__(self) -> str:
        return str(self.to_fmt())

    def get_match_tree(self, tree, idx, uid) -> []:
        #subtree = []
        if self.v is not None:
            idx = self.v.get_match_tree(tree, -1, (id(self), uid))
        idx += 1
        sz = len(tree)
        t = ('attr', self.name, (id(self), uid))
        if idx >= sz:
            tree.append(t)
            return idx
        elif type(tree[idx]) is not list:
            # add alternatives
            tree[idx] = [tree[idx]]
        if t not in tree[idx]:
            tree[idx].append(t)
        return idx


class MatchValue(MatchExpr):
    """
    Ast Node for matching one value.
    """
    def __init__(self, v=None):
        # if v is None -> wildcard
        self.v = v

    def __eq__(self, other) -> bool:
        return self.v == other.v

    def to_fmt(self) -> fmt.indentable:
        res = fmt.sep('', [])
        if self.v is None:
            res.lsdata.append('*')
        else:
            res.lsdata.append(repr(self.v))
        return res

    def __repr__(self) -> str:
        return str(self.to_fmt())

    def get_match_tree(self, tree, idx, uid) -> []:
        idx += 1
        sz = len(tree)
        t = ('value', self.v, uid)
        if idx >= sz:
            tree.append(t)
            return idx
        elif type(tree[idx]) is not list:
            # add alternatives
            tree[idx] = [tree[idx]]
        if t not in tree[idx]:
            tree[idx].append(t)
        return idx

class MatchType(MatchExpr):
    """
    Ast Node for matching exactly one type.
    """
    def __init__(
        self,
        t: type=object,
        attrs: [MatchExpr]=None,
        strict=True,
        iskindof=False
    ):
        self.t = t
        self.attrs = attrs
        self.strict = strict
        self.iskindof = iskindof

    def __eq__(self, other) -> bool:
        return self.t is other.t

    def to_fmt(self) -> fmt.indentable:
        res = fmt.sep('', [])
        if self.t is not object:
            res.lsdata.append(self.t.__name__)
        else:
            res.lsdata.append('*')
        iparen = []
        if self.attrs is not None:
            # TODO: render unknown attr (.?) at the end after ...,
            # also unknown attr implie 'unstrict' mode
            iparen = fmt.sep(', ', [])
            for a in self.attrs:
                iparen.lsdata.append(a.to_fmt())
        if not self.strict:
            iparen.lsdata.append('...')
        if self.iskindof:
            paren = fmt.block('^(', ')', iparen)
        else:
            paren = fmt.block('(', ')', iparen)
        res.lsdata.append(paren)
        return res

    def __repr__(self) -> str:
        return str(self.to_fmt())

    def get_match_tree(self, tree, idx, uid) -> []:
        lastidx = idx
        if self.strict:
            for item in self.attrs:
                lastidx = item.get_match_tree(tree, lastidx, (id(self), uid))
        else:
            subtree = []
            for item in self.attrs:
                lastidx = item.get_match_tree(subtree, -1, id(self))
            idx += 1
            sz = len(tree)
            t = ('attr_non_strict', subtree, (id(self), uid))
            if idx >= sz:
                tree.append(t)
            elif type(tree[idx]) is not list:
                tree[idx] = [tree[idx]]
            if idx < sz and t not in tree[idx]:
                tree[idx].append(t)
            lastidx = idx
        idx = lastidx + 1
        sz = len(tree)
        t = ('type', self.t.__name__, uid)
        if idx >= sz:
            tree.append(t)
            return idx
        elif type(tree[idx]) is not list:
            # add alternatives
            tree[idx] = [tree[idx]]
        if t not in tree[idx]:
            tree[idx].append(t)
        return idx

#class MatchPrecond(MatchExpr):
#    """
#    Ast Node for matching a precondition expression.
#    """
#    def __init__(
#        self,
#        precond: state.EventExpr,
#        v: MatchValue=None,
#        clean_event=True
#    ):
#        self.precond = precond
#        self.v = v
#        self.clean_event = clean_event
#
#    def __eq__(self, other) -> bool:
#        return id(self.precond) == id(other.precond)
#
#    def to_fmt(self) -> fmt.indentable:
#        res = fmt.sep(' ', [])
#        if self.v is not None:
#            res.lsdata.append(self.v.to_fmt())
#        if self.clean_event:
#            res.lsdata.append('?')
#        else:
#            res.lsdata.append('??')
#        res.lsdata.append('<' + repr(self.precond) + '>')
#        return res
#
#    def __repr__(self) -> str:
#        return str(self.to_fmt())


class MatchEvent(MatchExpr):
    """
    Ast Node for a Resulting Event.
    """
    def __init__(self, n: str, v: MatchValue):
        self.n = n
        self.v = v

    def __eq__(self, other) -> bool:
        return self.n == other.n

    def to_fmt(self) -> fmt.indentable:
        res = fmt.sep(' -> ', [self.v.to_fmt(), self.n + ';'])
        return res

    def __repr__(self) -> str:
        return str(self.to_fmt())


class MatchHook(MatchExpr):
    """
    Ast Node for a Resulting Hook.
    """
    def __init__(self, call: callable, v: MatchValue):
        if not callable(call):
            raise ValueError("argument 'call' must be callable")
        self.call = call
        self.n = call.__name__
        self.v = v

    def __eq__(self, other) -> bool:
        return id(self.call) == id(other.call)

    def to_fmt(self) -> fmt.indentable:
        res = fmt.sep(' -> ', [self.v.to_fmt(), '#' + self.n + ';'])
        return res

    def __repr__(self) -> str:
        return str(self.to_fmt())

    def get_match_tree(self, tree, idx, uid = 0) -> []:
        idx = self.v.get_match_tree(tree, idx, id(self))
        idx += 1
        sz = len(tree)
        t = ('hook', self.n, id(self))
        if idx >= sz:
            tree.append(t)
            return idx
        elif type(tree[idx]) is not list:
            # add alternatives
            tree[idx] = [tree[idx]]
        if t not in tree[idx]:
            tree[idx].append(t)
        return idx

class MatchBlock(MatchExpr):
    """ Ast Node for a block of PSL statement. """
    def __init__(self, stmts: [MatchExpr]):
        self.stmts = stmts
        self.root_edge = None

    def to_fmt(self) -> fmt.indentable:
        res = fmt.block('{\n', '}', [fmt.tab([])])
        lines = res.lsdata[0].lsdata
        for stmt in self.stmts:
            lines.append(fmt.end('\n', stmt.to_fmt()))
        return res

    def __repr__(self) -> str:
        return str(self.to_fmt())

    def get_match_tree(self, tree, idx = -1, uid = 0) -> []:
        lastidx = 0
        for item in self.stmts:
            lastidx = item.get_match_tree(tree, idx, uid)
        idx = lastidx + 1
        tree.append(('block', None))
        return idx
