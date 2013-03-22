class Node(dict):
    """Base class for node manipulation."""
    def __init__(self, val=True):
        self._bool = bool(val)
        if type(val) not in (bool, Node):
            raise TypeError(
                "{} is neither a Node nor a Boolean".format(
                    type(val).__name__))

    def __bool__(self):
        return self._bool

    def __repr__(self):
        items = []
        if len(self) > 0:
            items.append(repr(self.items()))
        for k, v in vars(self).items():
            items.append("{} = {}".format(k, repr(v)))
        return "{}({})".format(self.__class__.__name__, ', '.join(items))
