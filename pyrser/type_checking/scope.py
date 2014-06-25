# scope for type checking
import weakref
from pyrser import fmt
from pyrser.type_checking.symbol import *
from pyrser.type_checking.signature import *
from pyrser.type_checking.evalctx import *
from pyrser.type_checking.translator import *
from pyrser.passes.to_yml import *


# forward just for annotation (not the same id that final type)
class Scope:
    pass


class Scope(Symbol):
    """
    Scope of Signature for a Scope/namespace/type etc...
    Basic abstraction of type checking.
    Scope is not a 'pure' python set but something between a set and a dict...
    """

    def __init__(self, name: str=None, sig: [Signature]=None,
                 auto_update_parent=True):
        """Unnamed scope for global scope"""
        if name is not None and not isinstance(name, str):
            raise TypeError("name must be a str object.")
        super().__init__(name)
        # during typing, this scope need or not feedback pass
        self.need_feedback = False
        # auto update parent during add of Signature
        self.auto_update_parent = auto_update_parent
        # internal mapping for Type Conversion
        self.mapTypeTranslate = MapSourceTranslate()
        # TODO: ...could be unusable
        self._ntypes = 0
        self._nvars = 0
        self._nfuns = 0
        # internal store of Signature
        self._hsig = {}
        if sig is not None:
            if isinstance(sig, Signature) or isinstance(sig, Scope):
                self.add(sig)
            elif len(sig) > 0:
                self.update(sig)

    def set_parent(self, parent: Scope) -> object:
        Symbol.set_parent(self, parent)
        if parent is not None:
            self.mapTypeTranslate.set_parent(parent.mapTypeTranslate)
        return self

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

    def __update_count(self):
        """
        Update internal counters
        """
        self._ntypes = self.count_types()
        self._nvars = self.count_vars()
        self._nfuns = self.count_funs()

    # ======== PRETTY PRINTING ========
    def to_fmt(self) -> fmt.indentable:
        """
        Return an Fmt representation for pretty-printing
        """
        qual = "scope"
        txt = fmt.sep(" ", [qual])
        name = self.show_name()
        if name != "":
            txt.lsdata.append(name)
        if len(self._hsig) > 0 or len(self.mapTypeTranslate) > 0:
            lsb = []
            if len(self.mapTypeTranslate) > 0:
                lsb.append("translate:\n")
                lsb.append(fmt.end("\n", self.mapTypeTranslate.to_fmt()))
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

    # ======== SET OPERATORS OVERLOADING ========
    # in
    def __contains__(self, s: Signature) -> bool:
        if isinstance(s, Signature):
            return s.internal_name() in self._hsig
        elif isinstance(s, str):
            return s in self._hsig
        return False

    # |=
    def __ior__(self, sig: list or Scope) -> Scope:
        """|= operator"""
        return self.update(sig)

    def update(self, sig: list or Scope) -> Scope:
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

    # ======== SCOPE MANIPULATION ========
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

    # ======== SCOPE ITERATION ========
    def __len__(self) -> int:
        """
        Len of the Set
        """
        return len(self._hsig)

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

    # ======== SCOPE QUERY ========
    def first(self) -> Signature:
        """
        Retrieve the first Signature ordered by mangling descendant
        """
        k = sorted(self._hsig.keys())
        return self._hsig[k[0]]

    def last(self) -> Signature:
        """
        Retrieve the last Signature ordered by mangling descendant
        """
        k = sorted(self._hsig.keys())
        return self._hsig[k[-1]]

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
                # create an EvalCtx only when necessary
                lst.append(EvalCtx.from_sig(s))
        # include parent
        # TODO: see all case of local redefinition for
        #       global overloads
        # possible algos... take all with different internal_name
        if len(lst) == 0:
            p = self.get_parent()
            if p is not None:
                return p.get_by_symbol_name(name)
        rscope = Scope(sig=lst, auto_update_parent=False)
        # inherit type/translation from parent
        rscope.set_parent(self)
        return rscope

    def getsig_by_symbol_name(self, name: str) -> Signature:
        """
        Retrieve the unique Signature of a symbol.
        Fail if the Signature is not unique
        """
        subscope = self.get_by_symbol_name(name)
        if len(subscope) != 1:
            raise KeyError("%s have multiple candidates in scope" % name)
        v = list(subscope.values())
        return v[0]

    def get_by_return_type(self, tname: str) -> Scope:
        """
        Retrieve a Set of all signature by (return) type
        """
        lst = []
        for s in self._hsig.values():
            if s.tret == tname:
                lst.append(EvalCtx.from_sig(s))
        rscope = Scope(sig=lst, auto_update_parent=False)
        # inherit type/translation from parent
        rscope.set_parent(self)
        return rscope

    def get_all_polymorphic_return(self) -> bool:
        """
        For now, polymorphic return type are handle by symbol artefact.

        --> possible multi-polymorphic but with different constraint attached!
        """
        lst = []
        for s in self._hsig.values():
            if s.tret.is_polymorphic:
                # encapsulate s into a EvalCtx for meta-var resolution
                lst.append(EvalCtx.from_sig(s))
        rscope = Scope(sig=lst, auto_update_parent=False)
        # inherit type/translation from parent
        rscope.set_parent(self)
        return rscope

    def get_by_params(self, params: [Scope]) -> (Scope, [[Scope]]):
        """
        Retrieve a Set of all signature that match the parameter list.
        Return a pair.
            pair[0] the overloads for the functions
            pair[1] the overloads for the parameters (a list of candidate list of parameters)
        """
        lst = []
        scopep = []
        # for each of our signatures
        for s in self._hsig.values():
            # for each params of this signature
            if hasattr(s, 'tparams'):
                # number of matched params
                mcnt = 0
                # temporary collect
                nbparam_sig = len(s.tparams)
                nbparam_candidates = len(params)
                # don't treat signature too short
                if nbparam_sig > nbparam_candidates:
                    continue
                # don't treat signature too long if not variadic
                if nbparam_candidates > nbparam_sig and not s.variadic:
                    continue
                tmp = [None] * nbparam_candidates
                for i in range(nbparam_candidates):
                    tmp[i] = Scope()
                    # match param of the expr
                    if i < nbparam_sig:
                        m = params[i].get_by_return_type(s.tparams[i])
                        if len(m) > 0:
                            mcnt += 1
                            tmp[i].update(m)
                        else:
                            # co/contra-variance
                            # we just need to search a t1->t2
                            # and add it into the tree (with/without warnings)
                            t1 = params[i]
                            t2 = s.tparams[i]
                            # if exist a fun (t1) -> t2
                            (is_convertible,
                             signature,
                             translator
                             ) = t1.findTranslationTo(t2)
                            if is_convertible:
                                # add a translator
                                signature.use_translator(translator)
                                mcnt += 1
                                nscope = Scope(sig=[signature])
                                tmp[i].update(nscope)
                            elif s.tparams[i].is_polymorphic:
                                # handle polymorphic parameter
                                mcnt += 1
                                if not isinstance(params[i], Scope):
                                    raise Exception(
                                        "params[%d] must be a Scope" % i
                                    )
                                tmp[i].update(params[i])
                            else:
                                # handle polymorphic return type
                                m = params[i].get_all_polymorphic_return()
                                if len(m) > 0:
                                    mcnt += 1
                                    tmp[i].update(m)
                    # for variadic extra parameters
                    else:
                        mcnt += 1
                        if not isinstance(params[i], Scope):
                            raise Exception("params[%d] must be a Scope" % i)
                        tmp[i].update(params[i])
                # we have match all candidates
                if mcnt == len(params):
                    # select this signature but
                    # box it (with EvalCtx) for type resolution
                    lst.append(EvalCtx.from_sig(s))
                    scopep.append(tmp)
        rscope = Scope(sig=lst, auto_update_parent=False)
        # inherit type/translation from parent
        rscope.set_parent(self)
        return (rscope, scopep)

    def findTranslationTo(self, t2: str) -> (bool, Signature, Translator):
        """
        Find an arrow (->) aka a function able to translate something to t2
        """
        if not t2.is_polymorphic:
            collect = []
            for s in self._hsig.values():
                t1 = s.tret
                if t1.is_polymorphic:
                    continue
                if (s.tret in self.mapTypeTranslate):
                    if (t2 in self.mapTypeTranslate[t1]):
                        collect.append((
                            True,
                            s,
                            self.mapTypeTranslate[t1][t2]
                        ))
            # if len > 1 too many candidates
            if len(collect) == 1:
                return collect[0]
        return (False, None, None)
