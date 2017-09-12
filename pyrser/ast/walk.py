"""
This module implements a generic walking method for all pyrser.parsing.node.
"""

from pyrser import meta
from pyrser.parsing import node

not_normalized = {set, list, dict, tuple}
match_value = {int, float, str, bytes}

@meta.add_method(node.Node)
def walk(self, depth=0):
    """
    Work only on normalized tree
    """

    if type(self) in not_normalized:
        raise TypeError("Not a normalized tree! User node.normalize() function!")
    if hasattr(self, '__dict__') and not isinstance(self, node.ListNode):
        for k in sorted(vars(self).keys()):
            yield from walk(getattr(self, k), depth + 1)
            yield EventAttr(getattr(self, k), k, depth + 1)
        yield EventEndAttrs(self, depth=depth + 1)
    if hasattr(self, 'keys'):
        for k in sorted(self.keys()):
            yield from walk(self[k], depth + 1)
            yield EventKey(self[k], k, depth + 1)
        yield EventEndKeys(self, depth=depth + 1)
    elif not isinstance(self, str) and hasattr(self, '__iter__'):
        for idx, item in enumerate(self):
            yield from walk(self[idx], depth + 1)
            yield EventIndice(self[idx], idx, depth + 1)
        yield EventEndIndices(self, depth=depth + 1)
    yield EventValue(self, None, depth)
    yield EventType(self, type(self).__name__, depth)
    yield EventEndNode(self, depth=depth)

class Event:
    def __init__(self, node=None, attr=None, depth=None):
        self.node = node
        self.attr = attr
        self.depth = depth

    def __repr__(self) -> str:
        return "%s(%r, %r)" % (type(self).__name__, self.attr, self.node)

    def check_event(self, action, chk) -> bool:
        return False

class EventType(Event):
    def check_event(self, action, chk) -> bool:
        if action[0] == 'type':
            if len(action) == 1:
                return True
            if action[1] == self.attr:
                print("ok type")
                return True
        return False

class EventValue(Event):
    def check_event(self, action, chk) -> bool:
        global match_value
        if action[0] == 'value':
            if len(action) == 1:
                return True
            if type(self.node) in match_value and action[1] == self.node:
                print("ok value")
                return True
        return False

class EventEndNode(Event):
    def check_event(self, action, chk) -> bool:
        if action[0] == 'end_node':
            print("ok end_node")
            return True
        return False

class EventAttr(Event):
    def check_event(self, action, chk) -> bool:
        if action[0] == 'attr':
            if len(action) == 1:
                return True
            if action[1] == self.attr:
                print("ok attr")
                return True
        return False

class EventEndAttrs(Event):
    def check_event(self, action, chk) -> bool:
        if action[0] == 'end_attrs':
            print("ok end_attrs")
            return True
        return False

class EventKey(Event):
    def check_event(self, action, chk) -> bool:
        if action[0] == 'key':
            chk.first = self.attr
            if len(action) == 1:
                print("ok key: %s" % repr(chk.first))
                return True
            if action[1] == chk.first:
                print("ok key: %s" % repr(chk.first))
                return True
        return False

class EventEndKeys(Event):
    def check_event(self, action, chk) -> bool:
        if action[0] == 'end_keys':
            print("ok end_keys")
            return True
        return False

class EventIndice(Event):
    def check_event(self, action, chk) -> bool:
        if action[0] == 'indice':
            chk.first = self.attr
            if len(action) == 1:
                print("ok indice: %s" % repr(chk.first))
                return True
            if action[1] == chk.first:
                print("ok indice: %s" % repr(chk.first))
                return True
        return False

class EventEndIndices(Event):
    def check_event(self, action, chk) -> bool:
        if action[0] == 'end_indices':
            print("ok end_indices")
            return True
        return False
