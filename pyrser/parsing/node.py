""" Basic classes for AST manipulation """

import weakref


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
                if hasattr(self, 'keys'):
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


class ListNodeItem:
    pass


class ListNodeItemIterator:
    pass


class DictNode(dict):
    pass


class TupleNode(list):
    pass


class ListNode:
    allinst = []

    def __init__(self, it: []=None):
        self.cache = None
        self.must_update = False
        self.begin = None
        self.end = None
        if it is not None:
            head = None
            for data in it:
                self.append(data)

    def append(self, d):
        if self.end is None:
            self.begin = ListNodeItem(d)
            self.end = self.begin
            self.must_update = True
        else:
            self.end = self.end.append(d)

    def prepend(self, d):
        if self.begin is None:
            self.begin = ListNodeItem(d)
            self.end = self.begin
            self.must_update = True
        else:
            self.begin = self.begin.prepend(d)

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        txt = []
        for it in self.begin._fwd():
            txt.append(str(it))
        return repr(txt)

    def dump(self) -> str:
        txt = ""
        for it in self.begin._fwd():
            txt += dump(it)
        return txt

    def __len__(self) -> int:
        self._update()
        return len(self.cache)

    def __iter__(self) -> ListNodeItemIterator:
        return ListNodeItemIterator(self.begin)

    def __reversed__(self) -> ListNodeItemIterator:
        return ListNodeItemIterator(self.end, True)

    def _trueindex(self, k) -> int:
        if k >= 0:
            return k
        if k < 0:
            return len(self.cache) + k

    def _cache(self) -> str:
        txt = "{\n"
        txt += "begin= %d\n" % id(self.begin)
        txt += "end= %d\n" % id(self.end)
        txt += "}\n"
        return txt

    def _update(self):
        if self.cache is None or self.must_update:
            self.cache = {}
            idx = 0
            for it in self.begin._fwd():
                it.thelist = weakref.ref(self)
                self.cache[idx] = it
                idx += 1
            self.must_update = False

    def index(self, data) -> int:
        self._update()
        for k, v in self.cache.items():
            if v.data == data:
                return k
        raise ValueError("%d is not in list" % v)

    def count(self, data) -> int:
        self._update()
        cnt = 0
        for v in self.cache.values():
            if v.data == data:
                cnt += 1
        return cnt

    def get(self, k) -> ListNodeItem:
        if type(k) is not int:
            raise ValueError('Key must be an int')
        self._update()
        k = self._trueindex(k)
        if k not in self.cache:
            raise IndexError("list index out of range")
        return self.cache[k]

    # []
    def __getitem__(self, k) -> object:
        if type(k) is not int:
            raise ValueError('Key must be an int')
        self._update()
        k = self._trueindex(k)
        if k not in self.cache:
            raise IndexError("list index out of range")
        return self.cache[k].data

    # [] =
    def __setitem__(self, k, d):
        if type(k) is not int:
            raise ValueError('Key must be an int')
        self._update()
        k = self._trueindex(k)
        if k not in self.cache:
            raise IndexError("list index out of range")
        self.cache[k].data = d

    # del []
    def __delitem__(self, k):
        if type(k) is not int:
            raise ValueError('Key must be an int')
        self._update()
        k = self._trueindex(k)
        if k not in self.cache:
            raise IndexError("list index out of range")
        self.cache[k].popitem()
        self.must_update = True


class ListNodeItem:
    def __init__(self, data):
        self.data = data
        self.prev = None
        self.next = None
        self.thelist = None

    def __str__(self) -> str:
        return str(self.data)

    def __repr__(self) -> str:
        return str(self.data)

    def dump(self) -> str:
        txt = "{\n"
        txt += "prev= %d\n" % id(self.prev)
        txt += "self= %d\n" % id(self)
        txt += "data= %d - %s\n" % (id(self.data), repr(self.data))
        txt += "thelist= %d\n" % id(self.thelist)
        txt += "next= %d\n" % id(self.next)
        txt += "}\n"
        return txt

    def index(self, v) -> int:
        idx = 0
        for it in self._fwd():
            if it.data == v:
                return idx
            idx += 1
        raise ValueError("%d is not in list" % v)

    def count(self, v) -> int:
        cnt = 0
        for it in self._fwd():
            if it.data == v:
                cnt += 1
        return cnt

    def _get_slice(self, sl) -> [object]:
        # TODO: slice getter
        begin, end, step = sl

    # []
    def __getitem__(self, k) -> object:
        if self.thelist is None:
            raise ValueError("Bad initialised ListNode")
        return self.thelist()[k]

    # [] =
    def __setitem__(self, k, d):
        if self.thelist is None:
            raise ValueError("Bad initialised ListNode")
        self.thelist()[k] = d

    # del []
    def __delitem__(self, k):
        if type(k) is not int:
            raise ValueError('Key must be an int')
        gen = self._fwd
        if k < 0:
            gen = self._bwd
        idx = 0
        for it in gen():
            if idx == k:
                it.popitem()
                return
            idx += 1
        raise IndexError("list index out of range")

    def popitem(self) -> object:
        if self.prev is not None:
            self.prev.next = self.next
        if self.next is not None:
            self.next.prev = self.prev
        thelist = self.thelist()
        if thelist is not None:
            if thelist.begin is self:
                thelist.begin = self.next
            if thelist.end is self:
                thelist.end = self.prev
            thelist.must_update = True
        return self.data

    def append(self, data) -> ListNodeItem:
        if self.thelist is None:
            ListNode.allinst.append(ListNode())
            self.thelist = weakref.ref(ListNode.allinst[-1])
        thelist = self.thelist()
        thelist.must_update = True
        new = ListNodeItem(data)
        new.thelist = weakref.ref(thelist)
        new.next = self.next
        self.next = new
        new.prev = self
        if new.next is not None:
            new.next.prev = new
        # update thelist
        if thelist.end is self or thelist.end is None:
            thelist.end = new
        if thelist.begin is None:
            thelist.begin = self
        return new

    def prepend(self, data) -> ListNodeItem:
        if self.thelist is None:
            ListNode.allinst.append(ListNode())
            self.thelist = weakref.ref(ListNode.allinst[-1])
        thelist = self.thelist()
        thelist.must_update = True
        new = ListNodeItem(data)
        new.thelist = weakref.ref(thelist)
        new.prev = self.prev
        self.prev = new
        new.next = self
        if new.prev is not None:
            new.prev.next = new
        # update thelist
        if thelist.begin is self or thelist.begin is None:
            thelist.begin = new
        if thelist.end is None:
            thelist.end = self
        return new

    def values(self):
        tmp = self
        while tmp is not None:
            yield tmp.data
            tmp = tmp.next

    def rvalues(self):
        tmp = self
        while tmp is not None:
            yield tmp.data
            tmp = tmp.prev

    def _fwd(self):
        tmp = self
        while tmp is not None:
            yield tmp
            tmp = tmp.next

    def _bwd(self):
        tmp = self
        while tmp is not None:
            yield tmp
            tmp = tmp.prev


class ListNodeItemIterator:
    def __init__(self, current: ListNodeItem, reverse=False):
        self.current = current
        self.attr = 'next'
        if reverse:
            self.attr = 'prev'

    def __iter__(self):
        return self

    def __next__(self):
        if self.current is None:
            raise StopIteration
        data = self.current.data
        self.current = getattr(self.current, self.attr)
        return data


def normalize(ast: Node) -> Node:
    """
    Normalize an AST nodes.

    all builtins containers are replace by referencable subclasses
    """
    res = ast
    typemap = {DictNode, ListNode, TupleNode}
    if type(ast) is dict:
        res = DictNode(ast)
    elif type(ast) is list:
        res = ListNode(ast)
    elif type(ast) is tuple:
        res = TupleNode(ast)
    # in-depth change
    if hasattr(res, 'items'):
        for k, v in res.items():
            res[k] = normalize(v)
    elif hasattr(res, '__getitem__'):
        for idx, v in zip(range(len(res)), res):
            res[idx] = normalize(v)
    if type(res) not in typemap and hasattr(res, '__dict__'):
        subattr = vars(res)
        for k, v in subattr.items():
            setattr(res, k, normalize(v))
    return res
