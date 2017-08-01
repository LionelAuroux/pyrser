"""
This module provide classes for PSL (Pyrser Selectors Language) implementation.
"""

from weakref import *
from pyrser import fmt

##########
class MatchExpr:
    """
    Ast Node for all match expression.
    """
    def get_stack_action(self) -> list:
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

    def get_stack_action(self):
        tree = self.v.get_stack_action()
        t = ('indice',)
        tree[-1].append(t)
        return tree

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

    def get_stack_action(self):
        tree = []
        list_ev = []
        for item in self.ls:
            subtree = item.get_stack_action()
            unkev = self.create_unknown_event()
            subtree[-1].append(('set_event', unkev))
            tree += subtree
            list_ev.append(unkev)
        # final checks
        tree.append([])
        t = ('end_indices',)
        tree[-1].append(t)
        t = ('check_clean_event', list_ev)
        tree[-1].append(t)
        if self.strict:
            t = ('check_len', len(self.d))
            tree[-1].append(t)
        return tree

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

    def get_stack_action(self):
        tree = self.v.get_stack_action()
        t = ('key', self.key)
        tree[-1].append(t)
        return tree

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

    def get_stack_action(self):
        tree = []
        list_ev = []
        for item in self.d:
            subtree = item.get_stack_action()
            unkev = self.create_unknown_event()
            subtree[-1].append(('set_event', unkev))
            tree += subtree
            list_ev.append(unkev)
        # final checks
        tree.append([])
        t = ('end_keys',)
        tree[-1].append(t)
        t = ('check_clean_event', list_ev)
        tree[-1].append(t)
        if self.strict:
            t = ('check_len', len(self.d))
            tree[-1].append(t)
        return tree

class MatchAttr(MatchExpr):
    """
    Ast Node for matching one attribute.
    """
    def __init__(self, name: str=None, v=None):
        self.name = name
        if v is None:
            v = MatchValue()
        if type(v) in {int, str, float, bytes}:
            raise "Not literal"
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

    def get_stack_action(self):
        tree = self.v.get_stack_action()
        t = ('attr', self.name)
        tree[-1].append(t)
        return tree

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

    def get_stack_action(self):
        tree = [[]]
        t = ('value', self.v)
        tree[-1].append(t)
        t = ('type', type(self.v).__name__)
        tree[-1].append(t)
        t = ('end_node',)
        tree[-1].append(t)
        return tree

class MatchType(MatchExpr):
    """
    Ast Node for matching exactly one type.
    """
    def __init__(
        self,
        tname: str,
        attrs: [MatchExpr]=None,
        subs: [MatchDict or MatchList]=None,
        strict=True,
        iskindof=False
    ):
        self.t = tname
        self.attrs = None
        if attrs is not None:
            self.attrs = sorted(attrs, key=lambda x: x.name)
        self.subs = subs
        self.strict = strict
        self.iskindof = iskindof
        self.ref_me('attrs')
        self.ref_me('subs')

    def __eq__(self, other) -> bool:
        return self.t == other.t

    def to_fmt(self) -> fmt.indentable:
        res = fmt.sep('', [])
        res.lsdata.append(self.t)
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

    def get_stack_action(self):
        tree = []
        list_ev = []
        # subs are Dict or List
        if self.subs is not None:
            print("SUBS %s" % type(self.subs))
            tree = self.subs.get_stack_action()
            unkev = self.create_unknown_event()
            tree[-1].append(('set_event', unkev))
            list_ev.append(unkev)
        # TODO: first elem of subtree
        for idx, item in enumerate(self.attrs):
            subtree = item.get_stack_action()
            unkev = self.create_unknown_event()
            if idx == 0:
                subtree[-1].insert(0, ('no_event', ))
            else:
                subtree[-1].insert(0, ('check_event', list_ev.copy()))
            subtree[-1].append(('set_event', unkev))
            tree += subtree
            list_ev.append(unkev)
        # final checks
        tree.append([])
        t = ('end_attrs',)
        tree[-1].append(t)
        t = ('check_clean_event', list_ev)
        tree[-1].append(t)
        if self.strict:
            tree[-1].append(('check_attr_len', len(self.attrs)))
        t = ('type', self.t)
        tree[-1].append(t)
        t = ('end_node',)
        tree[-1].append(t)
        return tree

######### SPECIAL

class MatchCapture(MatchExpr):
    """
    Ast Node for capturing the current node during matching
    """
    def __init__(self, n: str, v: MatchExpr):
        self.name = n
        self.v = v

    def to_fmt(self) -> fmt.indentable:
        res = fmt.sep('/', [])
        res.lsdata.append(self.v.to_fmt())
        res.lsdata.append(self.name)
        return res

    def __repr__(self) -> str:
        return str(self.to_fmt())

    def get_stack_action(self):
        tree = self.v.get_stack_action()
        if tree[-1][-1][0] != 'end_node':
            raise TypeError("Bad postion of Capture in MatchObject")
        # we add capture before leaving the node
        tree[-1].insert(-1, ('capture', self.name))
        return tree

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

    #def get_stack_action(self, tree):
    #    print("%s" % tree)
    #    self.v.get_stack_action(tree)
    #    t = ('event', self.n, id(self))
    #    tree.append(t)

class MatchHook(MatchExpr):
    """
    Ast Node for a Resulting Hook.
    """
    def __init__(self, call: str, v: MatchValue):
        self.n = call
        self.v = v
        self.ref_me('v')

    def __eq__(self, other) -> bool:
        return id(self.call) == id(other.call)

    def to_fmt(self) -> fmt.indentable:
        res = fmt.sep(' -> ', [self.v.to_fmt(), '#' + self.n + ';'])
        return res

    def __repr__(self) -> str:
        return str(self.to_fmt())

    def get_stack_action(self):
        tree = self.v.get_stack_action()
        t = ('hook', self.n)
        tree[-1].append(t)
        return tree

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

    def get_stack_action(self):
        tree = []
        for idx, s in enumerate(self.stmts):
            tree += [(1, idx), s.get_stack_action()]
        return tree
