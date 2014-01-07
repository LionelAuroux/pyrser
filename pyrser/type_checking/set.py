# type set for type checking
from pyrser import fmt
from pyrser.type_checking.signature import *

def     RawSet(*signature):
    return Set(None, signature)

class   Set(Symbol):
    """
    Set of Signature for a Scope/namespace/type etc...
    Basic block of type checking
    """

    def __init__(self, name: str, ls: [Signature]=None, istype=False):
        super().__init__(name)
        self._ntypes = 0
        self._nvars = 0
        self._nfuns = 0
        if ls != None:
            self._hsig = {}
            for s in ls:
                if s.uniq_name() not in self._hsig:
                    self._hsig[s.uniq_name()] = s
                else:
                    raise KeyError(s.uniq_name() + ' redefine')
                s.set_parent(self)
                if hasattr(s, 'is_type') and s.is_type():
                    self._ntypes += 1
                if hasattr(s, 'is_var') and s.is_var():
                    self._nvars += 1
                if hasattr(s, 'is_fun') and s.is_fun():
                    self._nfuns += 1
        self._istype = istype

    def to_fmt(self):
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

    def __repr__(self):
        """
        Internal representation
        """
        return repr(self._hsig)

    def __str__(self):
        """
        Usefull representation
        """
        return str(self.to_fmt())

    def __len__(self):
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
    def __contains__(self, s: Signature):
        if type(s) is Signature:
            return s.uniq_name() in self._hsig
        if type(s) is str:
            return s in self._hsig
        return False

    # |=
    def __ior__(self, ls):
        """|= operator"""
        return self.update(ls)
    def update(self, ls):
        """Update the Set with values of another Set"""
        values = ls
        if hasattr(ls, 'values'):
            values = ls.values()
        for s in values:
            self._hsig[s.uniq_name()] = s
            s.set_parent(self)
        self.__update_count()
        return self
    # |
    def __or__(self, ls):
        """| operator"""
        return self.union(ls)
    def union(self, ls):
        """Create a new Set produce by the union of 2 Set"""
        new = RawSet(*tuple(self._hsig.values()))
        new |= ls
        return new

    # &=
    def __iand__(self, ls):
        """&= operator"""
        return self.intersection_update(ls)
    def intersection_update(self, oset):
        """Update Set with common values of another Set"""
        keys = list(self._hsig.keys())
        for k in keys:
            if k not in oset:
                del self._hsig[k]
            else:
                self._hsig[k] = oset.get(k)
        return self
    # &
    def __and__(self, ls):
        """& operator"""
        return self.intersection(ls)
    def intersection(self, ls):
        """Create a new Set produce by the intersection of 2 Set"""
        new = RawSet(*tuple(self._hsig.values()))
        new &= ls
        return new

    # -=
    def __isub__(self, ls):
        """-= operator"""
        return self.difference_update(ls)
    def difference_update(self, oset):
        """Remove values common with another Set"""
        keys = list(self._hsig.keys())
        for k in keys:
            if k in oset:
                del self._hsig[k]
        return self
    # -
    def __sub__(self, ls):
        """- operator"""
        return self.difference(ls)
    def difference(self, ls):
        """Create a new Set produce by a Set subtracted by another Set"""
        new = RawSet(*tuple(self._hsig.values()))
        new -= ls
        return new

    # ^=
    def __ixor__(self, ls):
        """^= operator"""
        return self.symmetric_difference_update(ls)
    def symmetric_difference_update(self, oset):
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
    def __xor__(self, ls):
        """^ operator"""
        return self.symmetric_difference(ls)
    def symmetric_difference(self, ls):
        """Create a new Set with values present in only one Set"""
        new = RawSet(*tuple(self._hsig.values()))
        new ^= ls
        return new

    def add(self, it: Signature):
        """
        Add it to the Set
        """
        if it.uniq_name() in self._hsig:
            return False
        self._hsig[it.uniq_name()] = it
        it.set_parent(self)
        self.__update_count()
        return True

    def remove(self, it: Signature):
        """
        Remove it but raise KeyError if not found
        """
        if it.uniq_name() not in self._hsig:
            raise KeyError(it.show_name() + ' not in Set')
        del self._hsig[it.uniq_name()]

    def discard(self, it: Signature):
        """
        Remove it only if present
        """
        if it.uniq_name() in self._hsig:
            del self._hsig[it.uniq_name()]

    def clear(self):
        self._hsig.clear()

    def pop(self):
        return self._hsig.popitem()

    def get(self, key, default=None):
        item = default
        if key in self._hsig:
            item = self._hsig[key]
        return item

    def values(self):
        return self._hsig.values()

    def count_types(self):
        """
        Count subtypes
        """
        n = 0
        for s in self._hsig.values():
            if hasattr(s, 'is_type') and s.is_type():
                n += 1
        return n

    def count_vars(self):
        """
        Count var define by this scope
        """
        n = 0
        for s in self._hsig.values():
            if hasattr(s, 'is_var') and s.is_var():
                n += 1
        return n

    def count_funs(self):
        """
        Count function define by this scope
        """
        n = 0
        for s in self._hsig.values():
            if hasattr(s, 'is_fun') and s.is_fun():
                n += 1
        return n

    def is_type(self):
        """
        If this scope define a new Type (language specific)
        """
        return self._istype
