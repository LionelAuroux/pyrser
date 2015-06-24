from pyrser import meta
from pyrser.parsing import node
from pyrser.ast import state

@meta.add_method(node.Node)
def walk(self, s: state.State, user_data=None):
    olds = s
    print("begin UID %d" % (s.state_register.get_uid(s)))
    ## walk attributes
    should_test_type = False
    if hasattr(self, '__dict__'):
        should_test_type = True
        for k in sorted(vars(self).keys()):
            print('.%s' % k)
            s = walk(getattr(self, k), s, user_data)
            # k == ?
            s = s.checkAttr(k, self, user_data)
            print("next UID attr %d" % (s.state_register.get_uid(s)))
    # ...as dict, walk values, match keys
    if hasattr(self, 'keys'):
        should_test_type = True
        for k in sorted(self.keys()):
            print('[%s]' % repr(k))
            s = walk(self[k], s, user_data)
            # k == ?
            s = s.checkKey(k, self, user_data)
            print("next UID key %d" % (s.state_register.get_uid(s)))
    # ...as list, walk values, match indices
    elif not isinstance(self, str) and hasattr(self, '__iter__'):
        should_test_type = True
        idx = 0
        for i in self:
            print('[%s]' % str(idx))
            s = walk(i, s, user_data)
            # idx == ?
            s = s.checkIndice(idx, self, user_data)
            print("next UID indice %d" % (s.state_register.get_uid(s)))
            idx += 1
    # ...type or value
    if should_test_type:
        print("test type")
        # type(self) == ?
        s = s.checkType(self, self, user_data)
        print("next UID type %d" % (s.state_register.get_uid(s)))
    else:
        #  self == ?
        s = s.checkValue(self, self, user_data)
        print("next UID value %d" % (s.state_register.get_uid(s)))
    ## Check EVENTS
    #TODO: what if the event do something but don't change current state and default change if!!!
    s = s.checkEventExpr(self, user_data)
    print("next UID event %d" % (s.state_register.get_uid(s)))
    # check Event
    s = s.doDefaultEvent(self, user_data)
    print("next UID default event %d" % (s.state_register.get_uid(s)))
    # check Hook
    s = s.doDefaultHook(self, user_data)
    print("next UID default hook %d" % (s.state_register.get_uid(s)))
    if id(s) == id(olds):
        # no transition, fallback to default
        s = s.doDefault(self, user_data)
        print("next UID default %d" % (s.state_register.get_uid(s)))
    return s
