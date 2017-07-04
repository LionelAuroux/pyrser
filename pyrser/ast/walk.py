"""
This module implements a generic walking method for all pyrser.parsing.node.
"""

from pyrser import meta
from pyrser.parsing import node

@meta.add_method(node.Node)
def walk(self):
    """
    Work only on normalized tree
    """
    not_normalized = {set, list, dict, tuple}
    match_value = {int, float, str, bytes}

    if type(self) in not_normalized:
        raise TypeError("Not a normalized tree! User node.normalize() function!")
    yield EventBeginNode(id(self), self)
    if hasattr(self, '__dict__') and not isinstance(self, node.ListNode):
        yield EventBeginAttrs(id(self), self)
        for k in sorted(vars(self).keys()):
            yield from walk(getattr(self, k))
            yield EventAttr(k, getattr(self, k))
        yield EventEndAttrs(id(self), self)
    if hasattr(self, 'keys'):
        yield EventBeginKeys(id(self), self)
        for k in sorted(self.keys()):
            yield from walk(self[k])
            yield EventKey(k, self[k])
        yield EventEndKeys(id(self), self)
    elif not isinstance(self, str) and hasattr(self, '__iter__'):
        yield EventBeginIndices(id(self), self)
        for idx, item in enumerate(self):
            yield from walk(self[idx])
            yield EventIndice(idx, item)
        yield EventEndIndices(id(self), self)
    if type(self) in match_value:
        yield EventValue(self, self)
    yield EventType(type(self), self)
    yield EventEndNode(id(self), self)

class Event:
    def __init__(self, attr, ref):
        self.attr = attr
        self.ref = ref

    def __repr__(self) -> str:
        return "%s(%r, %r)" % (type(self).__name__, self.attr, self.ref)

class EventBeginNode(Event):
    pass
class EventType(Event):
    pass
class EventValue(Event):
    pass
class EventEndNode(Event):
    pass

class EventBeginAttrs(Event):
    pass
class EventAttr(Event):
    pass
class EventEndAttrs(Event):
    pass

class EventBeginKeys(Event):
    pass
class EventKey(Event):
    pass
class EventEndKeys(Event):
    pass

class EventBeginIndices(Event):
    pass
class EventIndice(Event):
    pass
class EventEndIndices(Event):
    pass
