# around a signature store type resolution for monomorphic or polymorphic call
from pyrser import fmt
from pyrser.type_checking.signature import *

class EvalCtx(Signature):
    """
    Store environment for mono/poly call.
    """

    def __init__(self, name: str, tret: str, *tparams):
        super().__init__(name, tret, *tparams)
        self.resolution = dict()
        self.resolve()

    def set_parent(self, parent) -> object:
        """
        When we add a parent (from Symbol), don't forget to resolve.
        """
        ret = self
        if parent is not None:
            ret = super().set_parent(parent)
            self.resolve()
        elif not hasattr(self, 'parent'):
            # only if parent didn't exist yet
            self.parent = None
        return ret

    def resolve(self):
        """
        Process the signature and find definition for type.
        """
        # collect types for resolution
        t2resolv = [self.tret]
        for p in self.tparams:
            t2resolv.append(p)
        for t in t2resolv:
            for c in t.components:
                if c not in self.resolution or self.resolution[c] is None:
                    # try to find what is c
                    parent = self.get_parent()
                    if parent is not None:
                        sc = parent.get_by_symbol_name(c)
                        if len(sc) == 1:
                            rtyp = weakref.ref(sc.pop()[1])
                            self.resolution[c] = rtyp
                            continue
                    # unresolved
                    self.resolution[c] = None

    def to_fmt(self):
        """
        Return an Fmt representation for pretty-printing
        """
        qual = "evalctx"
        lseval = []
        block = fmt.block(":\n", "", fmt.tab(lseval))
        txt = fmt.sep(" ", [qual, block])
        lseval.append(super().to_fmt())
        if len(self.resolution) > 0:
            lsb = []
            for k in sorted(self.resolution.keys()):
                s = self.resolution[k]
                if s is not None:
                    lsb.append(fmt.end("\n", ["'%s': %s (%s)" % (k, s, s().show_name())]))
                else:
                    lsb.append(fmt.end("\n", ["'%s': Unresolved" % (k)]))
            lseval.append(fmt.block("\nresolution :\n", "", fmt.tab(lsb)))
        return txt

    def __str__(self):
        return str(self.to_fmt())
