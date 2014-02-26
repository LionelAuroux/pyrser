# scope for type checking
from pyrser import fmt
from pyrser.type_checking.symbol import *
from pyrser.type_checking.signature import *


# forward just for annotation (not the same id that final type)
class Scope: pass


class Scope(Symbol):
    """
    Scope of Signature for a Scope/namespace/type etc...
    Basic abstraction of type checking.
    Scope is not a 'pure' python set but something between a set and a dict...
    """

    def __init__(self, name: str=None, sig: [Signature]=None, auto_update_parent=True):
        """Unnamed scope for global scope"""
        super().__init__(name)
        # during typing, this scope need or not feedback pass
        self.need_feedback = False
        # auto update parent during add of Signature
        self.auto_update_parent = auto_update_parent
        # TODO: ...could be unusable
        self._ntypes = 0
        self._nvars = 0
        self._nfuns = 0
        self._hsig = {}
        if sig is not None:
            if isinstance(sig, Signature) or isinstance(sig, Scope):
                self.add(sig)
            elif len(sig) > 0:
                self.update(sig)

    def to_fmt(self) -> fmt.indentable:
        """
        Return an Fmt representation for pretty-printing
        """
        qual = "scope"
        txt = fmt.sep(" ", [qual])
        name = self.show_name()
        if name != "":
            txt.lsdata.append(name)
        if len(self._hsig) > 0:
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
        if isinstance(s, Signature):
            return s.internal_name() in self._hsig
        elif isinstance(s, str):
            return s in self._hsig
        return False

    # |=
    def __ior__(self, sig: Scope) -> Scope:
        """|= operator"""
        return self.update(sig)

    def update(self, sig: Scope) -> Scope:
        """Update the Set with values of another Set"""
        values = sig
        if hasattr(sig, 'values'):
            values = sig.values()
        for s in values:
            self._hsig[s.internal_name()] = s
            if self.auto_update_parent:
                s.set_parent(self)
        self.__update_count()
        return self

    # |
    def __or__(self, sig: Scope) -> Scope:
        """| operator"""
        return self.union(sig)

    def union(self, sig: Scope) -> Scope:
        """Create a new Set produce by the union of 2 Set"""
        new = Scope(sig=self._hsig.values())
        new |= sig
        return new

    # &=
    def __iand__(self, sig: Scope) -> Scope:
        """&= operator"""
        return self.intersection_update(sig)

    def intersection_update(self, oset: Scope) -> Scope:
        """Update Set with common values of another Set"""
        keys = list(self._hsig.keys())
        for k in keys:
            if k not in oset:
                del self._hsig[k]
            else:
                self._hsig[k] = oset.get(k)
        return self

    # &
    def __and__(self, sig: Scope) -> Scope:
        """& operator"""
        return self.intersection(sig)

    def intersection(self, sig: Scope) -> Scope:
        """Create a new Set produce by the intersection of 2 Set"""
        new = Scope(sig=self._hsig.values())
        new &= sig
        return new

    # -=
    def __isub__(self, sig: Scope) -> Scope:
        """-= operator"""
        return self.difference_update(sig)

    def difference_update(self, oset: Scope) -> Scope:
        """Remove values common with another Set"""
        keys = list(self._hsig.keys())
        for k in keys:
            if k in oset:
                del self._hsig[k]
        return self

    # -
    def __sub__(self, sig: Scope) -> Scope:
        """- operator"""
        return self.difference(sig)

    def difference(self, sig: Scope) -> Scope:
        """Create a new Set produce by a Set subtracted by another Set"""
        new = Scope(sig=self._hsig.values())
        new -= sig
        return new

    # ^=
    def __ixor__(self, sig: Scope) -> Scope:
        """^= operator"""
        return self.symmetric_difference_update(sig)

    def symmetric_difference_update(self, oset: Scope) -> Scope:
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
    def __xor__(self, sig: Scope) -> Scope:
        """^ operator"""
        return self.symmetric_difference(sig)

    def symmetric_difference(self, sig: Scope) -> Scope:
        """Create a new Set with values present in only one Set"""
        new = Scope(sig=self._hsig.values())
        new ^= sig
        return new

    def add(self, it: Signature) -> bool:
        """
        Add it to the Set
        """
        if it.internal_name() in self._hsig:
            return False
        self._hsig[it.internal_name()] = it
        if self.auto_update_parent:
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

    def get_by_symbol_name(self, name: str) -> Scope:
        """
        Retrieve a Set of all signature by symbol name
        """
        lst = []
        for s in self._hsig.values():
            if s.name == name:
                lst.append(s)
        # include parent
        # TODO: see all case of local redefinition for
        # global overloads
        if len(lst) == 0:
            p = self.get_parent()
            if p is not None:
                return p.get_by_symbol_name(name)
        return Scope(sig=lst, auto_update_parent=False)

    def get_by_return_type(self, tname: str) -> Scope:
        """
        Retrieve a Set of all signature by (return) type
        """
        lst = []
        for s in self._hsig.values():
            if s.tret == tname:
                lst.append(s)
        return Scope(sig=lst, auto_update_parent=False)

    def get_all_polymorphic_return(self) -> bool:
        """
        For now, polymorphic return type are handle by symbol artefact.

        --> possible multi-polymorphic but with different constraint attached!
        """
        lst = []
        for s in self._hsig.values():
            if s.tret.is_polymorphic():
                # TODO: must encapsulate s into a subscope for meta-var instanciation
                lst.append(s)
        return Scope(sig=lst, auto_update_parent=False)

    def get_by_params(self, *params) -> (Scope, [Scope]):
        """
        Retrieve a Set of all signature that match the parameter list.
        Must be overload in some language to handle things like ellipsis (...).
        Return a pair.
            pair[0] the overloads for the functions
            pair[1] the overloads for the parameters
        """
        lst = []
        scopep = [None] * len(params)
        # for each of our signature
        for s in self._hsig.values():
            # number of matchable params
            mcnt = 0
            # for each params of this signature
            if hasattr(s, 'tparams'):
                # temporary collect
                tmp = [None] * len(s.tparams)
                for i in range(len(s.tparams)):
                    # match param of the signature
                    m = params[i].get_by_return_type(s.tparams[i])
                    if len(m) > 0:
                        mcnt += 1
                        if tmp[i] is None:
                            tmp[i] = m
                        else:
                            tmp[i].update(m)
                    # TODO:???
                    # co/contra-variance before or after poly?
                    # iopi: FOR ME, BEFORE
                    elif s.tparams[i].is_polymorphic():
                        # handle polymorphic parameter
                        mcnt += 1
                        if tmp[i] is None:
                            tmp[i] = Scope(sig=params[i].values())
                        else:
                            tmp[i].update(params[i].values())
                        # we must instanciate params[i].values
                        #...
                    else:
                        # handle polymorphic return type
                        m = params[i].get_all_polymorphic_return()
                        if len(m) > 0:
                            mcnt += 1
                            if tmp[i] is None:
                                tmp[i] = m
                            else:
                                tmp[i].update(m)
                            # we must instanciate s.tparams[i]
                            #...
                        # here handle (co/contra) variance
                        # we just need to search a t1->t2
                        # and add it into the tree (with/without warnings)
                        # ...TODO
                # this could must be redefine for handle language with ellipsis
                if mcnt == len(s.tparams) and mcnt == len(params):
                    # select this signature
                    # TODO: must encapsul s if contains polymorphic parameter...
                    lst.append(s)
                    for i in range(mcnt):
                        m = tmp[i]
                        if scopep[i] is None:
                            scopep[i] = m
                        else:
                            scopep[i].update(m)
        return (Scope(sig=lst, auto_update_parent=False), scopep)

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
            if type(s).__name__ == 'Type':
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

    def set_name(self, name: str):
        """
        You could set the name after construction
        """
        self.name = name
        # update internal names
        lsig = self._hsig.values()
        self._hsig = {}
        for s in lsig:
            self._hsig[s.internal_name()] = s
