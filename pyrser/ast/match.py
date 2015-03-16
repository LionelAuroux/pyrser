from weakref import *
from pyrser import fmt
from pyrser.ast import state

class MatchExpr:
    pass

class StateBuilder:
    pass

#### To change to StateSeqBuilder

class StateSeqBuilder(StateBuilder):
    def __init__(self):
        self.ls = list()

    def add_match(self, b: StateBuilder):
        #if not isinstance(b, StateBuilder):
        #    raise ValueError("'b' is should be a StateBuilder")
        self.ls.append(b)

    def attach(self, s1: state.State, s2: state.State, sr: state.StateRegister):
        scurrent = s1
        snew = None
        sz = len(self.ls)
        for idx in range(sz):
            if idx == sz - 1:
                snew = s2
            else:
                snew = state.State(sr)
            snew.matchDefault(s1)
            self.ls[idx].attach(scurrent, snew, sr)
            scurrent = snew

class StateAltBuilder(StateBuilder):
    def __init__(self):
        self.alt = list()

    def add_match(self, b: StateBuilder):
        if not isinstance(b, StateBuilder):
            raise ValueError("'b' is should be a StateBuilder")
        self.alt.append(b)

    def attach(self, s1: state.State, s2: state.State, sr: state.StateRegister):
        scurrent = s1
        snew = None
        sz = len(self.alt)
        for idx in range(sz):
            # TODO: create an event for each branch... 
            snew = state.State(sr)
            snew.matchDefault(s1)
            self.alt[idx].attach(scurrent, snew, sr)
        # TODO: craft an expression <e1>&<e2>&... to s2

################

class MatchIndice(MatchExpr, StateBuilder):
    def __init__(self, idx: int, v=None):
        self.idx = idx
        self.v = v

    def __eq__(self, other) -> bool:
        return self.idx == other.idx

    def is_in_state(self, s: state.State):
        return self.idx in s.indices

    def attach(self, s1: state.State, s2: state.State, sr: state.StateRegister):
        s1.matchIndice(self.idx, s2)

    def build_state_tree(self, tree: StateBuilder):
        if self.v is not None:
            self.v.build_state_tree(tree)
        tree.add_match(self)

    def to_fmt(self) -> fmt.indentable:
        index = fmt.sep('', [str(self.idx)])
        res = fmt.block('[' + str(index) + ': ', ']', [])
        if self.v is not None:
            res.lsdata.append(self.v.to_fmt())
        return res

    def __repr__(self) -> str:
        return str(self.to_fmt())

class MatchKey(MatchExpr, StateBuilder):
    def __init__(self, key: str, v=None):
        self.key = key
        self.v = v

    def __eq__(self, other) -> bool:
        return self.key == other.key

    def is_in_state(self, s: state.State):
        return self.key in s.keys

    def attach(self, s1: state.State, s2: state.State, sr: state.StateRegister):
        s1.matchKey(self.key, s2)

    def build_state_tree(self, tree: StateBuilder):
        if self.v is not None:
            self.v.build_state_tree(tree)
        tree.add_match(self)

    def to_fmt(self) -> fmt.indentable:
        key = fmt.sep('', [repr(self.key)])
        res = fmt.block('{' + str(key) + ': ', '}', [])
        if self.v is not None:
            res.lsdata.append(self.v.to_fmt())
        else:
            res.lsdata.append('?')
        return res

    def __repr__(self) -> str:
        return str(self.to_fmt())

class MatchAttr(MatchExpr, StateBuilder):
    def __init__(self, name: str=None, v=None):
        self.name = name
        self.v = v

    def __eq__(self, other) -> bool:
        return self.name == other.name

    def is_in_state(self, s: state.State):
        return self.name in s.attrs

    def attach(self, s1: state.State, s2: state.State, sr: state.StateRegister):
        if self.name is not None:
            s1.matchAttr(self.name, s2)
        else:
            s1.matchDefault(s2)

    def build_state_tree(self, tree: StateBuilder):
        if self.v is not None:
            self.v.build_state_tree(tree)
        #TODO: match all attr
        tree.add_match(self)
        return tree

    def to_fmt(self) -> fmt.indentable:
        n = None
        if self.name is None:
            n = '.?'
        else:
            n = '.' + self.name
        res = fmt.block(n, '', [])
        if self.v is not None:
            res.lsdata.append('=' + str(self.v.to_fmt()))
        return res

    def __repr__(self) -> str:
        return str(self.to_fmt())

class MatchValue(MatchExpr, StateBuilder):
    def __init__(self, v=None):
        self.v = v

    def __eq__(self, other) -> bool:
        return self.v == other.v

    def is_in_state(self, s: state.State):
        return self.v in s.values

    def attach(self, s1: state.State, s2: state.State, sr: state.StateRegister):
        if self.v is not None:
            s1.matchValue(self.v, s2)
        # TODO: else: matchAllValue

    def build_state_tree(self, tree: StateBuilder):
        if self.v is not None:
            tree.add_match(self)

    def to_fmt(self) -> fmt.indentable:
        res = fmt.sep('', [])
        if self.v is not None:
            res.lsdata.append(repr(self.v))
        else:
            res.lsdata.append('?')
        return res

    def __repr__(self) -> str:
        return str(self.to_fmt())

class MatchType(MatchExpr, StateBuilder):
    def __init__(self, t: type=object, attrs: [MatchExpr]=None, strict=True):
        self.t = t
        self.attrs = attrs
        self.strict = strict

    def __eq__(self, other) -> bool:
        return self.t is other.t

    def is_in_state(self, s: state.State):
        return self.t in s.types

    def attach(self, s1: state.State, s2: state.State, sr: state.StateRegister):
        if self.t is not object:
            s1.matchType(self.t, s2)
        # TODO: else: matchAllType

    def build_state_tree(self, tree: StateBuilder):
        precond = None
        if self.attrs is not None:
            # TODO: attr with unknown name... after all other attr
            if self.strict:
               for a in self.attrs:
                    a.build_state_tree(tree)
            else:
                list_alt = []
                list_ev = []
                idx = 0
                for a in self.attrs:
                    # add a new event...
                    ev_name = 'E' + str(id(self)) + '_' + str(idx)
                    ev = MatchEvent(ev_name, a)
                    b = StateSeqBuilder()
                    ev.build_state_tree(b)
                    list_alt.append(b)
                    list_ev.append(ev_name)
                    idx += 1
                # add match event for the computed precond...
                list_expr = []
                for e in list_ev:
                    list_expr.append(state.EventNamed(e))
                precond = MatchPrecond(state.EventSeq(list_expr))
                tree.add_match(list_alt)
        if self.t is not object:
            tree.add_match(self)
        if precond is not None:
            tree.add_match(precond)

    def to_fmt(self) -> fmt.indentable:
        res = fmt.sep('', [])
        if self.t is not object:
            res.lsdata.append(self.t.__name__)
        else:
            res.lsdata.append('?')
        iparen = []
        if self.attrs is not None:
            # TODO: render unknown attr (.?) at the end after ..., also unknown attr implie 'unstrict' mode
            iparen = fmt.sep(', ', [])
            for a in self.attrs:
                iparen.lsdata.append(a.to_fmt())
        if not self.strict:
            iparen.lsdata.append('...')
        paren = fmt.block('(', ')', iparen)
        res.lsdata.append(paren)
        return res

    def __repr__(self) -> str:
        return str(self.to_fmt())

class MatchPrecond(MatchExpr, StateBuilder):
    def __init__(self, precond: state.EventExpr, v: MatchValue=None):
        self.precond = precond
        self.v = v

    def __eq__(self, other) -> bool:
        return id(self.precond) == id(other.precond)

    def is_in_state(self, s: state.State):
        return self.precond in s.events_expr

    def attach(self, s1: state.State, s2: state.State, sr: state.StateRegister):
        s1.matchEventExpr(self.precond, s2)

    def build_state_tree(self, tree: StateBuilder):
        if self.v is not None:
            self.v.build_state_tree(tree)
        tree.add_match(self)

    def to_fmt(self) -> fmt.indentable:
        res = fmt.sep('', [])
        if self.v is not None:
            res.lsdata.append(self.v.to_fmt())
        res.lsdata.append('<' + repr(self.precond) + '>')
        return res

    def __repr__(self) -> str:
        return str(self.to_fmt())

class MatchEvent(MatchExpr, StateBuilder):
    def __init__(self, n: str, v: MatchValue):
        self.n = n
        self.v = v

    def __eq__(self, other) -> bool:
        return self.n == other.n

    def attach(self, s1: state.State, s2: state.State, sr: state.StateRegister):
        s1.matchEvent(self.n, s2)

    def build_state_tree(self, tree: StateBuilder):
        self.v.build_state_tree(tree)
        tree.add_match(self)

    def to_fmt(self) -> fmt.indentable:
        res = fmt.sep(' -> ', [self.v.to_fmt(), '<' + self.n + '>;'])
        return res

    def __repr__(self) -> str:
        return str(self.to_fmt())

class MatchHook(MatchExpr, StateBuilder):
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

    def build_state_tree(self, tree: StateBuilder):
        self.v.build_state_tree(tree)
        tree.add_match(self)

    def to_fmt(self) -> fmt.indentable:
        res = fmt.sep(' -> ', [self.v.to_fmt(), '#' + self.n + ';'])
        return res

    def __repr__(self) -> str:
        return str(self.to_fmt())

##############

class Edge:
    def __init__(self, s: state.State):
        self.s = s
        self.next_state = []

    def get_next_state(self, m: MatchExpr):
        # if we manage this event, we have only one next_state
        if hasattr(m, 'is_in_state') and m.is_in_state(self.s):
            return self.next_state[-1]
        # if we have many next_state, could be one manage it
        for n in self.next_state:
            if hasattr(m, 'is_in_state') and m.is_in_state(n.s):
                return n
        return None

def populate_from_sequence(seq: StateBuilder, r, sr: state.StateRegister):
    base_state = r
    for m in seq.ls:
        # alternatives are represented by builtin list
        if isinstance(m, list):
            for item in m:
                populate_from_sequence(item, r, sr)
        elif isinstance(m, MatchExpr):
            # from the current state, have we a existing edge for this event?
            eX = r().get_next_state(m)
            if eX is None:
                sX = state.State(sr)
                sX.matchDefault(base_state().s)
                eX = Edge(sX)
                r().next_state.append(eX)
                m.attach(r().s, sX, sr)
            r = ref(eX)

def populate_state_register(all_seq: [StateBuilder], sr: state.StateRegister):
    # Walk on all sequence and connect state for all contiguous sequences
    s0 = state.State(sr)
    sr.set_default_state(s0)
    e0 = Edge(s0)
    for seq in all_seq:
        r = ref(e0)
        populate_from_sequence(seq, r, sr)

class MatchBlock(MatchExpr, StateBuilder):
    def __init__(self, stmts: [MatchExpr]):
        self.stmts = stmts

    def build_state_tree(self, tree: StateBuilder, sr: state.StateRegister):
        all_seq = []
        for stmt in self.stmts:
            part_seq = StateSeqBuilder()
            stmt.build_state_tree(part_seq)
            all_seq.append(part_seq)
        # Walk on all sequence and connect state for all contiguous sequences
        populate_state_register(all_seq, sr)

    def to_fmt(self) -> fmt.indentable:
        res = fmt.block('{\n', '}', [fmt.tab([])])
        lines = res.lsdata[0].lsdata
        for stmt in self.stmts:
            lines.append(fmt.end('\n', stmt.to_fmt()))
        return res

    def __repr__(self) -> str:
        return str(self.to_fmt())
