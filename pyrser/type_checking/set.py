# type set for type checking
from pyrser import fmt
from pyrser.type_checking.signature import *


def RawSet(*signature: [Signature]) -> 'Set':
    return Set(None, signature)


class Set(Symbol):
    """
    Set of Signature for a Scope/namespace/type etc...
    Basic abstraction of type checking.
    Set is not a 'pure' python set but something between a set and a dict...
    """

    def __init__(self, name: str, ls: [Signature]=None, istype=False):
        super().__init__(name)
        self._ntypes = 0
        self._nvars = 0
        self._nfuns = 0
        self._hsig = {}
        if ls is not None:
            self.update(ls)
        self._istype = istype

    def to_fmt(self) -> fmt.indentable:
        """
        Return an Fmt representation for pretty-printing
        """
        qual = "scope"
        if self.is_type():
            qual = "type"
        txt = fmt.sep(" ", [qual])
        name = self.show_name()
        if name != "":
            txt.lsdata.append(name)
        if hasattr(self, '_hsig') and len(self._hsig) > 0:
            lsb = []
            for k in sorted(self._hsig.keys()):
                s = self._hsig[k]
                lsb.append(fmt.end("\n", [s.to_fmt()]))
            block = fmt.block(":\n", "", fmt.tab(lsb))
            txt.lsdata.append(block)
        return txt

    def __repr__(self) -> str:
        """
        Internal representation
        """
        return repr(self._hsig)

    def __str__(self) -> str:
        """
        Usefull representation
        """
        return str(self.to_fmt())

    def __len__(self) -> int:
        """
        Len of the Set
        """
        return len(self._hsig)

    def __update_count(self):
        """
        Update internal counters
        """
        self._ntypes = self.count_types()
        self._nvars = self.count_vars()
        self._nfuns = self.count_funs()

    # in
    def __contains__(self, s: Signature) -> bool:
        if type(s) is Signature:
            return s.internal_name() in self._hsig
        if type(s) is str:
            return s in self._hsig
        return False

    # |=
    def __ior__(self, ls: 'Set') -> 'Set':
        """|= operator"""
        return self.update(ls)

    def update(self, ls: 'Set') -> 'Set':
        """Update the Set with values of another Set"""
        values = ls
        if hasattr(ls, 'values'):
            values = ls.values()
        for s in values:
            if s.internal_name() not in self._hsig:
                self._hsig[s.internal_name()] = s
            else:
                raise KeyError(s.internal_name() + ' redefine')
            s.set_parent(self)
        self.__update_count()
        return self

    # |
    def __or__(self, ls: 'Set') -> 'Set':
        """| operator"""
        return self.union(ls)

    def union(self, ls: 'Set') -> 'Set':
        """Create a new Set produce by the union of 2 Set"""
        new = RawSet(*tuple(self._hsig.values()))
        new |= ls
        return new

    # &=
    def __iand__(self, ls: 'Set') -> 'Set':
        """&= operator"""
        return self.intersection_update(ls)

    def intersection_update(self, oset: 'Set') -> 'Set':
        """Update Set with common values of another Set"""
        keys = list(self._hsig.keys())
        for k in keys:
            if k not in oset:
                del self._hsig[k]
            else:
                self._hsig[k] = oset.get(k)
        return self

    # &
    def __and__(self, ls: 'Set') -> 'Set':
        """& operator"""
        return self.intersection(ls)

    def intersection(self, ls: 'Set') -> 'Set':
        """Create a new Set produce by the intersection of 2 Set"""
        new = RawSet(*tuple(self._hsig.values()))
        new &= ls
        return new

    # -=
    def __isub__(self, ls: 'Set') -> 'Set':
        """-= operator"""
        return self.difference_update(ls)

    def difference_update(self, oset: 'Set') -> 'Set':
        """Remove values common with another Set"""
        keys = list(self._hsig.keys())
        for k in keys:
            if k in oset:
                del self._hsig[k]
        return self

    # -
    def __sub__(self, ls: 'Set') -> 'Set':
        """- operator"""
        return self.difference(ls)

    def difference(self, ls: 'Set') -> 'Set':
        """Create a new Set produce by a Set subtracted by another Set"""
        new = RawSet(*tuple(self._hsig.values()))
        new -= ls
        return new

    # ^=
    def __ixor__(self, ls: 'Set') -> 'Set':
        """^= operator"""
        return self.symmetric_difference_update(ls)

    def symmetric_difference_update(self, oset: 'Set') -> 'Set':
        """Remove common values and Update specific values from another Set"""
        skey = set()
        keys = list(self._hsig.keys())
        for k in keys:
            if k in oset:
                skey.add(k)
        for k in oset._hsig.keys():
            if k not in skey:
                self._hsig[k] = oset.get(k)
        for k in skey:
            del self._hsig[k]
        return self

    # ^
    def __xor__(self, ls: 'Set') -> 'Set':
        """^ operator"""
        return self.symmetric_difference(ls)

    def symmetric_difference(self, ls: 'Set') -> 'Set':
        """Create a new Set with values present in only one Set"""
        new = RawSet(*tuple(self._hsig.values()))
        new ^= ls
        return new

    def add(self, it: Signature) -> bool:
        """
        Add it to the Set
        """
        if it.internal_name() in self._hsig:
            return False
        self._hsig[it.internal_name()] = it
        it.set_parent(self)
        self.__update_count()
        return True

    def remove(self, it: Signature) -> bool:
        """
        Remove it but raise KeyError if not found
        """
        if it.internal_name() not in self._hsig:
            raise KeyError(it.show_name() + ' not in Set')
        del self._hsig[it.internal_name()]
        return True

    def discard(self, it: Signature) -> bool:
        """
        Remove it only if present
        """
        if it.internal_name() in self._hsig:
            del self._hsig[it.internal_name()]
            return True
        return False

    def clear(self) -> bool:
        """
        Clear all signatures in the Set
        """
        self._hsig.clear()
        return True

    def pop(self) -> Signature:
        """
        Pop a random Signature
        """
        return self._hsig.popitem()

    def get(self, key: str, default=None) -> Signature:
        """
        Get a signature instance by its internal_name
        """
        item = default
        if key in self._hsig:
            item = self._hsig[key]
        return item

    def get_by_symbol_name(self, name: str) -> 'Set':
        """
        Retrieve a Set of all signature by symbol name
        """
        lst = []
        for s in self._hsig.values():
            if s.name == name:
                lst.append(s)
        return RawSet(*tuple(lst))

    def get_by_return_type(self, tname: str) -> 'Set':
        """
        Retrieve a Set of all signature by (return) type
        """
        lst = []
        for s in self._hsig.values():
            if s.tret == tname:
                lst.append(s)
        return RawSet(*tuple(lst))

    def get_by_params(self, *params) -> ('Set', 'Set'):
        """
        Retrieve a Set of all signature that match the parameter list.
        Must be overload in some language to handle things like ellipsis (...).
        Return a pair.
            pair[0] the overloads for the functions
            pair[1] the overloads for the parameters
        """
        lst = []
        # for each of our signature
        for s in self._hsig.values():
            # number of matchable params
            mcnt = 0
            # for each params of this signature
            if hasattr(s, 'tparams'):
                for i in range(len(s.tparams)):
                    # match param of the signature
                    m = params[i].get_by_return_type(s.tparams[i])
                    if len(m) > 0:
                        mcnt += 1
                # this could must be redefine for handle language with ellipsis
                if mcnt == len(s.tparams) and mcnt == len(params):
                    # select this signature
                    lst.append(s)
        scopep = RawSet()
        # for each selected signature
        for s in lst:
            # for each params in this signature
            for i in range(len(s.tparams)):
                # collect this params
                scopep.update(params[i].get_by_return_type(s.tparams[i]))
        return (RawSet(*tuple(lst)), scopep)

    def values(self) -> [Signature]:
        """
        Retrieve all values
        """
        return self._hsig.values()

    def keys(self) -> [str]:
        """
        Retrieve all keys
        """
        return self._hsig.keys()

    def count_types(self) -> int:
        """
        Count subtypes
        """
        n = 0
        for s in self._hsig.values():
            if hasattr(s, 'is_type') and s.is_type():
                n += 1
        return n

    def count_vars(self) -> int:
        """
        Count var define by this scope
        """
        n = 0
        for s in self._hsig.values():
            if hasattr(s, 'is_var') and s.is_var():
                n += 1
        return n

    def count_funs(self) -> int:
        """
        Count function define by this scope
        """
        n = 0
        for s in self._hsig.values():
            if hasattr(s, 'is_fun') and s.is_fun():
                n += 1
        return n

    def is_type(self, change=None) -> bool:
        """
        If this scope define a new Type (language specific).
        You could change it!
        """
        if change is not None and type(change) is bool:
            self._istype = change
        return self._istype

    def set_name(self, name: str):
        """
        You could set the name after construction
        """
        self.name = name
        lsig = self._hsig.values()
        self._hsig = {}
        for s in lsig:
            self._hsig[s.internal_name()] = s
