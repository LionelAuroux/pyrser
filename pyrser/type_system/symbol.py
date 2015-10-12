# symbol for type checking
import weakref


class Symbol:
    """
    Symbol are semantic name used in a language.
    Could be map to binary symbol but conceptually are more related
    to language symbol table.
    """

    def __init__(self, name, parent=None):
        self.name = name
        self.set_parent(parent)

    def __getstate__(self):
        """
        For pickle don't handle weakrefs...
        """
        state = self.__dict__.copy()
        del state['parent']
        return state

    def set_parent(self, parent) -> object:
        if parent is not None:
            self.parent = weakref.ref(parent)
        else:
            self.parent = None
        return self

    def get_parent(self) -> object:
        """
        Auto deref parent and return the instance.
        """
        if hasattr(self, 'parent') and self.parent is not None:
            return self.parent()
        return None

    def get_scope_list(self) -> list:
        """
        Return the list of all contained scope from global to local
        """
        # by default only return scoped name
        lstparent = [self]
        p = self.get_parent()
        while p is not None:
            lstparent.append(p)
            p = p.get_parent()
        return lstparent

    def get_scope_names(self) -> list:
        """
        Return the list of all contained scope from global to local
        """
        # allow global scope to have an None string instance
        lscope = []
        for scope in reversed(self.get_scope_list()):
            if scope.name is not None:
                # handle fun/block scope decoration
                lscope.append(scope.name)
        return lscope

    # to overload for new language
    def show_name(self) -> str:
        """
        Return a convenient name for type checking
        """
        return ".".join(self.get_scope_names())

    # to overload for new language
    def internal_name(self) -> str:
        """
        Returns the namespace's internal_name.
        """
        unq = "_".join(self.get_scope_names())
        return unq

    def __str__(self) -> str:
        return self.show_name()

    def __repr__(self) -> str:
        return self.internal_name()
