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

    def check(self, ndict: dict, info="") -> bool:
        """
        Debug method, help detect cycle and/or
        other incoherence in a tree of Node
        """
        def iscycle(thing, ndict: dict, info: str) -> bool:
            # check if not already here
            idthing = id(thing)
            ndict[info] = idthing
            if idthing not in ndict:
                # add myself
                ndict[idthing] = "%s:%s no cycle" % (type(thing), info)
                return False
            else:
                ndict[idthing] += "\n%s:%s cycle" % (type(thing), info)
                return True

        def recurs(thing, ndict: dict, info: str) -> bool:
            if not iscycle(thing, ndict, info):
                res = False
                if isinstance(thing, list):
                    idx = 0
                    for i in thing:
                        res |= recurs(i, ndict, "%s[%d]" % (info, idx))
                        idx += 1
                elif isinstance(thing, Node):
                    res |= thing.check(ndict, info)
                elif isinstance(thing, dict):
                    for k, v in thing.items():
                        res |= recurs(v, ndict, "%s[%s]" % (info, k))
                return res
            return True
        # add ME FIRST
        if len(ndict) == 0:
            ndict['self'] = id(self)
            info = 'self'
        if not iscycle(self, ndict, info):
            res = False
            if len(self) > 0:
                keys = list(self.keys())
                for k in keys:
                    ndict["['" + k + "']"] = id(self[k])
                    res |= recurs(self[k], ndict, "%s[%s]" % (info, k))
            keys = list(vars(self).keys())
            for k in keys:
                ndict["." + k] = id(getattr(self, k))
                res |= recurs(getattr(self, k), ndict, "%s.%s" % (info, k))
            return res
        return True

    def clean(self):
        if len(self) > 0:
            keys = list(self.keys())
            for k in keys:
                del self[k]
        keys = list(vars(self).keys())
        for k in keys:
            delattr(self, k)

    def set(self, othernode):
        """allow to completly mutate the node into any subclasses of Node"""
        self.__class__ = othernode.__class__
        self.clean()
        if len(othernode) > 0:
            for k, v in othernode.items():
                self[k] = v
        for k, v in vars(othernode).items():
            setattr(self, k, v)
