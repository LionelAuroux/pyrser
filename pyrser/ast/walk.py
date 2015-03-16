from pyrser import meta
from pyrser.parsing import node
from pyrser.ast import state

@meta.add_method(node.Node)
def walk(self, s: state.State):
    olds = s
    ## walk attributes
    if hasattr(self, '__dict__'):
        for k in sorted(vars(self).keys()):
            print('.%s' % k)
            s = walk(getattr(self, k), s)
            # k == ?
            s = s.checkAttr(k, self)
    # ...as dict, walk values, match keys
    if hasattr(self, 'keys'):
        for k in sorted(self.keys()):
            print('[%s]' % repr(k))
            s = walk(self[k], s)
            # k == ?
            s = s.checkKey(k, self)
    # ...as list, walk values, match indices
    elif not isinstance(self, str) and hasattr(self, '__iter__'):
        idx = 0
        for i in self:
            print('[%s]' % str(idx))
            s = walk(i, s)
            # idx == ?
            s = s.checkIndice(idx, self)
            idx += 1
    # ...type/value
    else:
        #dbg
        if hasattr(self, '__str__'):
            print("it's a value: %s" % self)
        #  self == ?
        s = s.checkValue(self, self)
    # type(self) == ?
    s = s.checkType(self, self)
    ## Check EVENTS
#TODO: what if the event do something but don't change current state and default change if!!!
    s = s.checkEvent(self)
    if id(s) == id(olds):
        # no transition, fallback to default
        s = s.doDefault(self)
    return s
