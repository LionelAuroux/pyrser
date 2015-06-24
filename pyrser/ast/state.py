from pyrser import fmt

class State: pass

class StateRegister():
    def __init__(self, label=None):
        self.__default = None
        self.states = dict()
        self.label = label
        self.resetEvents()

    def resetEvents(self):
        self.events = set()
        self.named_events = dict()
        self.uid_events = dict()

    def set_default_state(self, s: State):
        if id(s) not in self.states:
            raise ValueError("%d not in StateRegister" % id(s))
        self.__default = s

    @property
    def default(self) -> State:
        return self.__default

    def add_state(self, s: State):
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
        with open(fname, 'w') as f:
            f.write(self.to_dot())

    def to_png_file(self, fname: str):
        import pipes
        cmd = pipes.Template()
        cmd.append('dot -Tpng > %s' % fname, '-.')
        with cmd.open('pipefile', 'w') as f:
            f.write(self.to_dot())

    def to_fmt(self) -> str:
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
    def checkEvent(self, sr: StateRegister) -> bool:
        return False

    def clean(self, sr: StateRegister, updown: bool):
        pass

class EventAlt(EventExpr):
    def __init__(self, alt: list):
        self.alt = alt

    def checkEvent(self, sr: StateRegister) -> bool:
        res = False
        for a in self.alt:
            b = a.checkEvent(sr)
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
    def __init__(self, seq: list):
        self.seq = seq

    def checkEvent(self, sr: StateRegister) -> bool:
        res = True
        for s in self.seq:
            b = s.checkEvent(sr)
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
    def __init__(self, subexpr: EventExpr):
        self.subexpr = subexpr

    def checkEvent(self, sr: StateRegister) -> bool:
        r = not self.subexpr.checkEvent(sr)
        return r

    def clean(self, sr: StateRegister, updown: bool) -> bool:
        self.subexpr.clean(sr, not updown)

    def to_fmt(self) -> fmt.indentable:
        res = fmt.block('!', '', [self.subexpr.to_fmt()])
        return res

    def __repr__(self) -> str:
        return str(self.to_fmt())

class EventParen(EventExpr):
    def __init__(self, subexpr: EventExpr):
        self.subexpr = subexpr

    def checkEvent(self, sr: StateRegister) -> bool:
        return self.subexpr.checkEvent(sr)

    def clean(self, sr: StateRegister, updown: bool) -> bool:
        self.subexpr.clean(sr, updown)

    def to_fmt(self) -> fmt.indentable:
        res = fmt.block('(', ')', [self.subexpr.to_fmt()])
        return res

    def __repr__(self) -> str:
        return str(self.to_fmt())

class EventNamed(EventExpr):
    def __init__(self, name: str):
        self.name = name

    def checkEvent(self, sr: StateRegister) -> bool:
        if self.name in sr.named_events:
            idevent = sr.named_events[self.name]
            return idevent.uid in sr.events
        return False

    def clean(self, sr: StateRegister, updown: bool) -> bool:
        self.subexpr.clean(sr, updown)

    def to_fmt(self) -> fmt.indentable:
        return self.name

    def __repr__(self) -> str:
        return str(self.to_fmt())

class State:
    def __init__(self, sr: StateRegister):
        sr.add_state(self)
        self.state_register = sr
        self.state_event = None
        self.events_expr = list()
        self.precond = None
        self.attrs = dict()
        self.indices = dict()
        self.keys = dict()
        self.types_list = list()
        self.types = dict()
        self.values = dict()
        self.default_event = None
        self.default_hook = None
        self.default = None

    def nextstate(self, newstate, tree, user_data):
        if newstate is None:
            return self
        if isinstance(newstate, State) and id(newstate) != id(self):
            return newstate
        elif isinstance(newstate, StateEvent):
            self.state_register.events |= {newstate.uid}
            return newstate.st
        elif isinstance(newstate, StatePrecond):
            #TODO: refresh or not state?
            # newstate.expr.clean(self.state_register, True)
            return newstate.st
        elif isinstance(newstate, StateHook):
            print("HOOK!!")
            ##TODO ??? rewriting?
            newnode = newstate.call(tree, user_data)
            return newstate.st
        #else:
        #    raise ValueError("Unknown object in state %s: %s" % (repr(newstate.state_register), repr(newstate)))
        return self

    ### Custom Named Events
    ## we could write boolean expression of events...

    def checkEventExpr(self, tree=None, user_data=None) -> State:
        # check all free events Expressions...
        # TODO: could be attach to default of the S0 state?
        for e in self.events_expr:
            if e.expr.checkEvent(self.state_register):
                return self.nextstate(e, tree, user_data)
        return self

    def matchEvent(self, n, state: State):
        # match Event Expression
        uid = None
        if n in self.state_register.named_events:
            uid = self.state_register.named_events[n].uid
        else:
            uid = len(self.state_register.named_events)
        se = StateEvent(n, uid, state)
        self.state_register.named_events[n] = se
        self.state_register.uid_events[uid] = se
        # store ids in the state
        self.state_event = uid
        self.default_event = se

    def matchEventExpr(self, e: EventExpr, state: State):
        uid = None
        # TODO: warning, if we compute unique event name we must rename it from parsing
        txtevent = repr(e)
        if txtevent in self.state_register.named_events:
            uid = self.state_register.named_events[txtevent].uid
        else:
            uid = len(self.state_register.named_events)
        se = StatePrecond(e, uid, state)
        self.state_register.named_events[txtevent] = se
        self.state_register.uid_events[uid] = se
        self.events_expr.append(se)

    ### ATTR

    def checkAttr(self, a, tree=None, user_data=None) -> State:
        if a in self.attrs:
            return self.nextstate(self.attrs[a], tree, user_data)
        return self

    def matchAttr(self, a, state: State):
        self.attrs[a] = state

    ### INDICE

    def checkIndice(self, i, tree=None, user_data=None) -> State:
        if i in self.indices:
            return self.nextstate(self.indices[i], tree, user_data)
        return self

    def matchIndice(self, i, state: State):
        self.indices[i] = state

    ### KEY

    def checkKey(self, k, tree=None, user_data=None) -> State:
        if k in self.keys:
            return self.nextstate(self.keys[k], tree, user_data)
        return self

    def matchKey(self, k, state: State):
        self.keys[k] = state

    ### TYPE (exact type)

    def checkType(self, t, tree=None, user_data=None) -> State:
        print("on UID %d" % (self.state_register.get_uid(self)))
        for it in self.types_list:
            print("CHECK TYPE %r" % it)
            if isinstance(t, it) or t is it:
                return self.nextstate(self.types[it.__name__], tree, user_data)
        print("END TYPE")
        return self

    def matchType(self, t, state: State):
        if type(t) is not type:
            raise ValueError("parameter 't' is a type")
        # TODO: check if an subclass object is the list...
        self.types_list.append(t)
        self.types[t.__name__] = state

    ### VALUE

    def checkValue(self, v, tree=None, user_data=None) -> State:
        if str(v) in self.values:
            return self.nextstate(self.values[str(v)], tree, user_data)
        return self

    def matchValue(self, v, state: State):
        self.values[str(v)] = state

    ### HOOK

    def matchHook(self, call, state: State):
        self.default_hook = StateHook(call, state)

    ### DEFAULT

    def doDefaultHook(self, tree=None, user_data=None) -> State:
        return self.nextstate(self.default_hook, tree, user_data)

    def doDefaultEvent(self, tree=None, user_data=None) -> State:
        return self.nextstate(self.default_event, tree, user_data)

    def doDefault(self, tree=None, user_data=None) -> State:
        return self.nextstate(self.default, tree, user_data)

    def matchDefault(self, state: State):
        self.default = state

    # internal transition
    def cleanAll(self):
        self.state_register.events = set()

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
            txt += "\t" + dst + ' [shape=box xlabel="<?' + s.txtevent + '>"];\n'
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
    def __init__(self, call: callable, st: State):
        if not callable(call):
            raise ValueError("'call' argument must be a callable")
        self.call = call
        self.st = st

class StateEvent:
    def __init__(self, n: str, uid: int, st: State):
        self.name = n
        self.uid = uid
        self.st = st

class StatePrecond:
    def __init__(self, e: EventExpr, uid: int, st: State):
        self.expr = e
        self.txtevent = repr(e)
        self.uid = uid
        self.st = st

    def to_fmt(self) -> fmt.indentable:
        res = fmt.sep(' : ', [])
        res.lsdata.append(str(self.uid))
        res.lsdata.append(self.txtevent)
        res.lsdata.append(id(self.st))
        return res

    def __repr__(self) -> str:
        return str(self.to_fmt())
