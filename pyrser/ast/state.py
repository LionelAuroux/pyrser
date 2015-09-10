"""
This module implement the states classes for tree automata.
"""

from pyrser import fmt
import os
import weakref
import pipes
import tempfile

# just a forward declaration -- for annotation
class State: pass

class StateRegister():
    """
    All State belongs to a global register that manage named events.
    """
    def __init__(self, named_events: dict={}, label=None):
        # default state
        self.__default = None
        # all state belonging to this register
        self.states = dict()
        # label store the string representation of the PSL expression that is responsible of all these states
        self.label = label
        # handle events
        self.named_events = named_events

    def cleanAll(self):
        """
        Set all events to empty.
        """
        self.named_events.clear()

    def set_default_state(self, s: State):
        if id(s) not in self.states:
            raise ValueError("%d not in StateRegister" % id(s))
        self.__default = s

    @property
    def default(self) -> State:
        return self.__default

    def add_state(self, s: State):
        """
        all state in the register have a uid
        """
        ids = id(s)
        uid = len(self.states)
        if ids not in self.states:
            self.states[ids] = (uid, s)

    def get_uid(self, s: State) -> int:
        if id(s) not in self.states:
            raise ValueError("%d not in StateRegister" % id(s))
        return self.states[id(s)][0]

    def __contains__(self, s: State) -> bool:
        sts = set(list(self.states.keys()))
        return id(s) in sts

    def to_dot(self) -> str:
        """
        Provide a '.dot' representation of all State in the register.
        """
        txt = ""
        txt += "digraph S%d {\n" % id(self)
        if self.label is not None:
            txt += '\tlabel="%s";\n' % (self.label + '\l').replace('\n', '\l')
        txt += "\trankdir=LR;\n"
        #txt += '\tlabelloc="t";\n'
        txt += '\tgraph [labeljust=l, labelloc=t, nojustify=true];\n'
        txt += "\tesep=1;\n"
        txt += '\tranksep="equally";\n'
        txt += "\tnode [shape = circle];\n"
        txt += "\tsplines = ortho;\n"
        for s in self.states.values():
            txt += s[1].to_dot()
        txt += "}\n"
        return txt

    def to_dot_file(self, fname: str):
        """
        write a '.dot' file.
        """
        with open(fname, 'w') as f:
            f.write(self.to_dot())

    def to_png_file(self, fname: str):
        """
        write a '.png' file.
        """
        cmd = pipes.Template()
        cmd.append('dot -Tpng > %s' % fname, '-.')
        with cmd.open('pipefile', 'w') as f:
            f.write(self.to_dot())

    def to_fmt(self) -> str:
        """
        Provide a useful representation of the register.
        """
        infos = fmt.end(";\n", [])
        s = fmt.sep(', ', [])
        for ids in sorted(self.states.keys()):
            s.lsdata.append(str(ids))
        infos.lsdata.append(fmt.block('(', ')', [s]))
        infos.lsdata.append("events:" + repr(self.events))
        infos.lsdata.append("named_events:" + repr(list(self.named_events.keys())))
        infos.lsdata.append("uid_events:" + repr(list(self.uid_events.keys())))
        return infos

    def __repr__(self) -> str:
        return str(self.to_fmt())

class EventExpr:
    """
    Ast Node for predicate Expression.
    """
    def checkEvent(self, sr: StateRegister, collect: dict) -> bool:
        return False

    def clean(self, sr: StateRegister, updown: bool):
        pass

class EventAlt(EventExpr):
    """
    Ast Node for a alternative predicate expression.
    """
    def __init__(self, alt: list):
        self.alt = alt

    def checkEvent(self, sr: StateRegister, collect: dict) -> bool:
        res = False
        for a in self.alt:
            b = a.checkEvent(sr, collect)
            res |= b
        return res

    def clean(self, sr: StateRegister, updown: bool) -> bool:
        for a in self.alt:
            a.clean(sr, updown)

    def to_fmt(self) -> fmt.indentable:
        res = fmt.sep(' | ', [])
        for a in self.alt:
            res.lsdata.append(a.to_fmt())
        return res

    def __repr__(self) -> str:
        return str(self.to_fmt())

class EventSeq(EventExpr):
    """
    Ast Node for a sequence predicate expression.
    """
    def __init__(self, seq: list):
        self.seq = seq

    def checkEvent(self, sr: StateRegister, collect: dict) -> bool:
        res = True
        for s in self.seq:
            b = s.checkEvent(sr, collect)
            res &= b
        return res

    def clean(self, sr: StateRegister, updown: bool) -> bool:
        for s in self.seq:
            s.clean(sr, updown)

    def to_fmt(self) -> fmt.indentable:
        res = fmt.sep(' & ', [])
        for s in self.seq:
            res.lsdata.append(s.to_fmt())
        return res

    def __repr__(self) -> str:
        return str(self.to_fmt())

class EventNot(EventExpr):
    """
    Ast Node for a not predicate expression.
    """
    def __init__(self, subexpr: EventExpr):
        self.subexpr = subexpr

    def checkEvent(self, sr: StateRegister, collect: dict) -> bool:
        c2 = {}
        r = not self.subexpr.checkEvent(sr, c2)
        return r

    def clean(self, sr: StateRegister, updown: bool) -> bool:
        self.subexpr.clean(sr, not updown)

    def to_fmt(self) -> fmt.indentable:
        res = fmt.block('!', '', [self.subexpr.to_fmt()])
        return res

    def __repr__(self) -> str:
        return str(self.to_fmt())

class EventParen(EventExpr):
    """
    Ast Node for a parenthesis predicate expression.
    """
    def __init__(self, subexpr: EventExpr):
        self.subexpr = subexpr

    def checkEvent(self, sr: StateRegister, collect: dict) -> bool:
        return self.subexpr.checkEvent(sr, collect)

    def clean(self, sr: StateRegister, updown: bool) -> bool:
        self.subexpr.clean(sr, updown)

    def to_fmt(self) -> fmt.indentable:
        res = fmt.block('(', ')', [self.subexpr.to_fmt()])
        return res

    def __repr__(self) -> str:
        return str(self.to_fmt())

class EventNamed(EventExpr):
    """
    Ast Node for a named predicate expression.
    """
    def __init__(self, name: str):
        self.name = name

    def checkEvent(self, sr: StateRegister, collect: dict) -> bool:
        if self.name in sr.named_events:
            collect[self.name] = True
            return True
        return False

    def clean(self, sr: StateRegister, updown: bool) -> bool:
        self.subexpr.clean(sr, updown)

    def to_fmt(self) -> fmt.indentable:
        return self.name

    def __repr__(self) -> str:
        return str(self.to_fmt())

class State:
    """
    Base class for a State and his transitions.
    """
    def __init__(self, sr: StateRegister):
        # register this state
        sr.add_state(self)
        self.state_register = sr
        # for predicates
        self.state_event = None
        self.events_expr = list()
        self.precond = None
        # for matching
        self.attrs = dict()
        self.indices = dict()
        self.keys = dict()
        self.values = dict()
        # wildcards
        self.wild_value = False
        self.wild_indice = False
        #...
        self.minsubelmt = 0
        # for exact type
        self.types_list = list()
        self.types = dict()
        # for iskind of type
        self.ktypes_list = list()
        self.ktypes = dict()
        # for defaults
        self.default_event = None
        self.default_hook = None
        self.default = None

    def nextstate(self, newstate, thenode=None, user_data=None, nodes: list=None):
        """
        Manage transition of state.
        """
        if newstate is None:
            return self
        if isinstance(newstate, State) and id(newstate) != id(self):
            return newstate
        elif isinstance(newstate, StateEvent):
            self.state_register.named_events[newstate.name] = True
            return newstate.st
        elif isinstance(newstate, StatePrecond):
            return newstate.st
        elif isinstance(newstate, StateHook):
            ##TODO ??? rewriting? rethink the API...
            newstate.call(thenode, user_data, nodes)
            return newstate.st
        return self

    ### Custom Named Events
    ## we could write boolean expression of events...

    def checkEventExpr(self) -> State:
        # check all free events Expressions...
        for e in self.events_expr:
            collect = {}
            if e.expr.checkEvent(self.state_register, collect):
                # TODO: clean or not event
                if e.clean_event:
                    for k in collect.keys():
                        del self.state_register.named_events[k]
                return self.nextstate(e)
        return self

    def matchEvent(self, n, state: State):
        # state Result Event
        se = StateEvent(n, state)
        self.default_event = se

    def matchEventExpr(self, e: EventExpr, state: State, clean_event: bool):
        # match Event Expression
        se = StatePrecond(e, state, clean_event)
        self.events_expr.append(se)

    ### ATTR

    def checkAttr(self, a) -> State:
        if a in self.attrs:
            return self.nextstate(self.attrs[a])
        return self

    def matchAttr(self, a, state: State):
        self.attrs[a] = state

    ### INDICE

    def checkIndice(self, i) -> State:
        if self.wild_indice:
            print("WILD INDEX")
            return self.nextstate(self.indices['*'])
        elif i in self.indices:
            return self.nextstate(self.indices[i])
        return self

    def matchIndice(self, i, state: State):
        if i is None:
            self.wild_indice = True
            self.indices['*'] = state
        else:
            self.indices[i] = state

    ### KEY

    def checkKey(self, k) -> State:
        if k in self.keys:
            return self.nextstate(self.keys[k])
        return self

    def matchKey(self, k, state: State):
        self.keys[k] = state

    ### TYPE (exact type)

    def checkKindOfType(self, t) -> State:
        for it in self.ktypes_list:
            if issubclass(t, it):
                return self.nextstate(self.ktypes[it.__name__])
        return self

    def checkType(self, t) -> State:
        for k in self.types.keys():
            if t.__name__ == k:
                return self.nextstate(self.types[k])
        return self

    def matchKindType(self, t, state: State):
        if type(t) is not type:
            raise ValueError("parameter 't' is a type")
        # TODO: check if an subclass object is the list...
        self.ktypes_list.append(t)
        self.ktypes[t.__name__] = state

    def matchType(self, t, state: State):
        if type(t) is not type:
            raise ValueError("parameter 't' is a type")
        # TODO: check if an subclass object is the list...
        self.types_list.append(t)
        self.types[t.__name__] = state

    ### VALUE

    def checkValue(self, v) -> State:
        """the str() of Values are stored internally for convenience"""
        if self.wild_value:
            return self.nextstate(self.values['*'])
        elif str(v) in self.values:
            return self.nextstate(self.values[str(v)])
        return self

    def matchValue(self, v, state: State):
        if v is None:
            self.wild_value = state
            self.values['*'] = state
        else:
            self.values[str(v)] = state

    ### HOOK

    def matchHook(self, call, state: State):
        self.default_hook = StateHook(call, state)

    ### DEFAULT

    def doResultHook(self, thenode=None, user_data=None, nodes: list=None) -> State:
        return self.nextstate(self.default_hook, thenode, user_data, nodes)

    def doResultEvent(self) -> State:
        return self.nextstate(self.default_event)

    def doDefault(self) -> State:
        return self.nextstate(self.default)

    def matchDefault(self, state: State):
        self.default = state

    # internal transition
    def cleanAll(self):
        self.state_register.cleanAll()

    def _str_state(self, s) -> str:
        if isinstance(s, State):
            return str(id(s))
        return repr(s)

    def _dot_state(self, s) -> str:
        return 'S' + str(self.state_register.get_uid(s))

    def _dot_relation(self, s, label) -> str:
        txt = ""
        dst = ""
        if isinstance(s, StateEvent):
            dst = "ent" + str(id(s))
            txt += "\t" + dst + ' [shape=box xlabel="<' + s.name + '>"];\n'
            txt += "\t" + dst + ' -> ' + self._dot_state(s.st) + ';\n'
        elif isinstance(s, StatePrecond):
            dst = "ent" + str(id(s))
            txt += "\t" + dst + ' [shape=box xlabel=" ? (' + s.txtevent + ')"];\n'
            txt += "\t" + dst + ' -> ' + self._dot_state(s.st) + ';\n'
        elif isinstance(s, StateHook):
            dst = "ent" + str(id(s))
            txt += "\t" + dst + ' [shape=box xlabel="' + repr(s.call) + '"];\n'
            txt += "\t" + dst + ' -> ' + self._dot_state(s.st) + '[xlabel = "return"];\n'
        else:
            dst = self._dot_state(s)
        txt += "\t" + self._dot_state(self) + ' -> ' + dst + ' [xlabel = "' + label + '" ];\n'
        return txt

    def to_dot(self) -> str:
        txt = ""
        if len(self.events_expr) > 0:
            for e in self.events_expr:
                txt += self._dot_relation(e, '')
        if len(self.attrs) > 0:
            for k in sorted(self.attrs.keys()):
                event = self.attrs[k]
                txt += self._dot_relation(event, '.' + k)
        if len(self.indices) > 0:
            for k in sorted(self.indices.keys()):
                event = self.indices[k]
                txt += self._dot_relation(event, '[' + repr(k) + ']')
        if len(self.keys) > 0:
            for k in sorted(self.keys.keys()):
                event = self.keys[k]
                txt += self._dot_relation(event, '{' + repr(k) + '}')
        if len(self.types) > 0:
            for k in sorted(self.types.keys()):
                event = self.types[k]
                txt += self._dot_relation(event, k + '(...)')
        if len(self.values) > 0:
            for k in sorted(self.values.keys()):
                event = self.values[k]
                txt += self._dot_relation(event, '=' + k)
        if self.default_hook is not None:
            txt += self._dot_relation(self.default_hook, 'hook')
        if self.default_event is not None:
            txt += self._dot_relation(self.default_event, 'event')
        if self.default is not None and self.default is not self.state_register.default:
            txt += self._dot_relation(self.default, '...')
        elif self.default is None:
            nodename = self._dot_state(self)
            txt += "\t" + nodename + '[label="' + nodename + '*"];\n'
        return txt

    def __repr__(self):
        # to expand for dbg
        txt = ""
        if len(self.events_expr) > 0:
            txt += "EXPR EVENT:\n"
            for e in self.events_expr:
                txt += repr(e) + '\n'
            txt += '-----\n'
        if len(self.attrs) > 0:
            txt += "ATTR EVENT:\n"
            for k in sorted(self.attrs.keys()):
                txt += repr(k) + ': ' + self._str_state(self.attrs[k]) + '\n'
            txt += '-----\n'
        if len(self.indices) > 0:
            txt += "INDICE EVENT:\n"
            for k in sorted(self.indices.keys()):
                txt += repr(k) + ': ' + self._str_state(self.indices[k]) + '\n'
            txt += '-----\n'
        if len(self.keys) > 0:
            txt += "KEY EVENT:\n"
            for k in sorted(self.keys.keys()):
                txt += repr(k) + ': ' + self._str_state(self.keys[k]) + '\n'
            txt += '-----\n'
        if len(self.types) > 0:
            txt += "TYPE EVENT:\n"
            for k in sorted(self.types.keys()):
                txt += repr(k) + ': ' + self._str_state(self.types[k]) + '\n'
            txt += '-----\n'
        if len(self.values) > 0:
            txt += "VALUE EVENT:\n"
            for k in sorted(self.values.keys()):
                txt += repr(k) + ': ' + self._str_state(self.values[k]) + '\n'
            txt += '-----\n'
        if self.default_hook is not None:
            txt += self._dot_relation(self.default_hook, 'hook')
        if self.default_event is not None:
            txt += self._dot_relation(self.default_event, 'event')
        if self.default is not None and self.default is not self.state_register.default:
            txt += "DEFAULT: %s\n" % self._str_state(self.default)
        return txt

class StateHook:
    """
    State for handling Resulting Hooks.
    """
    def __init__(self, call: callable, st: State):
        if not callable(call):
            raise ValueError("'call' argument must be a callable")
        self.call = call
        self.st = st

class StateEvent:
    """
    State for handling Resulting Event.
    """
    def __init__(self, n: str, st: State):
        self.name = n
        self.st = st

class StatePrecond:
    """
    State for handling Precondition using predicates.
    """
    def __init__(self, e: EventExpr, st: State, clean_event: bool):
        self.expr = e
        self.txtevent = repr(e)
        self.st = st
        self.clean_event = clean_event

    def to_fmt(self) -> fmt.indentable:
        res = fmt.sep(' : ', [])
        res.lsdata.append(self.txtevent)
        res.lsdata.append(id(self.st))
        res.lsdata.append(self.clean_event)
        return res

    def __repr__(self) -> str:
        return str(self.to_fmt())

class CaptureNode:
    kinds = {'Node', 'Attr', 'Indice', 'Key'}

    def __init__(self, kind: str, parent: None):
        if kind not in CaptureNode.kinds:
            raise ValueError("kind parameter not in %s" % repr(CaptureNode.kinds))
        # kind of CaptureNode
        self.kind = kind
        # parent object for modification
        self.parent = parent
        # the matched node
        self.node = None
        # value of attr/indice/key or None (when Node)
        self.value = None
        # recursively detail if in the pattern we provide the detail
        self.detail = None

    def to_fmt(self) -> fmt.indentable:
        res = fmt.sep('\n', [])
        res.lsdata.append("kind: %s" % self.kind)
        if self.parent is not None:
            res.lsdata.append("parent: %d" % id(self.parent))
        res.lsdata.append("node: %d" % id(self.node))
        return res

    def __repr__(self) -> str:
        return str(self.to_fmt())

class CaptureNodeDetail:
    def __init__(self):
        # contain list of CaptureNode
        self.attrs = []
        self.indices = []
        self.keys = []

    def to_fmt(self) -> fmt.indentable:
        return None

    def __repr__(self) -> str:
        return str(self.to_fmt())

class CollectContext(list):
    def __init__(self, ls, old_ref, la, lk, li):
        super(self.__class__, self).__init__(ls)
        self.old_ref = old_ref
        self.last_attr = la
        self.last_key = lk
        self.last_index = li

class LivingState:
    """
    State instances in a StateRegister represents all the tree automata but only LivingState that reference a State instance are used during the walk.
    """
    def __init__(self, s: State):
        self.alive = False
        self.have_finish = False
        self.thestate = weakref.ref(s)
        #TODO: chain named event from StateRegister for unknown event????
        # collect all matched nodes
        self.matched_nodes = []
        self.old_ref = []
        self.last_index = None
        self.last_key = None
        self.last_attr = None
        # for attrs,indices,keys collect id of parents
        self.subelmt = []

    #TODO: forward call to internal state
    def checkEventExpr(self):
        s = self.thestate().checkEventExpr()
        if id(s) != id(self.thestate()):
            self.thestate = weakref.ref(s)
            self.alive = True

    def checkAttr(self, a, parent=None):
        s = self.thestate().checkAttr(a)
        if id(s) != id(self.thestate()):
            self.last_attr = a
            self.subelmt.append(id(parent))
            self.thestate = weakref.ref(s)
            self.alive = True

    def checkIndice(self, i, parent=None):
        s = self.thestate().checkIndice(i)
        if id(s) != id(self.thestate()):
            self.last_index = i
            self.subelmt.append(id(parent))
            self.thestate = weakref.ref(s)
            self.alive = True

    def checkKey(self, k, parent=None):
        s = self.thestate().checkKey(k)
        if id(s) != id(self.thestate()):
            self.last_key = k
            self.subelmt.append(id(parent))
            self.thestate = weakref.ref(s)
            self.alive = True

    def checkType(self, t, thenode=None):
        statetype = self.thestate()
        # count the number of subelmt that belong to this type
        nsubelm = 0
        toremove = []
        l = len(self.subelmt)
        for idx, subelmtid in zip(range(l), self.subelmt):
            if id(thenode) == subelmtid:
                toremove.append(idx)
                nsubelm += 1
        # check the num min of subelmt associate with this type
        if nsubelm >= statetype.minsubelmt:
            s = self.thestate().checkType(t)
            if id(s) == id(self.thestate()):
                s = self.thestate().checkKindOfType(t)
            if id(s) != id(self.thestate()):
                print("ADD THENODE: %s" % thenode)
                # TODO: think a better way to store in // old ref for ancestors...siblings...
                self.matched_nodes.append(thenode)
                self.old_ref.append((self.last_attr, self.last_key, self.last_index))
                self.thestate = weakref.ref(s)
                self.alive = True
        for idx in reversed(toremove):
            self.subelmt.pop(idx)

    def checkValue(self, v):
        s = self.thestate().checkValue(v)
        if id(s) != id(self.thestate()):
            self.thestate = weakref.ref(s)
            self.alive = True

    def doResultHook(self, thenode=None, user_data=None, parent=None):
        #TODO: do the list nodes
        tmp = []
        if self.matched_nodes is not None:
            tmp = self.matched_nodes
        tmp = CollectContext(tmp + [parent], self.old_ref, self.last_attr, self.last_key, self.last_index)
        s = self.thestate().doResultHook(thenode, user_data, tmp)
        if id(s) != id(self.thestate()):
            print("RESET MATCHED NODES HOOK")
            self.matched_nodes = []
            self.old_ref = []
            self.thestate = weakref.ref(s)
            self.alive = True

    def doResultEvent(self):
        # TODO: event stored in the LivingState
        olds = self.thestate()
        s = self.thestate().doResultEvent()
        if id(s) != id(self.thestate()):
            print("RESET MATCHED NODES EV")
            self.matched_nodes = []
            self.old_ref = []
            self.thestate = weakref.ref(s)
            self.alive = True

    def doDefault(self):
        # TODO: ??? kill livingState in LivingContext??
        s = self.thestate().doDefault()
        if id(s) != id(self.thestate()):
            print("RESET MATCHED NODES DEFAULT")
            self.matched_nodes = []
            self.old_ref = []
            self.thestate = weakref.ref(s)
            self.alive = True

class LivingContext:
    """
    Create & Destroy Living State during tree walking for a current StateRegister.
    """
    def __init__(self):
        self.mblock = []
        self.nsr = []
        self.ls = []
        self.named_events = {}

    def add_match_block(self, m):
        self.mblock.append(m)

    def build_automata(self):
        for b in self.mblock:
            tree = list()
            nsr = StateRegister(named_events=self.named_events)
            b.build_state_tree(tree, nsr)
            nsr.label = repr(b)
            self.nsr.append(nsr)
        self.ls = []
        self.init_all()

    def init_all(self):
        for nsr in self.nsr:
            self.ls.append((nsr.default, LivingState(nsr.default)))

    def is_in_stable_state(self) -> bool:
        return len(self.nsr) == len(self.ls)

    #TODO: forward call to internal state
    def checkEventExpr(self):
        for ls in self.ls:
            ls[1].checkEventExpr()

    def checkAttr(self, a, parent=None):
        for ls in self.ls:
            ls[1].checkAttr(a, parent)

    def checkIndice(self, i, parent=None):
        # TODO: must store indice and restore state...
        # if wildcard, type are not strict... so set an event after parsing all indices
        fork_state = []
        l = len(self.ls)
        for idx, ls in zip(range(l), self.ls):
            store_indice = False
            if ls[1].thestate().wild_indice:
                store_indice = True
            ls[1].checkIndice(i, parent)

    def checkKey(self, k, parent=None):
        for ls in self.ls:
            ls[1].checkKey(k, parent)

    def checkType(self, t, thenode=None):
        for ls in self.ls:
            ls[1].checkType(t, thenode)

    def checkValue(self, v):
        for ls in self.ls:
            ls[1].checkValue(v)

    def doResultHook(self, thenode=None, user_data=None, parent=None):
        for ls in self.ls:
            ls[1].doResultHook(thenode, user_data, parent)
            #TODO: check subEvent for put it in LivingState
            ls[1].have_finish = True

    def doSubEvent(self):
        # TODO: doSubEvent on livingState and State
        for ls in self.ls:
            ls[1].doResultEvent()

    def doResultEvent(self):
        for ls in self.ls:
            ls[1].doResultEvent()
            #TODO: check subEvent for put it in LivingState
            ls[1].have_finish = True

    def doDefault(self):
        for ls in self.ls:
            if ls[1].alive is False:
                ls[1].doDefault()

    def resetLivingState(self):
        """Only one Living State on the S0 of each StateRegister"""
        # TODO: add some test to control number of instanciation of LivingState
        # clean all living state on S0
        must_delete = []
        l = len(self.ls)
        for idx, ls in zip(range(l), self.ls):
            ls[1].alive = False
            ids = id(ls[1].thestate())
            # TODO: !!!
            if ids == id(ls[0]) and (ls[1].have_finish or not ls[1].alive):
                must_delete.append(idx)
        for delete in reversed(must_delete):
            self.ls.pop(delete)
        self.init_all()
    #############

    def to_dot(self) -> str:
        lscat = []
        for nsr in self.nsr:
            f = tempfile.NamedTemporaryFile(delete=False)
            f.close()
            lscat.append(f.name)
            nsr.to_dot_file(f.name)
        cmd = pipes.Template()
        cmd.prepend('gvpack 2>/dev/null -u ' + ' '.join(lscat), '.-')
        content = ""
        with cmd.open('pipefile', 'r') as f:
            content += f.read()
        for f in lscat:
            os.unlink(f)
        return content

    def to_dot_file(self, fname: str):
        with open(fname, 'w') as f:
            f.write(self.to_dot())

    def to_png_file(self, fname: str):
        cmd = pipes.Template()
        cmd.append('dot -Tpng > %s' % fname, '-.')
        with cmd.open('pipefile', 'w') as f:
            f.write(self.to_dot())
