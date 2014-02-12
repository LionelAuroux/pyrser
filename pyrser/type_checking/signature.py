# function or var signature
import weakref
from pyrser import fmt


class Symbol:
    """
    Symbol are semantic name used in a language.
    Could be map to binary symbol but conceptually are more related
    to language symbol table.
    """

    def __init__(self, name, parent=None):
        self.name = name
        self.set_parent(parent)

    def set_parent(self, parent):
        if parent is not None:
            self.parent = weakref.ref(parent)
        else:
            self.parent = None

    def get_parent(self):
        if self.parent is not None:
            return self.parent()
        return None

    def get_scope_list(self):
        """
        Return the list of all contained scope from global to local
        """
        # by default only return scoped name
        lstparent = [self]
        p = self.get_parent()
        while p is not None:
            lstparent.append(p)
            p = p.get_parent()
        # allow global scope to have an None string instance
        lscope = []
        for scope in reversed(lstparent):
            if scope.name is not None:
                lscope.append(scope.name)
        return lscope

    # to overload for new language
    def show_name(self):
        """
        Return a convenient name for type checking
        """
        return ".".join(self.get_scope_list())

    # to overload for new language
    def internal_name(self):
        """
        Return the unique internal name
        """
        unq = "_".join(self.get_scope_list())
        if hasattr(self, 'tparams'):
            unq += "_" + "_".join(self.tparams)
        if hasattr(self, 'tret'):
            unq += "_" + self.tret
        return unq


class Signature(Symbol):
    """
    Describe a function or variable signature for the language
    """

    def __init__(self, name: str, tret: str, *tparams):
        super().__init__(name)
        self.tret = tret
        if len(tparams) > 0:
            self.tparams = tparams

    def to_fmt(self):
        """
        Return an Fmt representation for pretty-printing
        """
        params = ""
        txt = fmt.sep(" ", ['var'])
        name = self.show_name()
        if name != "":
            txt.lsdata.append(name)
        if hasattr(self, 'tparams'):
            params = '(' + ", ".join(self.tparams) + ')'
            txt.lsdata[0] = 'fun'
            txt.lsdata.append(': ' + params)
            txt.lsdata.append('-> ' + self.tret)
        else:
            txt.lsdata.append(': ' + self.tret)
        return txt

    def __str__(self):
        return str(self.to_fmt())

    def is_var(self):
        return not hasattr(self, 'tparams')

    def is_fun(self):
        return hasattr(self, 'tparams')
