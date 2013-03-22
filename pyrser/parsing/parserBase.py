from pyrser import meta
from pyrser.parsing.parserStream import Stream
from pyrser.parsing.node import Node


class BasicParser:
    """Emtpy basic parser, contains no rule nor hook.

    Unless you know what you are doing, use Parser instead of this class.

    """
    rules = {}

    def __init__(self, content: str=''):
        self.__hooks = {}
        self.__ignores = [BasicParser.ignore_blanks]
        self.__streams = [Stream(content, 'root')]
        self.__tags = {}
        self._rules = {}
        self.rulenodes = [{}]
        self._lastIgnoreIndex = 0
        self._lastIgnore = False
        # public
        # decorator rule handling
        if hasattr(BasicParser, 'class_rule_list'):
            self.setRules(BasicParser.class_rule_list)
        # decorator hook handling
        if hasattr(BasicParser, 'class_hook_list'):
            self.setHooks(BasicParser.class_hook_list)

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
    def pushRuleNodes(self) -> bool:
        """Push context variable to store rule nodes."""
        # outer scope visible in local
        if (len(self.rulenodes) > 0):
            self.rulenodes.append(self.rulenodes[-1].copy())
        return True

    def popRuleNodes(self) -> bool:
        """Pop context variable that store rule nodes"""
        if len(self.rulenodes) > 0:
            del self.rulenodes[-1]
        return True

### STREAM

    def parsedStream(self, sNewStream: str, sName="new"):
        """Push a new Stream into the parser.

        All subsequent called functions will parse this new stream,
        until the 'popStream' function is called.
        """
        self.__streams.append(Stream(sNewStream, sName))

    def popStream(self):
        """Pop the last Stream pushed on to the parser stack."""
        self.__streams.pop()

### VARIABLE PRIMITIVES

#TODO(iopi): change for beginTag, endTag, getTag for multicapture, and
# typesetting at endTag (i.e: readCChar,readCString need transcoding)
    def beginTag(self, name: str) -> Node:
        """Save the current index under the given name."""
        self.__tags[name] = {'begin': self._stream.index}
        return Node(True)

    def endTag(self, name: str) -> Node:
        """Extract the string between saved and current index."""
        self.__tags[name]['end'] = self._stream.index
        return Node(True)

    def getTag(self, name: str) -> str:
        """Extract the string previously saved."""
        begin = self.__tags[name]['begin']
        end = self.__tags[name]['end']
        return self._stream[begin:end]

####

    def setRules(self, rules: dict) -> bool:
        """
        Merge internal rules set with the given rules
        """
        for rule_name, rule_pt in rules.items():
            self.setOneRule(rule_name, rule_pt)
        return True

    def setOneRule(self, rule_name, callobject) -> bool:
        """
        Add one rule (with namespace handling) that call callobject
        and fix the value of parser in ParserTree
        """
        namespaces = reversed(rule_name.split('.'))
        lstname = []
        for name in namespaces:
            lstname.insert(0, name)
            strname = '.'.join(lstname)
            self._rules[strname] = callobject
        return True

    def setHooks(self, hook: dict) -> bool:
        """
        Merge internal hooks set with the given hook
        """
        self.__hooks.update(hook)
        return True

    def handleVarCtx(self, res: Node, name: str) -> Node:
        unnsname = name.split(".")[-1]
        # default behavior the returned node is transfered
        # if a rulenodes have the name $$, it's use for return
        if res and unnsname in self.rulenodes[-1]:
            res = self.rulenodes[-1][unnsname]
        return res

    #TODO(iopi): define what should be sent globally to all rules
    #TODO(iopi): think about rule proto? global data etc...
    #TODO(bps): Check why evalRule gets args & kwargs but does not use them
    def evalRule(self, name: str, *args, **kwargs) -> Node:
        """Evaluate a rule by name."""
        self.pushRuleNodes()
        # create a slot value for the result
        self.rulenodes[-1][name] = Node()
        res = self._rules[name](self)
        res = self.handleVarCtx(res, name)
        self.popRuleNodes()
        return res

    #TODO(iopi): think about hook prototype!!!
    def evalHook(self, name: str, ctx: list) -> Node:
        """Evaluate a hook by name."""
        return self.__hooks[name](self, *ctx)

### PARSING PRIMITIVES
#TODO(bps): is '''if self.readEOF():''' necessary?

    def peekChar(self, c: str) -> bool:
        if self.readEOF():
            return False
        return self._stream.peek_char == c

    def readChar(self, c: str) -> bool:
        """
        Consume the c head byte, increment current index and return True
        else return False. It use peekchar and it's the same as '' in BNF.
        """
        if self.readEOF():
            return False
        self._stream.save_context()
        if self._stream.peek_char == c:
            self._stream.incpos()
            return self._stream.validate_context()
        return self._stream.restore_context()

    def peekText(self, text: str) -> bool:
        """Same as readText but doesn't consume the stream."""
        stream = self._stream
        start = stream.index
        stop = start + len(text)
        return stream[start:stop] == text

    def readText(self, text: str) -> bool:
        """Consumes a text at current position in the stream if present."""
        if self.readEOF():
            return False
        self._stream.save_context()
        if not self.peekText(text):
            return self._stream.restore_context()
        self._stream.incpos(len(text))
        return self._stream.validate_context()

    def readUntil(self, c: str, cInhibitor='\\') -> bool:
        """
        Consume the stream while the c byte is not read, else return false
        ex : if stream is " abcdef ", readUntil("d"); consume "abcd".
        """
        if self.readEOF():
            return False
        self._stream.save_context()
        while not self.readEOF():
            if self._stream.peek_char == cInhibitor:
                self._stream.incpos()  # Deletion of the inhibitor.
                self._stream.incpos()  # Deletion of the inhibited character.
            if self._stream.peek_char == c:
                self._stream.incpos()
                return self._stream.validate_context()
            self._stream.incpos()
        return self._stream.restore_context()

    def readUntilEOF(self) -> bool:
        """Consume all the stream. Same as EOF in BNF."""
        if self.readEOF():
            return True
        self._stream.save_context()
        while not self.readEOF():
            self._stream.incpos()
        return self._stream.validate_context()

    def readRange(self, begin: str, end: str) -> int:
        """
        Consume head byte if it is >= begin and <= end else return false
        Same as 'a'..'z' in BNF
        """
        if self.readEOF():
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
        while not self.readEOF():
            if self._stream.peek_char not in " \t\r\n":
                return self._stream.validate_context()
            self._stream.incpos()
        return self._stream.validate_context()

    def pushIgnore(self, ignoreConvention) -> bool:
        """Set the ignore convention"""
        self.__ignores.append(ignoreConvention)
        return True

    def popIgnore(self) -> bool:
        """Remove the last ignore convention"""
        self.__ignores.pop()
        return True

    def skipIgnore(self) -> bool:
        self._lastIgnoreIndex = self._stream.index
        self.__ignores[-1](self)
        self._lastIgnore = self._stream.index != self._lastIgnoreIndex
        return True

    def undoIgnore(self) -> bool:
        # TODO(iopi): wrong don't work in all case
        if self._lastIgnore:
            self._stream.decpos(self._stream.index - self._lastIgnoreIndex)
            self._lastIgnoreIndex = self._stream.index
        return True

    def pushIgnore(self, ignoreConvention) -> bool:
        """Set the ignore convention."""
        self.__ignores.append(ignoreConvention)
        return True

    def popIgnore(self) -> bool:
        """Remove the last ignore convention."""
        self.__ignores.pop()
        return True


#TODO(bps): move ignore in parser
class Parser(BasicParser):
    """An ascii parsing primitive library."""
    def __init__(self, *args):
        super().__init__(*args)


### BASE RULES
@meta.rule(BasicParser, "Base.eof")
def readEOF(self) -> bool:
    """Returns true if reached end of the stream."""
    return self._stream.index == self._stream.eos_index


@meta.rule(Parser, "Base.eol")
def readEOL(self) -> bool:
    """Return True if the parser can consume an EOL byte sequence."""
    if self.readEOF():
        return False
    self._stream.save_context()
    self.readChar('\r')
    if self.readChar('\n'):
        return self._stream.validate_context()
    return self._stream.restore_context()


@meta.rule(Parser, "Base.num")
def readInteger(self) -> bool:
    """
    Read following BNF rule else return False
    readInteger ::= ['0'..'9']+ ;
    """
    if self.readEOF():
        return False
    self._stream.save_context()
    c = self._stream.peek_char
    if c.isdigit():
            self._stream.incpos()
            while not self.readEOF():
                c = self._stream.peek_char
                if not c.isdigit():
                    break
                self._stream.incpos()
            return self._stream.validate_context()
    return self._stream.restore_context()


@meta.rule(Parser, "Base.id")
def readIdentifier(self) -> bool:
    """
    Read following BNF rule else return False
    readIdentifier ::= ['a'..'z'|'A'..'Z'|'_']
                       ['0'..'9'|'a'..'z'|'A'..'Z'|'_']* ;
    """
    if self.readEOF():
        return False
    self._stream.save_context()
    c = self._stream.peek_char
    if c.isalpha() or c == '_':
            self._stream.incpos()
            while not self.readEOF():
                c = self._stream.peek_char
                if not (c.isalpha() or c.isdigit() or c == '_'):
                    break
                self._stream.incpos()
            return self._stream.validate_context()
    return self._stream.restore_context()


@meta.rule(Parser, "Base.string")
def readCString(self) -> bool:
    """
    Read following BNF rule else return False
    '"' -> ['/'| '"']
    """
    self._stream.save_context()
    idx = self._stream.index
    if self.readChar('\"') and self.readUntil('\"', '\\'):
        txt = self._stream[idx:self._stream.index]
        res = Node(self._stream.validate_context())
        res.value = txt.strip('"')
        return res
    return self._stream.restore_context()


@meta.rule(Parser, "Base.char")
def readCChar(self) -> bool:
    #TODO(iopi): octal digit, hex digit
    """
    Read following BNF rule else return False
    "'" -> [~"/" "'"]
    """
    self._stream.save_context()
    idx = self._stream.index
    if self.readChar('\'') and self.readUntil('\'', '\\'):
        txt = self._stream[idx:self._stream.index]
        res = Node(self._stream.validate_context())
        res.value = txt.strip("'")
        return res
    return self._stream.restore_context()
