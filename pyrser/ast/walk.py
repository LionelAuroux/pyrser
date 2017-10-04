"""
This module implements a generic walking method for all pyrser.parsing.node.
"""

from pyrser import meta
from pyrser.parsing import node

not_normalized = {set, list, dict, tuple}
match_value = {int, float, str, bytes}

@meta.add_method(node.Node)
def walk(self, depth=0, pwidth=0, idparent=0):
    """
    Work only on normalized tree
    """
    width = 0
    if type(self) in not_normalized:
        raise TypeError("Not a normalized tree! User node.normalize() function!")
    if hasattr(self, '__dict__') and not isinstance(self, node.ListNode):
        for k in sorted(vars(self).keys()):
            yield from walk(getattr(self, k), depth + 1, width, id(self))
            yield EventAttr(getattr(self, k), k, depth + 1, width, childrelat=(id(getattr(self, k)), idparent))
            width += 1
        yield EventEndAttrs(self, depth=depth + 1)
    if hasattr(self, 'keys'):
        for k in sorted(self.keys()):
            yield from walk(self[k], depth + 1, width, id(self))
            yield EventKey(self[k], k, depth + 1, width, childrelat=(id(self[k]), idparent))
            width += 1
        yield EventEndKeys(self, depth=depth + 1)
    elif not isinstance(self, str) and hasattr(self, '__iter__'):
        for idx, item in enumerate(self):
            yield from walk(self[idx], depth + 1, width, id(self))
            yield EventIndice(self[idx], idx, depth + 1, width, childrelat=(id(self[idx]), idparent))
            width += 1
        yield EventEndIndices(self, depth=depth + 1)
    yield EventValue(self, None, depth, pwidth)
    yield EventType(self, type(self).__name__, depth, pwidth)
    yield EventEndNode(self, depth=depth, width=pwidth, childrelat=(id(self), idparent))

class Event:
    def __init__(self, node=None, attr=None, depth=None, width=None, childrelat=None):
        self.node = node
        self.attr = attr
        self.depth = depth
        self.width = width
        self.childrelat = childrelat

    def __repr__(self) -> str:
        return "%s(%r, %r)" % (type(self).__name__, self.attr, self.node)

    def check_event(self, action, chk) -> bool:
        return False

class EventType(Event):
    def check_event(self, action, chk) -> bool:
        if action[0] == 'type':
            if len(action) == 1:
                return True
            print("Check TYPE %s ?? %s" % (self.attr, action[1]))
            if action[1] == self.attr:
                return True
        if action[0] == 'subtype':
            #TODO: very bad
            for it in type(object).__subclasses__(object):
                if it.__name__ == action[1]:
                    if it.__name__ == self.attr:
                        return True
                    for it2 in type(object).__subclasses__(it):
                        if it2.__name__ == self.attr:
                            return True
        return False

class EventValue(Event):
    def check_event(self, action, chk) -> bool:
        global match_value
        if action[0] == 'value':
            if len(action) == 1:
                return True
            if type(self.node) in match_value and action[1] == self.node:
                return True
        return False

class EventEndNode(Event):
    def check_event(self, action, chk) -> bool:
        if action[0] == 'end_node':
#            idchild = self.childrelat[0]
#            idparent = self.childrelat[1]
#            print("ENDNODE CHILD %d HAS PARENT %d" % (idchild, idparent))
#            # literals have always the same id, so they have many parents
#            if idchild not in chk.childrelat:
#                chk.childrelat[idchild] = []
#            # EventEnNode.check_event is called many time for the same node (depend of stack)
#            if idparent not in chk.childrelat[idchild]:
#                chk.childrelat[idchild].append(idparent)
#            chk.current_parent = self.childrelat[1]
            return True
        return False

class EventAttr(Event):
    def check_event(self, action, chk) -> bool:
        if action[0] == 'attr':
            if len(action) == 1:
                return True
            print("Check %s ?? %s" % (self.attr, action[1]))
            if action[1] == self.attr:
                return True
        return False

class EventEndAttrs(Event):
    def check_event(self, action, chk) -> bool:
        if action[0] == 'end_attrs':
            return True
        return False

class EventKey(Event):
    def check_event(self, action, chk) -> bool:
        if action[0] == 'key':
            chk.first = self.attr
            if len(action) == 1:
                return True
            if action[1] == chk.first:
                return True
        return False

class EventEndKeys(Event):
    def check_event(self, action, chk) -> bool:
        if action[0] == 'end_keys':
            return True
        return False

class EventIndice(Event):
    def check_event(self, action, chk) -> bool:
        if action[0] == 'indice':
            chk.first = self.attr
            if len(action) == 1:
                return True
            if action[1] == chk.first:
                return True
        return False

class EventEndIndices(Event):
    def check_event(self, action, chk) -> bool:
        if action[0] == 'end_indices':
            return True
        return False
