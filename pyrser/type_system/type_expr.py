### Type Expr component

class TypeExprComponent(list):
    contains = None
    minarity = None

    def __init__(self, *deflist):
        if self.minarity is not None and len(deflist) < self.minarity:
            raise TypeError("%s take minimum %d parameters" % (type(self).__name__, self.minarity))
        for t in deflist:
            if self.contains is not None and type(t).__name__ not in self.contains:
                raise TypeError("%s can't be put in %s" % (type(t), type(self)))
        list.__init__(self, deflist)

    @property
    def reprlist(self):
        r = []
        for it in self:
            t = str(it)
            if isinstance(it, list) and type(self) is not Overload and len(it) > 1:
                t = '(' + t + ')'
            r.append(t)
        return r

    def __repr__(self) -> str:
        return str(self)

class Define:
    def __init__(self, name: str, type_def: TypeExprComponent):
        self.name = name
        self.type_def = type_def

    def unify(self, oth_type_def: TypeExprComponent, blhs, brhs) -> TypeExprComponent:
        """
        unify a definition with a correspondant type_def
        """
        print("DEFINE TRY TO TYPE %s ?? %s" % (type(self.type_def), type(oth_type_def)))
        print("TRY TO unify %s ?? %s" % (self.type_def, oth_type_def))
        return self.type_def.unify(oth_type_def, blhs, brhs)

    def __len__(self) -> int:
        return len(self.type_def)

    def __getitem__(self, idx) -> TypeExprComponent:
        return self.type_def[idx]

    def __str__(self) -> str:
        return "%s: %s" % (self.name, self.type_def)

    def __repr__(self) -> str:
        return str(self)

class UnknownName:
    """
    Implement unknown names: ?0, ?1, ?2
    """
    count = 0
    minarity = 1
    def __init__(self):
        self.anonname = '?%d' % UnknownName.count
        self.type_def = None
        UnknownName.count += 1

    def __lt__(self, oth):
        return self.anonname < oth.anonname

    def unify(self, oth_type_def: TypeExprComponent, blhs, brhs) -> TypeExprComponent:
        """
        When we unify an Unknown Name vs another type def we always match
        """
        print("UNK TRY TO unify %s ?? %s" % (self, oth_type_def))
        if self.type_def is not None:
            if type(oth_type_def) is UnknownName:
                if oth_type_def is None:
                    oth_type_def.type_def = self.type_def
                    return self.type_def
            return self.type_def.unify(oth_type_def, blhs, brhs)
        # TODO: the type must be fixed by the feedback pass
        if self.type_def is None:
            self.type_def = Overload()
        if oth_type_def not in self.type_def:
            self.type_def.append(oth_type_def)
        return oth_type_def

    def __str__(self) -> str:
        return self.anonname

class AnonDefine(Define):
    """
    Implement the TypeVar: ?0, ?1, ?2, ...
    """
    def __init__(self, name: str = None, cnt: 'Constraints' = None):
        """
        TODO: not really the final version
        at begin, we create circular type
        """
        self.defs = UnknownName()
        if name is not None:
            self.defname = name
        else:
            self.defname = self.defs
        Define.__init__(self, self.defname, Overload(self.defs))
        if cnt is not None:
            self.cnt = cnt
            self.cnt.add_defines([self])

class Overload(TypeExprComponent):
    contains = {'Fun', 'T', 'N', 'UnknownName'}
    minarity = 0

    def unify(self, oth_type_def: TypeExprComponent, blhs, brhs) -> TypeExprComponent:
        """
        When we unify an overload vs another type def we match each fun and we return the rest.
    
        t1 & t2 ?? t1 match and we return t1
        t1 & t2 ?? t2 match and we return t2
        """
        print("OV TRY TO unify %s ?? %s" % (self, oth_type_def))
        ovres = Overload()
        for ov in self:
            if not ov.unify(oth_type_def, blhs, brhs):
                return None
            ovres.append(oth_type_def)
        return ovres

    def __str__(self) -> str:
        return "\n& ".join(self.reprlist)

class Fun(TypeExprComponent):
    contains = {'Fun', 'Union', 'Tuple', 'UnknownName', 'T', 'N'}
    minarity = 1

    def unify(self, oth_type_def: TypeExprComponent, blhs, brhs) -> TypeExprComponent:
        """
        When we unify a function vs another type def we match each term and we return the rest.
    
        t1 -> t2 -> t3 ?? t1 -> t2 match and we return t3
        t1 -> t2 ?? t1 -> t2 -> t3 didn't match

        Note: the first element is the return type
        """
        print("FUN TRY TO unify %s ?? %s" % (self, oth_type_def))
        if type(oth_type_def) is not Fun:
            if type(oth_type_def) is T:
                return self[0].unify(oth_type_def, blhs, brhs)
            raise "not implemented"
        diff_len = len(self) - len(oth_type_def)
        if diff_len < 0: ## TODO: ADD ELLIPSIS
            return None
        for a, b in zip(reversed(self), reversed(oth_type_def)):
            if not a.unify(b, blhs, brhs):
                return None
        # TODO: what to do with the rest
        return Fun(*self[:diff_len])

    def __str__(self) -> str:
        return " -> ".join(reversed(self.reprlist))

class Union(TypeExprComponent):
    contains = {'Union', 'T', 'N'}
    minarity = 2

    def __str__(self) -> str:
        return " | ".join(self.reprlist)

class Tuple(TypeExprComponent):
    contains = {'Fun', 'Union', 'Tuple', 'T', 'N'}
    minarity = 2

    def __str__(self) -> str:
        return ", ".join(self.reprlist)

class N(TypeExprComponent):
    """N for Namespaces"""
    contains = {'T'}
    minarity = 2

    def __str__(self) -> str:
        return ".".join(self.reprlist)

class T:
    """T for Type"""
    def __init__(self, name: str, parametric: Tuple or 'T'=None, attributes=None):
        self.name = name
        if parametric is not None and type(parametric) not in {Tuple, T}:
            raise TypeError("T parametric must be a Tuple")
        self.parametric = parametric
        self.attributes = attributes

    def unify(self, oth_type_def: TypeExprComponent, blhs, brhs) -> TypeExprComponent:
        """
        When we unify a type vs another type def we match each term to term
        
        t1 ?? t1 match
        t1 ?? t2 didn't match
        TODO: parametric
        """
        print("T TRY TO unify %s ?? %s" % (self, oth_type_def))
        return self.name == oth_type_def

    def __eq__(self, oth) -> bool:
        """
        Use by all __contains__ call when we do some 'in' test
        """
        # TODO: self and oth for comparaison with TypeVar, attributes and parametric
        return self.name == oth

    def __str__(self) -> str:
        r = self.name
        if self.parametric is not None:
            r += '<' + str(self.parametric) + '>'
        return r

    def __repr__(self) -> str:
        return str(self)
