class Node(dict):
    """Base class for node manipulation."""
    def __init__(self, val=True):
        if type(val) not in (bool, Node):
            raise TypeError(
                "{} is neither a Node nor a Boolean".format(
                    type(val).__name__))
        self._bool = bool(val)

    def __bool__(self):
        return self._bool

    def __repr__(self):
        items = []
        if len(self) > 0:
            items.append(repr(self.items()))
        for k, v in vars(self).items():
            items.append("{} = {}".format(k, repr(v)))
        return "{}({})".format(self.__class__.__name__, ', '.join(items))

    def set(self, othernode):
        """allow to completly mutate the node with another instance"""
        self.__class__ = othernode.__class__
        if len(othernode) > 0:
            for k, v in othernode.items():
                self[k] = v
        for k, v in vars(othernode).items():
            setattr(self, k, v)
