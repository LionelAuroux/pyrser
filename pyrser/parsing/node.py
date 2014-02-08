class Node(dict):
    """Base class for node manipulation."""

    def __bool__(self):
        return True

    def __repr__(self):
        #TODO: use to_yml
        items = []
        if len(self) > 0:
            items.append(repr(self.items()))
        for k, v in vars(self).items():
            items.append("{} = {}".format(k, repr(v)))
        return "{}({})".format(self.__class__.__name__, ', '.join(items))

    def set(self, othernode):
        """allow to completly mutate the node into any subclasses of Node"""
        self.__class__ = othernode.__class__
        if len(othernode) > 0:
            for k, v in othernode.items():
                self[k] = v
        for k, v in vars(othernode).items():
            setattr(self, k, v)
