"""
This module provide classes for PSL (Pyrser Selectors Language) implementation.
"""

from weakref import *
from pyrser import fmt
from pyrser.ast import state


################

class MatchExpr:
    """
    Ast Node for all match expression.
    """
    pass


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

    def is_in_state(self, s: state.State):
        if self.idx is None and '*' in s.indices:
            return s.indices['*']
        elif self.idx in s.indices:
            return s.indices[self.idx]
        return None

    def attach(self, s1: state.State, s2: state.State, sr: state.StateRegister):
        s1.matchIndice(self.idx, s2)

    def build_state_tree(self, tree: list):
        # go deeper
        self.v.build_state_tree(tree)
        # add ourself
        tree.append(self)

    def to_fmt(self) -> fmt.indentable:
        index = '*'
        if self.idx is not None:
            index = str(self.idx)
        res = fmt.block('[' + index + ': ', ']', [])
        res.lsdata.append(self.v.to_fmt())
        return res

    def __repr__(self) -> str:
        return str(self.to_fmt())

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

    def is_in_state(self, s: state.State):
        if self.key in s.keys:
            return s.keys[self.key]
        return None

    def attach(self, s1: state.State, s2: state.State, sr: state.StateRegister):
        s1.matchKey(self.key, s2)

    def build_state_tree(self, tree: list):
        # go deeper
        self.v.build_state_tree(tree)
        # add ourself
        tree.append(self)

    def to_fmt(self) -> fmt.indentable:
        key = '*'
        if self.key is not None:
            key = repr(self.key)
        res = fmt.block('{' + key + ': ', '}', [])
        res.lsdata.append(self.v.to_fmt())
        return res

    def __repr__(self) -> str:
        return str(self.to_fmt())

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

    def is_in_state(self, s: state.State):
        if self.name in s.attrs:
            return s.attrs[self.name]
        return None

    def attach(self, s1: state.State, s2: state.State, sr: state.StateRegister):
        if self.name is not None:
            s1.matchAttr(self.name, s2)
        else:
            s1.matchDefault(s2)

    def build_state_tree(self, tree: list):
        # go deeper
        self.v.build_state_tree(tree)
        #TODO: match all attr
        # add ourself
        tree.append(self)
        return tree

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

class MatchValue(MatchExpr):
    """
    Ast Node for matching one value.
    """
    def __init__(self, v=None):
        # if v is None -> wildcard
        self.v = v

    def __eq__(self, other) -> bool:
        return self.v == other.v

    def is_in_state(self, s: state.State):
        if self.v is None and '*' in s.values:
            return s.values['*']
        elif str(self.v) in s.values:
            return s.values[str(self.v)]
        return None

    def attach(self, s1: state.State, s2: state.State, sr: state.StateRegister):
        s1.matchValue(self.v, s2)

    def build_state_tree(self, tree: list):
        # we are typically a leaf
        tree.append(self)

    def to_fmt(self) -> fmt.indentable:
        res = fmt.sep('', [])
        if self.v is None:
            res.lsdata.append('*')
        else:
            res.lsdata.append(repr(self.v))
        return res

    def __repr__(self) -> str:
        return str(self.to_fmt())

class MatchType(MatchExpr):
    """
    Ast Node for matching exactly one type.
    """
    def __init__(self, t: type=object, attrs: [MatchExpr]=None, strict=True, iskindof=False):
        self.t = t
        self.attrs = attrs
        self.strict = strict
        self.iskindof = iskindof

    def __eq__(self, other) -> bool:
        return self.t is other.t

    def is_in_state(self, s: state.State):
        if self.iskindof and self.t in s.ktypes:
            return s.ktypes[self.t]
        if not self.iskindof and self.t in s.types:
            return s.types[self.t]
        return None

    def attach(self, s1: state.State, s2: state.State, sr: state.StateRegister):
        if self.t is not object:
            if self.iskindof:
                s1.matchKindType(self.t, s2)
            else:
                s1.matchType(self.t, s2)
            # to avoid artefact, store the minimal subelement to match
            s1.minsubelmt = len(self.attrs)

    def build_state_tree(self, tree: list):
        precond = None
        if self.attrs is not None:
            # TODO: attr with unknown name... after all other attr
            if self.strict:
                # go deeper
                for a in self.attrs:
                    a.build_state_tree(tree)
            else:
                # for non-strict match of type, we used unamed events...
                list_alt = []
                list_ev = []
                idx = 0
                for a in self.attrs:
                    # add a new event...
                    ev_name = '.E' + str(id(self)) + '_' + str(idx)
                    # the MatchEvent instance will set the event when is reached
                    ev = MatchEvent(ev_name, a)
                    b = list()
                    ev.build_state_tree(b)
                    list_alt.append(b)
                    # add the unamed event name
                    list_ev.append(ev_name)
                    idx += 1
                # add match event for the computed precond...
                list_expr = []
                for e in list_ev:
                    list_expr.append(state.EventNamed(e))
                precond = MatchPrecond(state.EventSeq(list_expr), MatchType(self.t, attrs=[], strict=True, iskindof=self.iskindof), clean_event=True)
                # add all alternative states
                tree.append(list_alt)
        # if needed, add a precondition
        if precond is not None:
            precond.build_state_tree(tree)
        # append ourself to match the type
        elif self.t is not object:
            tree.append(self)

    def to_fmt(self) -> fmt.indentable:
        res = fmt.sep('', [])
        if self.t is not object:
            res.lsdata.append(self.t.__name__)
        else:
            res.lsdata.append('*')
        iparen = []
        if self.attrs is not None:
            # TODO: render unknown attr (.?) at the end after ..., also unknown attr implie 'unstrict' mode
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

class MatchPrecond(MatchExpr):
    """
    Ast Node for matching a precondition expression.
    """
    def __init__(self, precond: state.EventExpr, v: MatchValue=None, clean_event=True):
        self.precond = precond
        self.v = v
        self.clean_event = clean_event

    def __eq__(self, other) -> bool:
        return id(self.precond) == id(other.precond)

    def is_in_state(self, s: state.State):
        if self.precond in s.events_expr:
            return s.events_expr[self.precond]
        return None

    def attach(self, s1: state.State, s2: state.State, sr: state.StateRegister):
        s1.matchEventExpr(self.precond, s2, self.clean_event)

    def build_state_tree(self, tree: list):
        # go deeper
        if self.v is not None:
            self.v.build_state_tree(tree)
        # add ourself
        tree.append(self)

    def to_fmt(self) -> fmt.indentable:
        res = fmt.sep(' ', [])
        if self.v is not None:
            res.lsdata.append(self.v.to_fmt())
        if self.clean_event:
            res.lsdata.append('?')
        else:
            res.lsdata.append('??')
        res.lsdata.append('<' + repr(self.precond) + '>')
        return res

    def __repr__(self) -> str:
        return str(self.to_fmt())

class MatchEvent(MatchExpr):
    """
    Ast Node for a Resulting Event.
    """
    def __init__(self, n: str, v: MatchValue):
        self.n = n
        self.v = v

    def __eq__(self, other) -> bool:
        return self.n == other.n

    def attach(self, s1: state.State, s2: state.State, sr: state.StateRegister):
        # TODO:!!! the event must be store in the LivingState
        s1.matchEvent(self.n, s2)

    def build_state_tree(self, tree: list):
        # go deeper
        self.v.build_state_tree(tree)
        # add ourself
        tree.append(self)

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

    def attach(self, s1: state.State, s2: state.State, sr: state.StateRegister):
        s1.matchHook(self.call, s2)

    def build_state_tree(self, tree: list):
        # go deeper
        self.v.build_state_tree(tree)
        # add ourself
        tree.append(self)

    def to_fmt(self) -> fmt.indentable:
        res = fmt.sep(' -> ', [self.v.to_fmt(), '#' + self.n + ';'])
        return res

    def __repr__(self) -> str:
        return str(self.to_fmt())

class MatchBlock(MatchExpr):
    """
    Ast Node for a block of PSL statement.
    """
    def __init__(self, stmts: [MatchExpr]):
        self.stmts = stmts
        self.root_edge = None

    def build_state_tree(self, tree: list, sr: state.StateRegister):
        """
        main function for creating a bottom-up tree automata for a block of matching statements.
        """
        all_seq = []
        # for all statements populate a list from deeper to nearer of MatchExpr instances.
        for stmt in self.stmts:
            part_seq = list()
            stmt.build_state_tree(part_seq)
            all_seq.append(part_seq)
        # Walk on all MatchExpr instance and create State instance into the StateRegister
        self.root_edge = populate_state_register(all_seq, sr)

    def to_fmt(self) -> fmt.indentable:
        res = fmt.block('{\n', '}', [fmt.tab([])])
        lines = res.lsdata[0].lsdata
        for stmt in self.stmts:
            lines.append(fmt.end('\n', stmt.to_fmt()))
        return res

    def __repr__(self) -> str:
        return str(self.to_fmt())

##############

class Edge:
    """
    Class that implement the state transition, used for state construction.
    """
    def __init__(self, s: state.State):
        self.s = s
        self.next_edge = {}

    def get_next_edge(self, m: MatchExpr):
        # check if the MatchExpr is already handle by the state
        if hasattr(m, 'is_in_state'):
            sX = m.is_in_state(self.s)
            if sX is not None:
                # return the corresponding edge
                return self.next_edge[id(sX)]
        return None

def populate_from_sequence(seq: list, r: ref(Edge), sr: state.StateRegister):
    """
    function that connect each other one sequence of MatchExpr.
    """
    base_state = r
    # we need to detect the last state of the sequence
    idxlast = len(seq) - 1
    idx = 0
    for m in seq:
        # alternatives are represented by builtin list
        if isinstance(m, list):
            # so recursively connect all states of each alternative sequences.
            for item in m:
                populate_from_sequence(item, r, sr)
        elif isinstance(m, MatchExpr):
            # from the current state, have we a existing edge for this event?
            eX = r().get_next_edge(m)
            if eX is None:
                sX = None
                if idx != idxlast:
                    sX = state.State(sr)
                    sX.matchDefault(base_state().s)
                else:
                    # last state of sequence return to the base
                    sX = base_state().s
                eX = Edge(sX)
                r().next_edge[id(sX)] = eX
                m.attach(r().s, sX, sr)
            r = ref(eX)
        idx += 1

def populate_state_register(all_seq: [list], sr: state.StateRegister) -> Edge:
    """
    function that create a state for all instance of MatchExpr in the given list and connect each others.
    """
    # Basic State
    s0 = state.State(sr)
    # loop on himself
    s0.matchDefault(s0)
    # this is default
    sr.set_default_state(s0)
    # use Edge to store connection
    e0 = Edge(s0)
    for seq in all_seq:
        r = ref(e0)
        # merge all sequences into one tree automata
        populate_from_sequence(seq, r, sr)
    # return edge for debug purpose
    return e0

