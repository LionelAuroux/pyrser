from pyrser.parsing.parserBase import BasicParser
from pyrser.parsing.node import Node


class ParserTree:
    """Dummy Base class for all parse tree classes.

    common property:
        pt if contain a ParserTree
        ptlist if contain a list of ParserTree
    """
    pass


class Seq(ParserTree):
    """A B C bnf primitive as a functor."""

    def __init__(self, *ptlist: ParserTree):
        ParserTree.__init__(self)
        if len(ptlist) == 0:
            raise TypeError("Expected ParserTree")
        self.ptlist = ptlist

    def __call__(self, parser: BasicParser) -> bool:
        for pt in self.ptlist:
            parser.skipIgnore()
            if not pt(parser):
                return False
        return True


class Scope(ParserTree):
    """functor to wrap SCOPE/rule directive or just []."""

    def __init__(self, begin: Seq, end: Seq, pt: Seq):
        ParserTree.__init__(self)
        self.begin = begin
        self.end = end
        self.pt = pt

    def __call__(self, parser: BasicParser) -> Node:
        if not self.begin(parser):
            return False
        res = self.pt(parser)
        if not self.end(parser):
            return False
        return res


class Call(ParserTree):
    """Functor wrapping a BasicParser method call in a BNF clause."""

    def __init__(self, callObject, *params):
        ParserTree.__init__(self)
        #TODO(bps): fix the function vs. method mess
        import types
        if isinstance(callObject, types.MethodType):
            self.callObject = callObject.__func__
        else:
            self.callObject = callObject
        self.params = params

    def __call__(self, parser: BasicParser) -> Node:
        return self.callObject(parser, *self.params)


class CallTrue(Call):
    """Functor to wrap arbitrary callable object in BNF clause."""

    def __call__(self) -> Node:
        self.callObject(*self.params)
        return True


class Capture(ParserTree):
    """Functor to handle capture variables."""

    def __init__(self, tagname: str, pt: ParserTree):
        ParserTree.__init__(self)
        if not isinstance(tagname, str) or len(tagname) == 0:
            raise TypeError("Illegal tagname for capture")
        self.tagname = tagname
        self.pt = pt

    def __call__(self, parser: BasicParser) -> Node:
        if parser.beginTag(self.tagname):
            parser.rulenodes[-1][self.tagname] = Node()
            res = self.pt(parser)
            if res and parser.endTag(self.tagname):
                text = parser.getTag(self.tagname)
                # wrap it in a Node instance
                if type(res) is bool:
                    res = Node(res)
                #TODO(iopi): should be a future capture object for multistream
                # capture
                if not hasattr(res, 'value'):
                    res.value = text
                parser.rulenodes[-1][self.tagname] = res
                return res
        return False


class Alt(ParserTree):
    """A | B bnf primitive as a functor."""

    def __init__(self, *ptlist: Seq):
        ParserTree.__init__(self)
        self.ptlist = ptlist

    def __call__(self, parser: BasicParser) -> Node:
        for pt in self.ptlist:
            parser._stream.save_context()
            parser.skipIgnore()
            res = pt(parser)
            if res:
                parser._stream.validate_context()
                return res
            parser._stream.restore_context()
        return False


class RepOptional(ParserTree):
    """[]? bnf primitive as a functor."""
    def __init__(self, pt: Seq):
        ParserTree.__init__(self)
        self.pt = pt

    def __call__(self, parser: BasicParser) -> bool:
        parser.skipIgnore()
        self.pt(parser)
        return True


class Rep0N(ParserTree):
    """[]* bnf primitive as a functor."""

    #TODO(iopi): at each turn, pop/push rulenodes
    def __init__(self, pt: Seq):
        ParserTree.__init__(self)
        self.pt = pt

    def __call__(self, parser: BasicParser) -> bool:
        parser.skipIgnore()
        while self.pt(parser):
            parser.skipIgnore()
        return True


class Rep1N(ParserTree):
    """[]+ bnf primitive as a functor."""

    #TODO(iopi): at each turn, pop/push rulenodes
    def __init__(self, pt: Seq):
        ParserTree.__init__(self)
        self.pt = pt

    def __call__(self, parser: BasicParser) -> bool:
        parser.skipIgnore()
        if self.pt(parser):
            parser.skipIgnore()
            while self.pt(parser):
                parser.skipIgnore()
            return True
        return False


class Rule(ParserTree):
    """Call a rule by its name."""

    #TODO(iopi): Handle additionnal value
    def __init__(self, name: str):
        ParserTree.__init__(self)
        self.name = name

    def __call__(self, parser: BasicParser) -> Node:
        return parser.evalRule(self.name)


class Hook(ParserTree):
    """Call a hook by his name."""

    def __init__(self, name: str, param: [(object, type)]):
        ParserTree.__init__(self)
        self.name = name
        # compose the list of value param, check type
        for v, t in param:
            if type(t) is not type:
                raise TypeError("Must be pair of value and type (i.e: int, "
                                "str, Node)")
        self.param = param

    def __call__(self, parser: BasicParser) -> bool:
        valueparam = []
        for v, t in self.param:
            if t is Node:
                import weakref
                valueparam.append(weakref.proxy(parser.rulenodes[-1][v]))
            elif type(v) is t:
                valueparam.append(v)
            else:
                raise TypeError("Type mismatch expected {} got {}".format(
                    t, type(v)))
        return parser.evalHook(self.name, valueparam)


class DirectiveWrapper(object):
    """functor to wrap begin/end directive"""

    def __init__(self, ):
        ParserTree.__init__(self)

    def checkParam(self, params: list):
        print("REPR %r" % dir(self.__class__))
        if ('begin' not in dir(self.__class__)) or ('end' not in dir(self.__class__)):
            return False
        pbegin = self.__class__.begin.__code__.co_varnames
        fbegin = self.__class__.begin.__annotations__
        pend = self.__class__.end.__code__.co_varnames
        fend = self.__class__.end.__annotations__
        print("PARAM %s" % repr(pbegin))
        print("ANNOT %s" % repr(fbegin))
        for value, idx in zip(params, range(len(params))):
            print("ITER PARAMS %s %s" % (value, idx))
        return True

    # must be define in inherited class
    #def begin(self, parser, ...):
    #    pass

    # must be define in inherited class
    #def end(self, parser, ...):
    #    pass


class Directive(ParserTree):
    """functor to wrap directive HOOKS"""

    def __init__(self, directive: DirectiveWrapper, param: [(object, type)], pt: ParserTree):
        ParserTree.__init__(self)
        self.directive = directive
        self.pt = pt
        # compose the list of value param, check type
        for v, t in param:
            if type(t) is not type:
                raise TypeError("Must be pair of value and type (i.e: int, str, Node)")
        self.param = param

    def __call__(self, parser: BasicParser) -> Node:
        valueparam = []
        for v, t in self.param:
            if t is Node:
                valueparam.append(weakref.proxy(parser.rulenodes[-1][v]))
            elif type(v) is t:
                valueparam.append(v)
            else:
                raise TypeError("Type mismatch expected {} got {}".format(t, type(v)))
        print("LIST CONTENT %s" % repr(valueparam))
        if not self.directive.checkParam(valueparam):
            return False
        if not self.directive.begin(parser, *valueparam):
            return False
        res = self.pt(parser)
        if not self.directive.end(parser, *valueparam):
            return False
        return res

