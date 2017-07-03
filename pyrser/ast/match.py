"""
This module provide classes for PSL (Pyrser Selectors Language) implementation.
"""

from weakref import *
from pyrser import fmt

################

def match(tree) -> bool:
    from pyrser.ast.walk import walk

    res = False
    try:
        g = walk(tree)
        while True:
            ev = g.send(None)
            # TODO: 
            print(ev)
    except StopIteration as e:
        return res
    return False

class MatchExpr:
    """
    Ast Node for all match expression.
    """
    def get_match_tree(self, tree, idx, uid) -> []:
        raise TypeError("Not implemented")

    def ref_me(self, attr: str):
        # child reference this node
        child = getattr(self, attr)
        if child is not None:
            if type(child) is list:
                for c in child:
                    c.parent = self
            elif type(child) is dict:
                for c in child.values():
                    c.parent = self
            else:
                child.parent = self

    def get_root(self) -> 'MatchExpr':
        n = self
        while hasattr(n, 'parent'):
            n = n.parent
        return n

    def create_unknown_event(self) -> int:
        r = self.get_root()
        if not hasattr(r, 'max_unkev'):
            r.max_unkev = 0
            r.mapev = dict()
        uid = r.max_unkev
        r.mapev[uid] = '_%d' % uid
        r.max_unkev += 1
        return uid

class MatchIndice(MatchExpr):
    """
    Ast Node for matching one indice.
    """
    def __init__(self, idx: int, v=None):
        self.idx = idx
        if v is None:
            v = MatchValue()
        self.v = v
        self.ref_me('v')

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
    def __init__(self, ls: [MatchIndice], strict=True):
        self.ls = sorted(ls, key=lambda x: x.idx)
        self.strict = strict
        self.ref_me('ls')

    def __eq__(self, other) -> bool:
        return self.ls == other.ls

    def to_fmt(self) -> fmt.indentable:
        res = fmt.block('[', ']', [])
        subls = []
        for item in self.ls:
            subls.append(item.to_fmt())
        if not self.strict:
            subls.append('...')
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
        self.ref_me('v')

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
    def __init__(self, d: [MatchKey], strict=True):
        self.d = sorted(d, key=lambda x: x.key)
        self.strict = strict
        self.ref_me('d')

    def __eq__(self, other) -> bool:
        return self.d == other.d

    def to_fmt(self) -> fmt.indentable:
        res = fmt.block('{', '}', [])
        subls = []
        for item in self.d:
            subls.append(item.to_fmt())
        if not self.strict:
            subls.append('...')
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
        self.ref_me('v')

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
        subs: [MatchDict or MatchList]=None,
        strict=True,
        iskindof=False
    ):
        self.t = t
        self.attrs = None
        if attrs is not None:
            self.attrs = sorted(attrs, key=lambda x: x.name)
        self.subs = subs
        self.strict = strict
        self.iskindof = iskindof
        self.ref_me('attrs')
        self.ref_me('subs')

    def __eq__(self, other) -> bool:
        return self.t is other.t

    def to_fmt(self) -> fmt.indentable:
        res = fmt.sep('', [])
        if self.t is not object:
            res.lsdata.append(self.t.__name__)
        else:
            res.lsdata.append('*')
        subs = None
        if self.subs is not None:
            subs = self.subs.to_fmt()
        iparen = fmt.sep(', ', [])
        if self.attrs is not None:
            # TODO: render unknown attr (.?) at the end befor ', ...'
            # also unknown attr implie 'unstrict' mode
            for a in self.attrs:
                iparen.lsdata.append(a.to_fmt())
        if not self.strict:
            iparen.lsdata.append('...')
        data = None
        if subs is not None and iparen is not None:
            data = fmt.sep(" ", [subs, iparen])
        elif subs is None:
            data = iparen
        elif iparen is None:
            data = subs
        if self.iskindof:
            paren = fmt.block('^(', ')', data)
        else:
            paren = fmt.block('(', ')', data)
        res.lsdata.append(paren)
        return res

    def __repr__(self) -> str:
        return str(self.to_fmt())

    def get_match_tree(self, tree, idx, uid) -> []:
        subtree = []
        # TODO: self.subs
        # ...
        # TODO: first elem of subtree
        for item in self.attrs:
            lastidx = item.get_match_tree(subtree, -1, id(self))
            unkev = self.create_unknown_event()
            subtree.insert(lastidx + 1, ('event', '_%d' % unkev, id(item)))
        if self.strict:
            subtree.append(('check_attr_len', len(self.attrs), (id(self), uid)))
            idx += 1
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
    Ast Node for a Resulting Event or intermediate Event.
    """
    nbinst = 0

    def __init__(self, n: str, v: MatchExpr):
        self.n = n
        self.v = v
        self.ref_me('v')

    def getname() -> str:
        res = "E%d" % MatchEvent.nbinst
        MatchEvent.nbinst += 1
        return res

    def __eq__(self, other) -> bool:
        return self.n == other.n

    def to_fmt(self) -> fmt.indentable:
        res = fmt.sep(' ! ', [self.v.to_fmt(), self.n + ';'])
        return res

    def __repr__(self) -> str:
        return str(self.to_fmt())

    def get_match_tree(self, tree, idx, uid = 0) -> []:
        idx = self.v.get_match_tree(tree, idx, id(self))
        idx += 1
        sz = len(tree)
        t = ('event', self.n, id(self))
        if idx >= sz:
            tree.append(t)
            return idx
        elif type(tree[idx]) is not list:
            # add alternatives
            tree[idx] = [tree[idx]]
        if t not in tree[idx]:
            tree[idx].append(t)
        return idx


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
        self.ref_me('v')

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
        self.ref_me('stmts')

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
