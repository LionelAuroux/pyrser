import inspect
import types
from pyrser import meta, error
from pyrser.parsing.base import BasicParser
from pyrser.parsing.node import Node
from pyrser.parsing.stream import Tag


_decorators = []


class Functor:
    """ Dummy Base class for all parse tree classes.

    common property:
        pt if contain a Functor
        ptlist if contain a list of Functor
    """

    def do_call(self, parser: BasicParser) -> Node:
        pass

    def __call__(self, parser: BasicParser) -> Node:
        global _decorators
        # call the begin methods in order
        for i in range(0, len(_decorators)):
            _decorators[i].begin(parser, self)
        # forward the call to the functor
        res = self.do_call(parser)
        # call the end methods in reverse order
        for i in range(len(_decorators) - 1, -1, -1):
            _decorators[i].end(res, parser, self)
        return res


class Directive2(Functor):
    def __init__(self, name, param: [(object, type)], pt: Functor):
        Functor.__init__(self)
        self.name = name
        self.pt = pt
        # compose the list of value param, check type
        for v, t in param:
            if type(t) is not type:
                raise TypeError(
                    "Must be pair of value and type (i.e: int, str, Node)")
        self.param = param

    def do_call(self, parser: BasicParser) -> bool:
        raise TypeError("Must be rewrite before execution")
        return False


class RewritingRules(Functor):
    """ Allow to write rewriting rules that transform
        the AST before code generation/interpretation.
    """

    def __init__(self, name: str=""):
        self.name = name


class SkipIgnore(Functor):
    """ Call Ignore Convention primitive functor. """

    def __init__(self, convention: str=""):
        """TODO: Could be better to implement Directive thru functors???"""
        self.convention = convention

    def do_call(self, parser: BasicParser) -> bool:
        #if len(parser._ignores) > 0:
        #    parser._ignores[-1](parser)
        parser.skip_ignore()
        return True


class Leaf:
    pass


class PeekChar(Functor, Leaf):
    """ !!'A' bnf primitive functor. """

    def __init__(self, c: str):
        self.char = c

    def do_call(self, parser: BasicParser) -> bool:
        return parser.peek_char(self.char)


class PeekText(Functor, Leaf):
    """ !!"TXT" bnf primitive functor. """

    def __init__(self, c: str):
        self.char = c

    def do_call(self, parser: BasicParser) -> bool:
        return parser.peek_text(self.char)


class Text(Functor, Leaf):
    """ "TXT" bnf primitive functor. """

    def __init__(self, txt: str):
        self.text = txt

    def do_call(self, parser: BasicParser) -> bool:
        return parser.read_text(self.text)


class Char(Functor, Leaf):
    """ 'A' bnf primitive functor. """

    def __init__(self, c: str):
        self.char = c

    def do_call(self, parser: BasicParser) -> bool:
        return parser.read_char(self.char)


class Range(Functor, Leaf):
    """ 'A'..'Z' bnf primitive functor. """

    def __init__(self, begin: str, end: str):
        self.begin = begin
        self.end = end

    def do_call(self, parser: BasicParser) -> bool:
        return parser.read_range(self.begin, self.end)


class UntilChar(Functor, Leaf):
    """ ->'A' bnf primitive functor. """

    def __init__(self, c: str):
        self.char = c

    def do_call(self, parser: BasicParser) -> bool:
        return parser.read_until(self.char)


class Seq(Functor):
    """ A B C bnf primitive as a functor. """

    def __init__(self, *ptlist: Functor):
        Functor.__init__(self)
        if len(ptlist) == 0:
            raise TypeError("Expected Functor")
        self.ptlist = []
        for it in ptlist:
            if not isinstance(it, SkipIgnore):
                self.ptlist.append(it)
                self.ptlist.append(SkipIgnore())
        if not isinstance(self.ptlist[0], SkipIgnore):
            self.ptlist.insert(0, SkipIgnore())

    def __getitem__(self, idx) -> Functor:
        """ Hide SkipIgnore object from outside """
        if idx >= 0:
            idx = (idx * 2) + 1
        else:
            idx = len(self.ptlist) - ((idx + 1) * 2) - 2
        return self.ptlist[idx]

    def do_call(self, parser: BasicParser) -> bool:
        parser._stream.save_context()
        for pt in self.ptlist:
            if not pt(parser):
                return parser._stream.restore_context()
        return parser._stream.validate_context()


class Scope(Functor):
    """ functor to wrap SCOPE/rule directive or just []. """

    def __init__(self, begin: Seq, end: Seq, pt: Seq):
        Functor.__init__(self)
        self.begin = begin
        self.end = end
        self.pt = pt

    def do_call(self, parser: BasicParser) -> Node:
        if not self.begin(parser):
            return False
        res = self.pt(parser)
        if not self.end(parser):
            return False
        return res


class LookAhead(Functor):
    """ !!A bnf primitive as a functor. """
    def __init__(self, pt: Functor):
        Functor.__init__(self)
        self.pt = pt
        if isinstance(self.pt, Seq):
            if isinstance(self.pt.ptlist[0], SkipIgnore):
                self.pt.ptlist.pop(0)
            if isinstance(self.pt.ptlist[-1], SkipIgnore):
                self.pt.ptlist.pop()

    def do_call(self, parser: BasicParser) -> bool:
        parser._stream.save_context()
        res = self.pt(parser)
        parser._stream.restore_context()
        return res


class Neg(Functor):
    """ !A bnf primitive as a functor. """

    def __init__(self, pt: Functor):
        Functor.__init__(self)
        self.pt = pt
        if isinstance(self.pt, Seq):
            if isinstance(self.pt.ptlist[0], SkipIgnore):
                self.pt.ptlist.pop(0)
            if isinstance(self.pt.ptlist[-1], SkipIgnore):
                self.pt.ptlist.pop()

    def do_call(self, parser: BasicParser):
        parser._stream.save_context()
        if self.pt(parser):
            res = parser._stream.restore_context()
            return res
        return parser._stream.validate_context()


class Complement(Functor):
    """ ~A bnf primitive as a functor. """

    def __init__(self, pt: Functor):
        Functor.__init__(self)
        self.pt = pt
        if isinstance(self.pt, Seq):
            if isinstance(self.pt.ptlist[0], SkipIgnore):
                self.pt.ptlist.pop(0)
            if isinstance(self.pt.ptlist[-1], SkipIgnore):
                self.pt.ptlist.pop()

    def do_call(self, parser: BasicParser) -> bool:
        if parser.read_eof():
            return False
        parser._stream.save_context()
        res = self.pt(parser)
        if not res:
            parser._stream.incpos()
            return parser._stream.validate_context()
        parser._stream.restore_context()
        return False


class Until(Functor):
    """ ->A bnf primitive as a functor. """

    def __init__(self, pt: Functor):
        Functor.__init__(self)
        self.pt = pt
        if isinstance(self.pt, Seq):
            if isinstance(self.pt.ptlist[0], SkipIgnore):
                self.pt.ptlist.pop(0)
            if isinstance(self.pt.ptlist[-1], SkipIgnore):
                self.pt.ptlist.pop()

    def do_call(self, parser: BasicParser) -> bool:
        parser._stream.save_context()
        while not parser.read_eof():
            res = self.pt(parser)
            if res:
                return parser._stream.validate_context()
            parser._stream.incpos()
        parser._stream.restore_context()
        parser.undo_last_ignore()
        return False


class Call(Functor):
    """ Functor wrapping a BasicParser method call in a BNF clause. """

    def __init__(self, callObject, *params):
        Functor.__init__(self)
        self.callObject = callObject
        self.params = params

    def do_call(self, parser: BasicParser) -> Node:
        return self.callObject(parser, *self.params)


class CallTrue(Call):
    """ Functor to wrap arbitrary callable object in BNF clause. """

    def do_call(self, parser: BasicParser) -> Node:
        self.callObject(*self.params)
        return True


class Capture(Functor):
    """ Functor to handle capture nodes. """

    def __init__(self, tagname: str, pt: Functor):
        Functor.__init__(self)
        if not isinstance(tagname, str) or len(tagname) == 0:
            raise TypeError("Illegal tagname for capture")
        self.tagname = tagname
        self.pt = pt
        if isinstance(self.pt, Seq):
            if isinstance(self.pt.ptlist[-1], SkipIgnore):
                self.pt.ptlist.pop()

    def do_call(self, parser: BasicParser) -> Node:
        if parser.begin_tag(self.tagname):
            # subcontext
            parser.push_rule_nodes()
            res = self.pt(parser)
            parser.pop_rule_nodes()
            if res and parser.end_tag(self.tagname):
                tag = parser.get_tag(self.tagname)
                # no bindings, wrap it in a Node instance
                if type(res) is bool:
                    res = Node()
                # update node cache
                parser.tag_node(self.tagname, res)
                parser.rule_nodes[self.tagname] = res
                # forward nodes
                return res
        return False


class DeclNode(Functor):
    """ Functor to handle node declaration with __scope__:N. """

    def __init__(self, tagname: str):
        Functor.__init__(self)
        if not isinstance(tagname, str) or len(tagname) == 0:
            raise TypeError("Illegal tagname for capture")
        self.tagname = tagname

    def do_call(self, parser: BasicParser) -> Node:
        parser.rule_nodes[self.tagname] = Node()
        return True


class Bind(Functor):
    """ Functor to handle the binding of a resulting nodes
        to an existing name.
    """

    def __init__(self, tagname: str, pt: Functor):
        Functor.__init__(self)
        if not isinstance(tagname, str) or len(tagname) == 0:
            raise TypeError("Illegal tagname for capture")
        self.tagname = tagname
        self.pt = pt

    def do_call(self, parser: BasicParser) -> Node:
        res = self.pt(parser)
        if res:
            parser.bind(self.tagname, res)
            return res
        return False


class Alt(Functor):
    """ A | B bnf primitive as a functor. """

    def __init__(self, *ptlist: Seq):
        Functor.__init__(self)
        self.ptlist = ptlist

    def __getitem__(self, idx) -> Functor:
        return self.ptlist[idx]

    def do_call(self, parser: BasicParser) -> Node:
        # save result of current rule
        parser.push_rule_nodes()
        for pt in self.ptlist:
            parser._stream.save_context()
            parser.push_rule_nodes()
            res = pt(parser)
            if res:
                parser.pop_rule_nodes()
                parser.pop_rule_nodes()
                parser._stream.validate_context()
                return res
            parser.pop_rule_nodes()
            parser._stream.restore_context()
        parser.pop_rule_nodes()
        return False


class RepOptional(Functor):
    """ []? bnf primitive as a functor. """
    def __init__(self, pt: Seq):
        Functor.__init__(self)
        self.pt = pt
        if (isinstance(self.pt, Text) or isinstance(self.pt, Char)
            or isinstance(self.pt, Range) or isinstance(self.pt, Directive)
        ):
            self.pt = Seq(self.pt)

    def do_call(self, parser: BasicParser) -> bool:
        res = self.pt(parser)
        if res:
            return res
        return True


class Rep0N(Functor):
    """ []* bnf primitive as a functor. """

    def __init__(self, pt: Seq):
        Functor.__init__(self)
        self.pt = pt
        if (isinstance(self.pt, Text) or isinstance(self.pt, Char)
            or isinstance(self.pt, Range) or isinstance(self.pt, Directive)
        ):
            self.pt = Seq(self.pt)

    def do_call(self, parser: BasicParser) -> bool:
        parser._stream.save_context()
        parser.push_rule_nodes()
        while self.pt(parser):
            pass
        parser.pop_rule_nodes()
        return parser._stream.validate_context()


class Rep1N(Functor):
    """ []+ bnf primitive as a functor. """

    def __init__(self, pt: Seq):
        Functor.__init__(self)
        self.pt = pt
        if (isinstance(self.pt, Text) or isinstance(self.pt, Char)
            or isinstance(self.pt, Range) or isinstance(self.pt, Directive)
        ):
            self.pt = Seq(self.pt)

    def do_call(self, parser: BasicParser) -> bool:
        parser._stream.save_context()
        parser.push_rule_nodes()
        if self.pt(parser):
            while self.pt(parser):
                pass
            parser.pop_rule_nodes()
            return parser._stream.validate_context()
        parser.pop_rule_nodes()
        return parser._stream.restore_context()


class Error(Functor):
    """ Raise an error. """

    def __init__(self, msg: str, **kwargs):
        self.msg = msg
        self.kw = kwargs

    def do_call(self, parser: BasicParser) -> bool:
        parser.diagnostic.notify(
            error.Severity.ERROR,
            self.msg,
            error.LocationInfo.from_stream(parser._stream, is_error=True)
        )
        raise parser.diagnostic


class Rule(Functor, Leaf):
    """ Call a rule by its name. """

    def __init__(self, name: str):
        Functor.__init__(self)
        self.name = name

    def do_call(self, parser: BasicParser) -> Node:
        parser.push_rule_nodes()
        res = parser.eval_rule(self.name)
        parser.pop_rule_nodes()
        return res


class Hook(Functor, Leaf):
    """ Call a hook by his name. """

    def __init__(self, name: str, param: [(object, type)]):
        Functor.__init__(self)
        self.name = name
        # compose the list of value param, check type
        for v, t in param:
            if type(t) is not type:
                raise TypeError("Must be pair of value and type (i.e: int, "
                                "str, Node)")
        self.param = param

    def do_call(self, parser: BasicParser) -> bool:
        valueparam = []
        for v, t in self.param:
            if t is Node:
                if v not in parser.rule_nodes:
                    parser.diagnostic.notify(
                        error.Severity.ERROR,
                        "Unknown capture variable : %s" % v,
                        error.LocationInfo.from_stream(
                            parser._stream,
                            is_error=True
                        )
                    )
                    raise parser.diagnostic
                valueparam.append(parser.rule_nodes[v])
            elif type(v) is t:
                valueparam.append(v)
            else:
                raise TypeError("Type mismatch expected {} got {}".format(
                    t, type(v)))
        return parser.eval_hook(self.name, valueparam)


class MetaDirectiveWrapper(type):
    """ metaclass of all DirectiveWrapper subclasses.
    ensure that begin and end exists in subclasses as method
    """
    def __new__(metacls, name, bases, namespace):
        cls = type.__new__(metacls, name, bases, namespace)
        if 'begin' not in namespace:
            raise TypeError(
                "DirectiveWrapper %s must have a begin method" % name)
        if not(isinstance(namespace['begin'], types.FunctionType)):
            raise TypeError(
                "'begin' not a function class in DirectiveWrapper %s" % name)
        if 'end' not in namespace:
            raise TypeError(
                "DirectiveWrapper %s subclasse must have a end method" % name)
        if not(isinstance(namespace['end'], types.FunctionType)):
            raise TypeError(
                "'end' not a function class in DirectiveWrapper %s" % name)
        return cls


class DirectiveWrapper(Functor, metaclass=MetaDirectiveWrapper):
    """ functor to wrap begin/end directive """

    def __init__(self, ):
        Functor.__init__(self)

    def checkParam(self, params: list):
        if (not hasattr(self.__class__, 'begin') or
                not hasattr(self.__class__, 'end')):
            return False
        sbegin = inspect.signature(self.begin)
        send = inspect.signature(self.end)

        idx = 0
        for param in list(sbegin.parameters.values())[1:]:
            if idx >= len(params) and param.default is inspect.Parameter.empty:
                raise RuntimeError("{}: No parameter given to begin"
                                   " method for argument {}, expected {}".
                                   format(
                                       self.__class__.__name__,
                                       idx, param.annotation))
            elif (idx < len(params)
                  and not isinstance(params[idx], param.annotation)):
                raise TypeError(
                    "{}: Wrong parameter in begin method parameter {} "
                    "expected {} got {}".format(
                        self.__class__.__name__,
                        idx, type(params[idx]),
                        param.annotation))
            idx += 1

        idx = 0
        for param in list(send.parameters.values())[1:]:
            if idx >= len(params) and param.default is inspect.Parameter.empty:
                raise RuntimeError("{}: No parameter given to end"
                                   " method for argument {}, expected {}".
                                   format(
                                       self.__class__.__name__,
                                       idx, param.annotation))
            elif (idx < len(params)
                  and not isinstance(params[idx], param.annotation)):
                raise TypeError(
                    "{}: Wrong parameter in end method parameter {} "
                    "expected {} got {}".format(
                        self.__class__.__name__,
                        idx, type(params[idx]),
                        param.annotation))
            idx += 1

        return True

    def begin(self):
        pass

    def end(self):
        pass


class Directive(Functor):
    """ functor to wrap directive HOOKS """

    def __init__(self, directive: DirectiveWrapper, param: [(object, type)],
                 pt: Functor):
        Functor.__init__(self)
        self.directive = directive
        self.pt = pt
        # compose the list of value param, check type
        for v, t in param:
            if type(t) is not type:
                raise TypeError(
                    "Must be pair of value and type (i.e: int, str, Node)")
        self.param = param

    def do_call(self, parser: BasicParser) -> Node:
        valueparam = []
        for v, t in self.param:
            if t is Node:
                valueparam.append(parser.rule_nodes[v])
            elif type(v) is t:
                valueparam.append(v)
            else:
                raise TypeError(
                    "Type mismatch expected {} got {}".format(t, type(v)))
        if not self.directive.checkParam(valueparam):
            return False
        if not self.directive.begin(parser, *valueparam):
            return False
        res = self.pt(parser)
        if not self.directive.end(parser, *valueparam):
            return False
        return res


class MetaDecoratorWrapper(type):
    """ metaclass of all DecoratorWrapper subclasses.
    ensure that begin and end exists in subclasses as method
    """
    def __new__(metacls, name, bases, namespace):
        cls = type.__new__(metacls, name, bases, namespace)
        if 'begin' not in namespace:
            raise TypeError(
                "DirectiveWrapper %s must have a begin method" % name)
        if not(isinstance(namespace['begin'], types.FunctionType)):
            raise TypeError(
                "'begin' not a function class in DirectiveWrapper %s" % name)
        if 'end' not in namespace:
            raise TypeError(
                "DirectiveWrapper %s subclasse must have a end method" % name)
        if not(isinstance(namespace['end'], types.FunctionType)):
            raise TypeError(
                "'end' not a function class in DirectiveWrapper %s" % name)
        return cls


class DecoratorWrapper(Functor, metaclass=MetaDecoratorWrapper):

    def begin(self):
        pass

    def end(self):
        pass


class Decorator(Functor):
    def __init__(self, decoratorClass: type, param: [(object, type)],
                 pt: Functor):
        self.decorator_class = decoratorClass
        self.pt = pt
        # compose the list of value param, check type
        for v, t in param:
            if type(t) is not type:
                raise TypeError(
                    "Must be pair of value and type (i.e: int, str, Node)")
        self.param = param

    def checkParam(self, the_class: type, params: list) -> bool:
        sinit = inspect.signature(the_class.__init__)

        idx = 0
        for param in list(sinit.parameters.values())[1:]:
            if idx >= len(params) and param.default is inspect.Parameter.empty:
                raise RuntimeError("{}: No parameter given to begin"
                                   " method for argument {}, expected {}".
                                   format(
                                       the_class.__name__,
                                       idx, param.annotation))
            elif (idx < len(params)
                  and not isinstance(params[idx], param.annotation)):
                raise TypeError(
                    "{}: Wrong parameter in begin method parameter {} "
                    "expected {} got {}".format(
                        the_class.__name__,
                        idx, type(params[idx]),
                        param.annotation))
            idx += 1

        return True

    def do_call(self, parser: BasicParser) -> Node:
        """
            The Decorator call is the one that actually pushes/pops
            the decorator in the active decorators list (parsing._decorators)
        """
        valueparam = []
        for v, t in self.param:
            if t is Node:
                valueparam.append(parser.rule_nodes[v])
            elif type(v) is t:
                valueparam.append(v)
            else:
                raise TypeError(
                    "Type mismatch expected {} got {}".format(t, type(v)))

        if not self.checkParam(self.decorator_class, valueparam):
            return False

        decorator = self.decorator_class(*valueparam)

        global _decorators
        _decorators.append(decorator)
        res = self.pt(parser)
        _decorators.pop()

        return res
