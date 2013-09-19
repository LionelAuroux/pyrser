from pyrser import meta
from pyrser import error
from pyrser.parsing.parserStream import Stream
from pyrser.parsing.node import Node
import collections

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
    """Emtpy basic parser, contains no rule nor hook.

    Unless you know what you are doing, use Parser instead of this class.

    """
    _rules = collections.ChainMap()
    _hooks = collections.ChainMap()

    def __init__(self, content: str='', stream_name: str="root"):
        self._ignores = [BasicParser.ignore_blanks]
        self.__streams = [Stream(content, stream_name)]
        self.__tags = {}
        self.rulenodes = collections.ChainMap()
        self._lastIgnoreIndex = 0
        self._lastIgnore = False

### READ ONLY @property

    @property
    def _stream(self) -> Stream:
        """The current Stream."""
        return self.__streams[-1]

    @property
    def rules(self) -> dict:
        """
        Return the grammar dict
        """
        return self._rules

### Rule Nodes

    def push_rule_nodes(self) -> bool:
        """Push context variable to store rule nodes."""
        self.rulenodes = self.rulenodes.new_child()
        return True

    def pop_rule_nodes(self) -> bool:
        """Pop context variable that store rule nodes"""
        self.rulenodes = self.rulenodes.parents
        return True

### STREAM

    def parsed_stream(self, sNewStream: str, sName="string"):
        """Push a new Stream into the parser.
        All subsequent called functions will parse this new stream,
        until the 'popStream' function is called.
        """
        self.__streams.append(Stream(sNewStream, sName))

    def pop_stream(self):
        """Pop the last Stream pushed on to the parser stack."""
        self.__streams.pop()

### VARIABLE PRIMITIVES

# TODO(iopi): change for beginTag,endTag,getTag for multicapture,
# and typesetting at endTag (i.e: readCChar,readCString need transcoding)
    def begin_tag(self, name: str) -> Node:
        """Save the current index under the given name."""
        self.__tags[name] = {'begin': self._stream.index}
        return Node(True)

    def end_tag(self, name: str) -> Node:
        """Extract the string between saved and current index."""
        self.__tags[name]['end'] = self._stream.index
        return Node(True)

    def get_tag(self, name: str) -> str:
        """Extract the string previously saved."""
        begin = self.__tags[name]['begin']
        end = self.__tags[name]['end']
        return self._stream[begin:end]

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
        self.push_rule_nodes()
        # create a slot value for the result
        return_node = Node()
        import weakref
        self.rulenodes['_'] = weakref.proxy(return_node)
        if name not in self.__class__._rules:
            error.throw("Unknown rule : %s" % name, self)
        res = self.__class__._rules[name](self)
        if res:
            res = return_node
        self.pop_rule_nodes()
        return res

    def eval_hook(self, name: str, ctx: list) -> Node:
        """Evaluate the hook by its name"""
        if name not in self.__class__._hooks:
            # TODO: don't always throw error, could have return True by default
            error.throw("Unknown hook : %s" % name, self)
        return self.__class__._hooks[name](self, *ctx)

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
            if self._stream.peek_char == inhibitor:
                # Delete inhibitor and inhibited character
                self._stream.incpos()
                self._stream.incpos()
            if self._stream.peek_char == c:
                self._stream.incpos()
                return self._stream.validate_context()
            self._stream.incpos()
        return self._stream.restore_context()

    def read_until_eof(self) -> bool:
        """Consume all the stream. Same as EOF in BNF."""
        if self.read_eof():
            return True
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
            nLength = len(text)
            for _ in range(0, nLength):
                self._stream.incpos()
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
        if not self.read_eof() and self._stream.peek_char in " \t\f\r\n":
            while not self.read_eof() and self._stream.peek_char in " \t\f\r\n":
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
        self._lastIgnoreIndex = self._stream.index
        if len(self._ignores) > 0:
            self._ignores[-1](self)
        self._lastIgnore = (self._stream.index != self._lastIgnoreIndex)
        return True

    def undo_ignore(self) -> bool:
        # TODO(iopi): wrong don't work in all case
        if self._lastIgnore:
            self._stream.decpos(self._stream.index - self._lastIgnoreIndex)
            self._lastIgnoreIndex = self._stream.index
        return True


class Parser(BasicParser):
    """An ascii parsing primitive library."""
    pass

### BASE RULES


@meta.rule(BasicParser, "Base.read_char")
def read_one_char(self) -> bool:
    """Read one byte in stream"""
    if self.read_eof():
        return False
    self._stream.incpos()
    return True


@meta.rule(BasicParser, "Base.eof")
def read_eof(self) -> bool:
    """Returns true if reached end of the stream."""
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


@meta.rule(Parser, "Base.num")
def read_integer(self) -> bool:
    """
    Read following BNF rule else return False
    readInteger ::= ['0'..'9']+ ;
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
    Read following BNF rule else return False
    readIdentifier ::= ['a'..'z'|'A'..'Z'|'_']['0'..'9'|'a'..'z'|'A'..'Z'|'_']* ;
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
    Read following BNF rule else return False
    '"' -> ['/'| '"']
    """
    self._stream.save_context()
    idx = self._stream.index
    if self.read_char('\"') and self.read_until('\"', '\\'):
        txt = self._stream[idx:self._stream.index]
        res = Node(self._stream.validate_context())
        return res
    return self._stream.restore_context()


@meta.rule(Parser, "Base.char")
def read_cchar(self) -> bool:
    # TODO(iopi): octal digit, hex digit
    """
    Read following BNF rule else return False
    "'" -> [~"/" "'"]
    """
    self._stream.save_context()
    idx = self._stream.index
    if self.read_char('\'') and self.read_until('\'', '\\'):
        txt = self._stream[idx:self._stream.index]
        res = Node(self._stream.validate_context())
        return res
    return self._stream.restore_context()
