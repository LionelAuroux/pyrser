### Type Expr component
import weakref as wr
import re
from collections import ChainMap

class Log:
    def __init__(self):
        self.type_log = []
        self.annexe_log = []

    def __str__(self) -> str:
        txt_log = []
        if len(self.type_log):
            txt_log += ["type:"]
            for l in self.type_log:
                txt_log += ["\t- %s" % l]
        if len(self.annexe_log):
            txt_log += ["annexe:"]
            for l in self.annexe_log:
                txt_log += ["\t- %s" % l]
        return "\n".join(txt_log)

class Term:
    def __init__(self):
        # self.link will become a weakref on the correspondant term if needed
        # during find return the link
        self.link = None
        self.t = None

    def ref_it(self, t):
        self.link = wr.ref(t)

    def log_it(self, l: Log):
        #if type(self) is not Term:
        #    raise RuntimeError("Must be implemented in inherited class")
        l.type_log += ["id%s" % str(id(self))]

    def find(self) -> 'Term':
        print("FIND REAL %d -" % id(self), end='')
        if self.link is not None:
            t = find(self.link())
            # dynamically updated if need
            if t is not self.link():
                self.ref_it(t)
            self.t = t
            print("IS %d" % id(t))
            return t
        self.t = self
        print("IS %d" % id(self.t))
        return self

    def __str__(self) -> str:
        if self.t is self:
            return str(id(self.t))
        return str(self.t)

    def __repr__(self) -> str:
        return str(self)

class TypeExprComponent(list, Term):
    contains = None
    minarity = None
    def __init__(self, *deflist):
        if self.minarity is not None and len(deflist) < self.minarity:
            raise TypeError("%s take minimum %d parameters" % (type(self).__name__, self.minarity))
        for t in deflist:
            if self.contains is not None and type(t).__name__ not in self.contains:
                raise TypeError("%s can't be put in %s" % (type(t), type(self)))
        list.__init__(self, deflist)
        Term.__init__(self)

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

class Scope:
    """
    to simul a scope where thing are defined
    """
    def __init__(self):
        self.lookup_table = ChainMap()

    def set(self, n, o):
        self.lookup_table[n] = o

    def get(self, n):
        return self.lookup_table[n]

    def push(self):
        self.lookup_table = self.lookup_table.new_child()

    def pop(self):
        self.lookup_table = self.lookup_table.parents

    def unify(self, t1, t2) -> bool:
        t1 = t1.find()
        # t2 is None for ExprFun
        # TODO: t2 could be None for all Expr
        if t2 is not None:
            t2 = t2.find()
        print("unify:")
        print(str(t1))
        print("with:")
        print(str(t2))
        print("-" * 20)
        if t1 is t2:
            print("IS THE SAME")
            return True
        if type(t1) is UnknownName:
            t1.ref_it(t2)
            return True
        if type(t2) is UnknownName:
            t2.ref_it(t1)
            return True
        if type(t1) is Expr and type(t2) is Expr:
            return False
        if type(t1) is BoundCall and t2 is None:
            print("BoundCall")
            print("proto: %s" % str(t1.proto))
            inst_f = Fun(UnknownName(), *t1.call_list)
            print("call: %s" % str(inst_f))
            # unify t1.proto with t1.call_list
            for st1, st2 in zip(t1.proto, inst_f):
                if not self.unify(st1, st2):
                    return False
            print("final call: %s" % str(inst_f))
            return True
        return False

    def log_it(self, l: Log):
        for k in sorted(self.lookup_table.keys()):
            self.lookup_table[k].log_it(l)

class Expr(Term):
    def __init__(self, name: str, scope: Scope):
        self.name = name
        self.t = None
        self.scope = scope

    def find(self) -> 'Term':
        if self.t is None:
            self.t = self.scope.get(self.name)
        return self.t

    def __str__(self) -> str:
        return "%s: %s" % (self.name, str(self.t))

class ExprLiteral(Expr):
    def __init__(self, value: str, t: str, scope: Scope):
        """
        think another way to map literal value to type
        """
        #assoc_match_type = [(r'(\d+\.\d*)|\.\d+', 'float'), (r'\d+', 'int')]
        #n = None
        #for regx, t in assoc_match_type:
        #    if re.match(regx, value):
        #        n = scope.get(t)
        Expr.__init__(self, t, scope)
        self.value = value

class BoundCall(Term):
    """
    Represent an expression bound to his definition
    """
    def __init__(self, name: str, proto: TypeExprComponent, call_list: TypeExprComponent):
        self.name = name
        self.proto = proto
        self.call_list = call_list

    def __str__(self) -> str:
        return "%s: %s" % (self.name, str(self.proto))

class ExprFun(Expr):
    def __init__(self, name: str, call_list: [Expr], scope: Scope):
        Expr.__init__(self, name, scope)
        self.call_list = call_list

    def find(self) -> 'Term':
        # TODO: see all kind of binding
        # Lookup of the function
        proto = self.scope.get(self.name)
        # TODO: check unkown function self.name if proto is None
        return BoundCall(self.name, proto, self.call_list)

class Define(Term):
    def __init__(self, name: str, type_def: TypeExprComponent, scope: Scope):
        self.name = name
        self.type_def = type_def
        self.scope = scope
        scope.set(name, type_def)

    def find(self) -> 'Term':
        return self.scope.get(self.name)

    def unify(self, oth_type_def: TypeExprComponent, blhs, brhs) -> TypeExprComponent:
        """
        unify a definition with a correspondant type_def
        """
        print("DEFINE TRY TO TYPE %s ?? %s" % (type(self.type_def), type(oth_type_def)))
        print("TRY TO unify %s ?? %s" % (self.type_def, oth_type_def))
        return self.type_def.unify(oth_type_def, blhs, brhs)

    def log_it(self, l: Log):
        l.type_log += [str(self)]

    def __len__(self) -> int:
        return len(self.type_def)

    def __getitem__(self, idx) -> TypeExprComponent:
        return self.type_def[idx]

    def __str__(self) -> str:
        return "%s: %s" % (self.name, self.type_def)

    def __repr__(self) -> str:
        return str(self)

class UnknownName(Term):
    """
    Implement unknown names: ?0, ?1, ?2
    """
    count = 0
    minarity = 1
    def __init__(self):
        Term.__init__(self)
        self.anonname = '?%d' % UnknownName.count
        UnknownName.count += 1

    def __lt__(self, oth):
        return self.anonname < oth.anonname

    def unify(self, oth_type_def: TypeExprComponent, blhs, brhs) -> TypeExprComponent:
        """
        When we unify an Unknown Name vs another type def we always match
        """
        print("UNK TRY TO unify %s ?? %s" % (self, oth_type_def))

    def log_it(self, l: Log):
        l.type_log += [str(self)]
        if self.link is not None:
            l.annexe_log += [self.anonname + ': ' + str(self.link())]

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

class Overload(TypeExprComponent):
    contains = {'Fun', 'T', 'N', 'UnknownName'}
    minarity = 0

    def unify(self, oth_type_def: TypeExprComponent, blhs, brhs) -> TypeExprComponent:
        """
        When we unify an overload vs another type def we match each fun and we return the rest.
    
        t1 ^ t2 ?? t1 match and we return t1
        t1 ^ t2 ?? t2 match and we return t2
        """
        print("OV TRY TO unify %s ?? %s" % (self, oth_type_def))
        ovres = Overload()
        for ov in self:
            if not ov.unify(oth_type_def, blhs, brhs):
                return None
            ovres.append(oth_type_def)
        return ovres

    def __str__(self) -> str:
        return "\n^ ".join(self.reprlist)

class Fun(TypeExprComponent):
    contains = {'Fun', 'Union', 'Tuple', 'UnknownName', 'T', 'N', 'Term', 'Expr'}
    minarity = 1

    def unify(self, oth_type_def: TypeExprComponent, blhs, brhs) -> TypeExprComponent:
        """
        When we unify a function vs another type def we match each term and we return the rest.
    
        t1 -> t2 -> t3 ?? t1 -> t2 match and we return t3
        t1 -> t2 ?? t1 -> t2 -> t3 didn't match

        Note: the first element is the return type (the last in repr)
        """
        print("FUN TRY TO unify %s ?? %s" % (self, oth_type_def))

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
        return " * ".join(self.reprlist)

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
