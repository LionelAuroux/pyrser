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
    not_value = {node.SetNode, node.ListNode, node.DictNode, node.TupleNode}

    if type(self) in not_normalized:
        raise TypeError("Not a normalized tree! User node.normalize() function!")
    yield ('begin', id(self), self)
    if hasattr(self, '__dict__') and not isinstance(self, node.ListNode):
        yield ('begin_attr', id(self), self)
        for k in sorted(vars(self).keys()):
            yield from walk(getattr(self, k))
            yield ('attr', k, getattr(self, k))
        yield ('end_attr', id(self), self)
    if hasattr(self, 'keys'):
        yield ('begin_keys', id(self), self)
        for k in sorted(self.keys()):
            yield from walk(self[k])
            yield ('key', k, self[k])
        yield ('end_keys', id(self), self)
    elif not isinstance(self, str) and hasattr(self, '__iter__'):
        yield ('begin_idx', id(self), self)
        for idx, item in enumerate(self):
            yield from walk(self[idx])
            yield ('idx', idx, item)
        yield ('end_idx', id(self), self)
    yield ('type', type(self), self)
    if type(self) not in not_value:
        yield ('value', self, self)
    yield ('end', id(self), self)
