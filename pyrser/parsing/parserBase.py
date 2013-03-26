import collections

from pyrser import meta
from pyrser.parsing.parserStream import Stream
from pyrser.parsing.node import Node


class MetaBasicParser(type):
    """Metaclass for all parser."""
    def __new__(metacls, name, bases, namespace):
        # TODO: add auto namespacing!!!
        cls = type.__new__(metacls, name, bases, namespace)
        # create rules mapping in the class from inheritance
        cls._rules = collections.ChainMap()
        for base in reversed(bases):
            if (hasattr(base, '_rules') and
                    isinstance(base._rules, collections.ChainMap)):
                cls._rules = base._rules.new_child()
        # create hooks mapping in the class from inheritance
        cls._hooks = collections.ChainMap()
        for base in reversed(bases):
            if (hasattr(base, '_hooks') and
                    isinstance(base._hooks, collections.ChainMap)):
                cls._hooks = base._hooks.new_child()
        # create directives mapping in the class from inheritance
        cls._directives = collections.ChainMap()
        for base in reversed(bases):
            if (hasattr(base, '_directives') and
                    isinstance(base._directives, collections.ChainMap)):
                cls._directives = base._directives.new_child()
        return cls


class BasicParser(metaclass=MetaBasicParser):
    """Emtpy basic parser, contains no rule nor hook.

    Unless you know what you are doing, use Parser instead of this class.

    """
    def __init__(self, content: str=''):
        self._ignores = [BasicParser.ignore_blanks]
        self.__streams = [Stream(content, "root")]
        self.__tags = {}
        self.rulenodes = [{}]
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
        # outer scope visible in local
        if (len(self.rulenodes) > 0):
            self.rulenodes.append(self.rulenodes[-1].copy())
        return True

    def pop_rule_nodes(self) -> bool:
        """Pop context variable that store rule nodes"""
        if len(self.rulenodes) > 0:
            del self.rulenodes[-1]
        return True

### STREAM

    def parsed_stream(self, sNewStream: str, sName="new"):
        """Push a new Stream into the parser.
        All subsequent called functions will parse this new stream,
        until the 'popStream' function is called.
        """
        self.__streams.append(Stream(sNewStream, sName))

    def pop_stream(self):
        """Pop the last Stream pushed on to the parser stack."""
        self.__streams.pop()

### VARIABLE PRIMITIVES

#TODO(iopi): change beginTag, endTag, and getTag for multicapture,
#            and typesetting at endTag (i.e: readCChar, readCString need
#            transcoding)
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
            cls.set_one(cls._rules, rule_name, rule_pt)
        return True

    @classmethod
    def set_hooks(cls, hooks: dict) -> bool:
        """
        Merge internal hooks set with the given hooks
        """
        cls._hooks = cls._hooks.new_child()
        for hook_name, hook_pt in hooks.items():
            cls.set_one(cls._hooks, hook_name, hook_pt)
        return True

    @classmethod
    def set_directives(cls, directives: dict) -> bool:
        """
        Merge internal directives set with the given directives.
        For working directives, attach it only in the dsl.Parser class
        """
        cls._directives = cls._directives.new_child()
        for dir_name, dir_pt in directives.items():
            cls.set_one(cls._directives, dir_name, dir_pt)
        return True

    @classmethod
    def set_one(cls, chainmap, thing_name, callobject):
        """Add a mapping with key thing_name for callobject in chainmap with
           namespace handling.
        """
        namespaces = reversed(thing_name.split("."))
        if namespaces is None:
            namespaces = [thing_name]
        lstname = []
        for name in namespaces:
            lstname.insert(0, name)
            strname = '.'.join(lstname)
            chainmap[strname] = callobject

    def handle_var_ctx(self, res: Node, name: str) -> Node:
        unnsname = name.split(".")[-1]
        # default behavior the returned node is transfered
        # if a rulenodes have the name $$, it's use for return
        if res and unnsname in self.rulenodes[-1]:
            res = self.rulenodes[-1][unnsname]
        return res

    #TODO(iopi): define what should be sent globally to all rules
    #TODO(iopi): think about rule proto? global data etc...
    #TODO(bps): Check why eval_rule gets args & kwargs but does not use them
    def eval_rule(self, name: str, *args, **kwargs) -> Node:
        """Evaluate a rule by name."""
        self.push_rule_nodes()
        # create a slot value for the result
        self.rulenodes[-1][name] = Node()
        #TODO(iopi): think about rule proto? global data etc...
        res = self.__class__._rules[name](self)
        res = self.handle_var_ctx(res, name)
        self.pop_rule_nodes()
        return res

    def eval_hook(self, name: str, ctx: list) -> Node:
        """Evaluate the hook by its name"""
        # TODO: think of hooks prototype!!!
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
        if self._stream.peek_char == c:
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
        """Consume comments and whitespace characters."""
        self._stream.save_context()
        while not self.read_eof():
            if self._stream.peek_char not in " \t\r\n":
                return self._stream.validate_context()
            self._stream.incpos()
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
    def __init__(self, *args):
        super().__init__(*args)

### BASE RULES


@meta.rule(BasicParser, "Base.eof")
def read_eof(self) -> bool:
    """Returns true if reached end of the stream."""
    return self._stream.index == self._stream.eos_index


@meta.rule(Parser, "Base.eol")
def read_eol(self) -> bool:
    """Return True if the parser can consume an EOL byte sequence."""
    if self.read_eol():
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


@meta.rule(Parser, "Base.id")
def read_identifier(self) -> bool:
    """
    Read following BNF rule else return False
    readIdentifier ::= ['a'..'z'|'A'..'Z'|'_']
                       ['0'..'9'|'a'..'z'|'A'..'Z'|'_']* ;
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
        res.value = txt.strip('"')
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
        res.value = txt.strip("'")
        return res
    return self._stream.restore_context()
