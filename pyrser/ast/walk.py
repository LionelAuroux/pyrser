"""
This module implements a generic walking method for all pyrser.parsing.node.
"""

from pyrser import meta
from pyrser.parsing import node
from pyrser.ast import state


@meta.add_method(node.Node)
def walk(self, lc: state.LivingContext, user_data=None, parent=None):
    """
    TODO: should_test_type??
    """
    global _cacheid
    # root node autorefence
    if parent is None:
        parent = self
    ## walk attributes
    if hasattr(self, '__dict__') and not isinstance(self, node.ListNode):
        for k in sorted(vars(self).keys()):
            print("RECURS key %s ID %d" % (k, id(getattr(self, k))))
            walk(getattr(self, k), lc, user_data, self)
            # k == ?
            #print('test attr .%s' % k)
            lc.checkAttr(k, self)
            # check precond
            lc.checkEventExpr()
            # do sub Event (for unstrict mode)
            lc.doSubEvent()
    # ...as dict, walk values, match keys
    if hasattr(self, 'keys'):
        for k in sorted(self.keys()):
            #print("RECURS ID %d" % id(self[k]))
            walk(self[k], lc, user_data, self)
            # k == ?
            #print('test key [%s]' % repr(k))
            lc.checkKey(k, self)
            # check precond
            lc.checkEventExpr()
            # do sub Event (for unstrict mode)
            lc.doSubEvent()
    # ...as list, walk values, match indices
    elif not isinstance(self, str) and hasattr(self, '__iter__'):
        idx = 0
        for i in self:
            #print("RECURS ID %d" % id(i))
            walk(i, lc, user_data, self)
            # idx == ?
            #print('test indice [%s]' % str(idx))
            lc.checkIndice(idx, self)
            idx += 1
            # check precond
            lc.checkEventExpr()
            # do sub Event (for unstrict mode)
            lc.doSubEvent()
    # ...type or value
    # type(self) == ?
    #print("test type %s" % type(self))
    lc.checkType(type(self), self, parent)
    # self == ?
    #print("test value %s" % str(self))
    lc.checkValue(self)
    ## Check EVENTS
    # TODO: what if the event do something
    # but don't change current state and default change it!!!
    lc.checkEventExpr()
    #print("RESULT")
    # check Event
    lc.doResultEvent()
    # check Hook
    lc.doResultHook(self, user_data, parent)
    # no transition, fallback to default
    lc.doDefault()
    # maintain the pool of LivingState
    lc.resetLivingState()
