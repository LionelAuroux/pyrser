from typing import *

class ParsingBlock:
    """ Dummy Base class for all parse tree classes.
    """

class PeekChar(ParsingBlock):
    """
    !! 'a'
    """
    def __init__(self, value):
        self.value = value

class PeekText(ParsingBlock):
    """
    !! "toto"
    """
    def __init__(self, value):
        self.value = value

class Char(ParsingBlock):
    """
    'a'
    """
    def __init__(self, value):
        self.value = value

class Text(ParsingBlock):
    """
    "toto"
    """
    def __init__(self, value):
        self.value = value

class Range(ParsingBlock):
    """
    'a'..'z'
    """
    def __init__(self, begin, end):
        self.begin = begin
        self.end = end

class Seq(ParsingBlock):
    """
    A B C
    """
    def __init__(self, *arg: Tuple[ParsingBlock]):
        self.list = arg

class Alt(ParsingBlock):
    """
    A | B | C
    """
    def __init__(self, *arg: Tuple[ParsingBlock]):
        self.list = arg

class LookAhead(ParsingBlock):
    """
    !! R
    """
    def __init__(self, name, rule: ParsingBlock):
        self.name = name
        self.list = rule

class Neg(ParsingBlock):
    """
    ! R
    """
    def __init__(self, name, rule: ParsingBlock):
        self.name = name
        self.list = rule

class Complement(ParsingBlock):
    """
    ~ R
    """
    def __init__(self, name, rule: ParsingBlock):
        self.name = name
        self.list = rule

class Until(ParsingBlock):
    """
    -> R
    """
    def __init__(self, name, rule: ParsingBlock):
        self.name = name
        self.list = rule

class Capture(ParsingBlock):
    """
    A : b
    """
    def __init__(self, name, rule: ParsingBlock):
        self.name = name
        self.list = rule

class DeclNode(ParsingBlock):
    """
    __scope__ : b
    """
    def __init__(self, name):
        self.name = name

class RepOptional(ParsingBlock):
    """
    A ?
    """
    def __init__(self, rule: ParsingBlock):
        self.list = rule

class Rep0N(ParsingBlock):
    """
    A *
    """
    def __init__(self, rule: ParsingBlock):
        self.list = rule

class Rep1N(ParsingBlock):
    """
    A +
    """
    def __init__(self, rule: ParsingBlock):
        self.list = rule

class Rule(ParsingBlock):
    """
    A
    """
    def __init__(self, name):
        self.name = name

class Hook(ParsingBlock):
    """
    #withnoparam
    #withparam(a, b, c, d, ...)
    """
    def __init__(self, name, param: List[str]):
        self.name = name
        self.param = param

class Directive(ParsingBlock):
    """
    @withnoparam R
    @withparam(a, b, c, d, ...) R
    """
    def __init__(self, name, param: List[str], rule: ParsingBlock):
        self.name = name
        self.param = param
        self.list = rule

class DeclRule(ParsingBlock):
    """
    A = ...
    """
    def __init__(self, name, rule: ParsingBlock):
        self.name = name
        self.list = rule

class Decorator(ParsingBlock):
    """
    @withnoparam
    @withparam(a, b, c, d)
    A = ...
    """
    def __init__(self, name, param: List[Tuple[str]], rule: Union[DeclRule, 'Decorator']):
        self.name = name
        self.param = param
        self.list = rule

class Grammar(ParsingBlock):
    """
    grammar A
    from "something.peg" import B as C # other file
    from "thing.peg" import D # 
    import E # same file
    {
    }
    """
    def __init__(self, includes: List[Tuple[str, str, str]], *arg: Tuple[Union[Decorator, DeclRule]]):
        self.list = arg
