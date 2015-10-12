from weakref import *
from pyrser import fmt
from pyrser.grammar import *

#
# TODO: define TypeExpr DSL to write Type Compent's Tree in a easy way.
# example:
#   int
#   list<string>
#   map<string, int>
#   *<int>
#   *[size=20]<char> : array size as attribute of type *
#   *[const]<char[const]> : attribute syntaxe []
#   *[size=20,const]<char> : array size as attribute of type *


class TypeName:
    def __init__(self, name: str=None):
        self.name = name
        self.attributes = {}

    def set_attr(self, name: str, value=None):
        self.attributes[name] = value

    def get_attr(self, name: str) -> object:
        return self.attributes[name]

    def to_fmt(self) -> fmt.indentable:
        txt = fmt.sep("", [self.name])
        if len(self.attributes) > 0:
            lsattr = fmt.sep(", ", [])
            lkey = sorted(self.attributes.keys())
            for k in lkey:
                t = k
                if self.attributes[k] is not None:
                    t += '=' + str(self.attributes[k])
                lsattr.lsdata.append(t)
            txt.lsdata.append(fmt.block("[", "]", lsattr))
        return txt


class RealName(TypeName):
    pass


class AbstractName(TypeName):
    def to_fmt(self) -> fmt.indentable:
        return fmt.sep("", ['?', TypeName.to_fmt(self)])


class DeltaComponentTypeName:
    def __init__(self):
        self.diff = []

    def __len__(self):
        return 0

    def add(self, d1, d2):
        class D(dict):
            pass
        d = D()
        d.wref1 = ref(d1)
        d.wref2 = ref(d2)
        self.diff.append(d)


class ComponentTypeName:
    pass


class ComponentTypeName:

    empty = TypeName()

    def __init__(self):
        self.__name = None
        self.__params = []
        self.__subcomponent = None

    def __sub__(self, other: ComponentTypeName) -> DeltaComponentTypeName:
        res = DeltaComponentTypeName()
        s1 = self.__name
        s2 = other._ComponentTypeName__name
        if s1 != s2:
            res.add(s1, s2)
        l1 = len(self.__params)
        l2 = len(other._ComponentTypeName__params)
        s = max(l1, l2)
        for i in range(s):
            if i < l1 and i < l2:
                res.add(self.__params[i], other._ComponentTypeName__params[i])
            elif i >= l1:
                res.add(
                    ComponentTypeName.empty,
                    other._ComponentTypeName__params[i]
                )
            elif i >= l2:
                res.add(self.__params[i], ComponentTypeName.empty)
        if (self.__subcomponent is not None
            and other._ComponentTypeName__subcomponent is not None
        ):
            sc = self.__subcomponent
            osc = other._ComponentTypeName__subcomponent
            subdiff = sc - osc
            res.diff += subdiff.diff
        elif self.__subcomponent is not None:
            res.add(self.__subcomponent, ComponentTypeName.empty)
        elif other._ComponentTypeName__subcomponent is not None:
            res.add(
                ComponentTypeName.empty,
                other._ComponentTypeName__subcomponent
            )
        return res

    def set_name(self, tn: TypeName) -> ComponentTypeName:
        if not isinstance(tn, TypeName):
            raise TypeError("tn must be a TypeName")
        self.__name = tn
        return self

    def set_params(self, params: [ComponentTypeName]) -> ComponentTypeName:
        i = 0
        for p in params:
            if not isinstance(p, ComponentTypeName):
                raise TypeError("params[%d] must be a ComponentTypeName" % i)
            self.__params.append(p)
            i += 1
        return self

    def add_params(self, param: ComponentTypeName) -> ComponentTypeName:
        if not isinstance(param, ComponentTypeName):
            raise TypeError("param must be a ComponentTypeName")
        self.__params.append(param)
        return self

    def set_subcomponent(self, sc: ComponentTypeName) -> ComponentTypeName:
        if not isinstance(sc, ComponentTypeName):
            raise TypeError("sc must be a ComponentTypeName")
        self.__subcomponent = sc
        return self

    @property
    def name(self) -> TypeName:
        return self.__name

    @property
    def subcomponent(self) -> ComponentTypeName:
        return self.__subcomponent

    @property
    def paramitems(self) -> iter:
        return self.__params.items()

    @property
    def isRealType(self) -> bool:
        return isinstance(self.__name, RealName)

    @property
    def isAbstractType(self) -> bool:
        return isinstance(self.__name, AbstractName)

    @property
    def isPackage(self) -> bool:
        return len(self.__params) == 0

    @property
    def isParametric(self) -> bool:
        return len(self.__params) > 0

    def to_fmt(self) -> fmt.indentable:
        lsub = []
        txtfinal = fmt.sep(".", lsub)
        lself = []
        txtself = fmt.sep("", lself)
        lself.append(self.__name.to_fmt())
        if len(self.__params) > 0:
            lsp = []
            for p in self.__params:
                lsp.append(p.to_fmt())
            txtparams = fmt.block("<", ">", lsp)
            lself.append(txtparams)
        lsub.append(lself)
        if self.__subcomponent is not None:
            lsub.append(self.__subcomponent.to_fmt())
        return txtfinal

    def __str__(self) -> str:
        return str(self.to_fmt())


class TypeExprParser(Grammar):
    entry = 'atype'
    grammar = """
        atype = [ component ['.' component]* ]

        component = [ typename [params]?]

        params = [ '<' typename [',' typename]* '>']

        typename = ['?'? ~' '+ [attr]? ]

        attr = [ '[' kv [',' kv]* ']' ]

        kv = [ id ['=' value]?]
    """


class TypeExpr:
    def __init__(self, expr):
        self.expr = expr
        parser = TypeExprParser()
        self.tn = parser.parse(self.expr)

    @property
    def getCTN(self) -> ComponentTypeName:
        return self.tn
