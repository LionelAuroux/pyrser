import collections
import os

from pyrser import meta
from pyrser import error
from pyrser.parsing.stream import Stream
from pyrser.parsing.stream import Tag
from pyrser.parsing.node import Node

# TODO: ensure unicity of names
#: Module variable to store meta class instance by classname
_MetaBasicParser = {}


class MetaBasicParser(type):
    """Metaclass for all parser."""
    def __new__(metacls, name, bases, namespace):
        global _MetaBasicParser
        # create the metaclass instance
        cls = type.__new__(metacls, name, bases, namespace)
        # search metaclass instance of all base
        if len(bases) > 1:
            raise TypeError("%s must inherit from an unique parent,"
                            " use Grammar for aggregation" % name)
        # Manage inheritance of Parser
        if len(bases) == 1:
            strbase = bases[0].__name__
            if strbase not in _MetaBasicParser:
                raise TypeError("metaclass of %s not found"
                                % bases[0].__name__)
            # we inherit from an already constructed parser, so get metaclass
            clsbase = _MetaBasicParser[strbase]
            # inherit rules from parser
            if hasattr(clsbase, '_rules'):
                cls._rules = clsbase._rules.new_child()
            # inherit hooks from parser
            if hasattr(clsbase, '_hooks'):
                cls._hooks = clsbase._hooks.new_child()
        # add localy defined rules
        if '_rules' in namespace:
            cls._rules.update(namespace['_rules'])
        # add localy defined hooks
        if '_hooks' in namespace:
            cls._hooks.update(namespace['_hooks'])
        # store in global registry
        _MetaBasicParser[name] = cls
        return cls


class BasicParser(metaclass=MetaBasicParser):
    """Empty basic parser, contains no rule nor hook.

    Unless you know what you are doing, use Parser instead of this class.

    """

    _rules = collections.ChainMap()
    _hooks = collections.ChainMap()

    def __init__(
            self,
            content: str='',
            stream_name: str=None,
            raise_diagnostic=True
    ):
        self._ignores = [BasicParser.ignore_blanks]
        self._streams = [Stream(content, stream_name)]
        self.rule_nodes = None
        self.push_rule_nodes()
        self._lastIgnoreIndex = 0
        self._lastIgnore = False
        self._lastRule = ""
        self.raise_diagnostic = raise_diagnostic
        self.diagnostic = error.Diagnostic()

### READ ONLY @property
    def __bool__(self):
        return self.diagnostic is False

    @property
    def _stream(self) -> Stream:
        """The current Stream."""
        return self._streams[-1]

    @property
    def nstream(self) -> int:
        """Return the number of opened stream"""
        return len(self._streams)

    @property
    def rules(self) -> dict:
        """
        Return the grammar dict
        """
        return self._rules

### Rule Nodes

    def push_rule_nodes(self) -> bool:
        """Push context variable to store rule nodes."""
        if self.rule_nodes is None:
            self.rule_nodes = collections.ChainMap()
            self.tag_cache = collections.ChainMap()
            self.id_cache = collections.ChainMap()
        else:
            self.rule_nodes = self.rule_nodes.new_child()
            self.tag_cache = self.tag_cache.new_child()
            self.id_cache = self.id_cache.new_child()
        return True

    def pop_rule_nodes(self) -> bool:
        """Pop context variable that store rule nodes"""
        self.rule_nodes = self.rule_nodes.parents
        self.tag_cache = self.tag_cache.parents
        self.id_cache = self.id_cache.parents
        return True

    def value(self, n: Node) -> str:
        """Return the text value of the node"""
        id_n = id(n)
        idcache = self.id_cache
        if id_n not in idcache:
            return ""
        name = idcache[id_n]
        tag_cache = self.tag_cache
        if name not in tag_cache:
            raise Exception("Incoherent tag cache")
        tag = tag_cache[name]
        k = "%d:%d" % (tag._begin, tag._end)
        valcache = self._streams[-1].value_cache
        if k not in valcache:
            valcache[k] = str(tag)
        return valcache[k]

### STREAM

    def parsed_stream(self, content: str, name: str=None):
        """Push a new Stream into the parser.
        All subsequent called functions will parse this new stream,
        until the 'popStream' function is called.
        """
        self._streams.append(Stream(content, name))

    def pop_stream(self):
        """Pop the last Stream pushed on to the parser stack."""
        s = self._streams.pop()
        self.clean_tmp(s)

### VARIABLE PRIMITIVES

    def begin_tag(self, name: str) -> Node:
        """Save the current index under the given name."""
        # Check if we could attach tag cache to current rule_nodes scope
        self.tag_cache[name] = Tag(self._stream, self._stream.index)
        return True

    def end_tag(self, name: str) -> Node:
        """Extract the string between saved and current index."""
        self.tag_cache[name].set_end(self._stream.index)
        return True

    def get_tag(self, name: str) -> Tag:
        """Extract the string previously saved."""
        return self.tag_cache[name]

    def tag_node(self, name: str, node: Node):
        self.id_cache[id(node)] = name

####

    @classmethod
    def set_rules(cls, rules: dict) -> bool:
        """
        Merge internal rules set with the given rules
        """
        cls._rules = cls._rules.new_child()
        for rule_name, rule_pt in rules.items():
            if '.' not in rule_name:
                rule_name = cls.__module__ \
                    + '.' + cls.__name__ \
                    + '.' + rule_name
            meta.set_one(cls._rules, rule_name, rule_pt)
        return True

    @classmethod
    def set_hooks(cls, hooks: dict) -> bool:
        """
        Merge internal hooks set with the given hooks
        """
        cls._hooks = cls._hooks.new_child()
        for hook_name, hook_pt in hooks.items():
            if '.' not in hook_name:
                hook_name = cls.__module__ \
                    + '.' + cls.__name__ \
                    + '.' + hook_name
            meta.set_one(cls._hooks, hook_name, hook_pt)
        return True

    @classmethod
    def set_directives(cls, directives: dict) -> bool:
        """
        Merge internal directives set with the given directives.
        For working directives, attach it only in the dsl.Parser class
        """
        meta._directives = meta._directives.new_child()
        for dir_name, dir_pt in directives.items():
            meta.set_one(meta._directives, dir_name, dir_pt)
            dir_pt.ns_name = dir_name
        return True

    def eval_rule(self, name: str) -> Node:
        """Evaluate a rule by name."""
        # context created by caller
        n = Node()
        id_n = id(n)
        self.rule_nodes['_'] = n
        self.id_cache[id_n] = '_'
        # TODO: other behavior for  empty rules?
        if name not in self.__class__._rules:
            self.diagnostic.notify(
                error.Severity.ERROR,
                "Unknown rule : %s" % name,
                error.LocationInfo.from_stream(self._stream, is_error=True)
            )
            raise self.diagnostic
        self._lastRule = name
        rule_to_eval = self.__class__._rules[name]
        # TODO: add packrat cache here, same rule - same pos == same res
        res = rule_to_eval(self)
        if res:
            res = self.rule_nodes['_']
        return res

    def eval_hook(self, name: str, ctx: list) -> Node:
        """Evaluate the hook by its name"""
        if name not in self.__class__._hooks:
            # TODO: don't always throw error, could have return True by default
            self.diagnostic.notify(
                error.Severity.ERROR,
                "Unknown hook : %s" % name,
                error.LocationInfo.from_stream(self._stream, is_error=True)
            )
            raise self.diagnostic
        self._lastRule = '#' + name
        res = self.__class__._hooks[name](self, *ctx)
        if type(res) is not bool:
            raise TypeError("Your hook %r didn't return a bool value" % name)
        return res

### PARSING PRIMITIVES

    def peek_char(self, c: str) -> bool:
        if self.read_eof():
            return False
        return self._stream.peek_char == c

    def peek_text(self, text: str) -> bool:
        """Same as readText but doesn't consume the stream."""
        start = self._stream.index
        stop = start + len(text)
        if stop > self._stream.eos_index:
            return False
        return self._stream[self._stream.index:stop] == text

    def one_char(self) -> bool:
        """Read one byte in stream"""
        if self.read_eof():
            return False
        self._stream.incpos()
        return True

    def read_char(self, c: str) -> bool:
        """
        Consume the c head byte, increment current index and return True
        else return False. It use peekchar and it's the same as '' in BNF.
        """
        if self.read_eof():
            return False
        self._stream.save_context()
        if c == self._stream.peek_char:
            self._stream.incpos()
            return self._stream.validate_context()
        return self._stream.restore_context()

    def read_until(self, c: str, inhibitor='\\') -> bool:
        """
        Consume the stream while the c byte is not read, else return false
        ex : if stream is " abcdef ", read_until("d"); consume "abcd".
        """
        if self.read_eof():
            return False
        self._stream.save_context()
        while not self.read_eof():
            if self.peek_char(inhibitor):
                # Delete inhibitor and inhibited character
                self.one_char()
                self.one_char()
            if self.peek_char(c):
                self._stream.incpos()
                return self._stream.validate_context()
            self._stream.incpos()
        return self._stream.restore_context()

    def read_until_eof(self) -> bool:
        """Consume all the stream. Same as EOF in BNF."""
        if self.read_eof():
            return True
        # TODO: read ALL
        self._stream.save_context()
        while not self.read_eof():
            self._stream.incpos()
        return self._stream.validate_context()

    def read_text(self, text: str) -> bool:
        """
        Consume a strlen(text) text at current position in the stream
        else return False.
        Same as "" in BNF
        ex : read_text("ls");.
        """
        if self.read_eof():
            return False
        self._stream.save_context()
        if self.peek_text(text):
            self._stream.incpos(len(text))
            return self._stream.validate_context()
        return self._stream.restore_context()

    def read_range(self, begin: str, end: str) -> int:
        """
        Consume head byte if it is >= begin and <= end else return false
        Same as 'a'..'z' in BNF
        """
        if self.read_eof():
            return False
        c = self._stream.peek_char
        if begin <= c <= end:
            self._stream.incpos()
            return True
        return False

### IGNORE CONVENTION

    def ignore_null(self) -> bool:
        """
        Empty ignore convention for notignore
        """
        return True

    def ignore_blanks(self) -> bool:
        """Consume whitespace characters."""
        self._stream.save_context()
        if not self.read_eof() and self._stream.peek_char in " \t\v\f\r\n":
            while (not self.read_eof()
                   and self._stream.peek_char in " \t\v\f\r\n"):
                self._stream.incpos()
            return self._stream.validate_context()
        return self._stream.validate_context()

    def push_ignore(self, ignoreConvention) -> bool:
        """Set the ignore convention"""
        self._ignores.append(ignoreConvention)
        return True

    def pop_ignore(self) -> bool:
        """Remove the last ignore convention"""
        self._ignores.pop()
        return True

    def skip_ignore(self) -> bool:
        if len(self._ignores) > 0:
            self._ignores[-1](self)
        self._lastIgnore = (self._stream.index != self._lastIgnoreIndex)
        self._lastIgnoreIndex = self._stream.index
        return True

    def undo_last_ignore(self) -> bool:
        # TODO(iopi): wrong don't work in all case
        if (self._stream.index > self._lastIgnoreIndex):
            self._stream.decpos(self._stream.index - self._lastIgnoreIndex)
            self._lastIgnoreIndex = self._stream.index
            #self._lastIgnore = False
        return True


class Parser(BasicParser):
    """An ascii parsing primitive library."""
    pass

### BASE RULES


@meta.hook(BasicParser)
def bind(self, dst: str, src: Node) -> bool:
    """Allow to alias a node to another name.

    Useful to bind a node to _ as return of Rule::

        R = [
            __scope__:L [item:I #add_item(L, I]* #bind('_', L)
        ]

    It's also the default behaviour of ':>'

    """

    for m in self.rule_nodes.maps:
        for k, v in m.items():
            if k == dst:
                m[k] = src
                return True
    raise Exception('%s not found' % dst)


@meta.rule(BasicParser, "Base.read_char")
def read_one_char(self) -> bool:
    return self.one_char()


@meta.rule(BasicParser, "Base.eof")
def read_eof(self) -> bool:
    """Returns true if reached end of the stream."""
    # TODO: handle multi-stream, pop last stream and continue if not the last
    return self._stream.index == self._stream.eos_index


@meta.rule(Parser, "Base.eol")
def read_eol(self) -> bool:
    """Return True if the parser can consume an EOL byte sequence."""
    if self.read_eof():
        return False
    self._stream.save_context()
    self.read_char('\r')
    if self.read_char('\n'):
        return self._stream.validate_context()
    return self._stream.restore_context()


@meta.rule(Parser, "Base.hex_num")
def read_hex_integer(self) -> bool:
    """
    Read the following BNF rule else return False::

        readHexInteger = [
            [ '0'..'9' | 'a'..'f' | 'A'..'F' ]+
        ]
    """
    if self.read_eof():
        return False
    self._stream.save_context()
    c = self._stream.peek_char
    if c.isdigit() or ('a' <= c.lower() and c.lower() <= 'f'):
        self._stream.incpos()
        while not self.read_eof():
            c = self._stream.peek_char
            if not (c.isdigit() or ('a' <= c.lower() and c.lower() <= 'f')):
                break
            self._stream.incpos()
        return self._stream.validate_context()
    return self._stream.restore_context()


@meta.rule(Parser, "Base.oct_num")
def read_oct_integer(self) -> bool:
    """
    Read the following BNF rule else return False::

        readOctInteger = [
            [ '0'..'7' ]+
        ]
    """
    if self.read_eof():
        return False
    self._stream.save_context()
    c = self._stream.peek_char
    if c.isdigit() and 0 <= int(c) and int(c) <= 7:
        self._stream.incpos()
        while not self.read_eof():
            c = self._stream.peek_char
            if not (c.isdigit() and 0 <= int(c) and int(c) <= 7):
                break
            self._stream.incpos()
        return self._stream.validate_context()
    return self._stream.restore_context()


@meta.rule(Parser, "Base.num")
def read_integer(self) -> bool:
    """
    Read following BNF rule else return False::

        readInteger = [
            ['0'..'9']+
        ]

    """
    if self.read_eof():
        return False
    self._stream.save_context()
    c = self._stream.peek_char
    if c.isdigit():
            self._stream.incpos()
            while not self.read_eof():
                c = self._stream.peek_char
                if not c.isdigit():
                    break
                self._stream.incpos()
            return self._stream.validate_context()
    return self._stream.restore_context()


# `Base.id`
@meta.rule(Parser, "Base.id")
def read_identifier(self) -> bool:
    """
    Read following BNF rule else return False::

        readIdentifier = [
            ['a'..'z'|'A'..'Z'|'_']['0'..'9'|'a'..'z'|'A'..'Z'|'_']*
        ]

    """
    if self.read_eof():
        return False
    self._stream.save_context()
    c = self._stream.peek_char
    if c.isalpha() or c == '_':
            self._stream.incpos()
            while not self.read_eof():
                c = self._stream.peek_char
                if not (c.isalpha() or c.isdigit() or c == '_'):
                    break
                self._stream.incpos()
            return self._stream.validate_context()
    return self._stream.restore_context()


@meta.rule(Parser, "Base.string")
def read_cstring(self) -> bool:
    """
    Read following BNF rule else return False::

        '"' -> ['\\' #char | ~'\\'] '"'

    """
    self._stream.save_context()
    idx = self._stream.index
    if self.read_char("\"") and self.read_until("\"", "\\"):
        txt = self._stream[idx:self._stream.index]
        return self._stream.validate_context()
    return self._stream.restore_context()


@meta.rule(Parser, "Base.char")
def read_cchar(self) -> bool:
    # TODO(iopi): octal digit, hex digit
    """
    Read following BNF rule else return False::

        "'" -> ['\\' #char | ~'\\'] "'"

    """
    self._stream.save_context()
    idx = self._stream.index
    if self.read_char("\'") and self.read_until("\'", "\\"):
        txt = self._stream[idx:self._stream.index]
        return self._stream.validate_context()
    return self._stream.restore_context()


@meta.rule(Parser, "__scope__")
def scope_nodes(self) -> bool:
    """Used for create scoped nodes"""
    return True
