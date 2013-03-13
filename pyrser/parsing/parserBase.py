from pyrser.parsing.parserStream import Stream
from pyrser import meta
from pyrser import node


class BasicParser:
    """Emtpy basic parser, contains no rule nor hook.

    Unless you know what you are doing, use Parser instead of this class.
    """
    rules = {}

    def __init__(self, content: str=''):
        self.__hooks = {}
        self.__ignores = [self.ignoreBlanks]
        self.__streams = [Stream(content, 'root')]
        self.__tags = {}
        self._rules = {}
        self.rulenodes = [{}]
        # Basic rules handling
        self._lastIgnoreIndex = 0
        # public
        # decorator rule handling
        if hasattr(BasicParser, 'class_rule_list'):
            self.setRules(BasicParser.class_rule_list)
        # decorator hook handling
        if hasattr(BasicParser, 'class_hook_list'):
            self.setHooks(BasicParser.class_hook_list)

    @property
    def _stream(self) -> Stream:
        """The current Stream."""
        return self.__streams[-1]

### Rule Nodes

    def pushRuleNodes(self) -> bool:
        """
        Push context variable to store rule nodes
        """
        # outer scope visible in local
        if (len(self.rulenodes) > 0):
            self.rulenodes.append(self.rulenodes[-1].copy())
        return True

    def popRuleNodes(self) -> bool:
        """Pop context variable that store rule nodes."""
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
    def beginTag(self, name: str) -> node.Node:
        """Save the current index under the given name."""
        self.__tags[name] = {'index': self._stream.index}
        return node.Node(True)

    def endTag(self, name: str) -> node.Node:
        """Extract the string between saved and current index."""
        tag = self.__tags[name]
        start = tag['index']
        tag['value'] = self._stream[start:self._stream.index]
        return node.Node(True)

    def getTag(self, name: str) -> str:
        """Extract the string previously saved."""
        return self.__tags[name]['value']

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
        """
        namespaces = rule_name.split("::")
        if namespaces is None:
            namespaces = [rule_name]
        lstname = []
        namespaces.reverse()
        for name in namespaces:
            lstname.insert(0, name)
            strname = "::".join(lstname)
            self._rules[strname] = callobject
        return True

    def setHooks(self, hook: dict) -> bool:
        """
        Merge internal hooks set with the given hook
        """
        self.__hooks.update(hook)
        return True

    def handleVarCtx(self, res: node.Node, name: str) -> node.Node:
        unnsname = name.split("::")[-1]
        # default behavior the returned node is transfered
        # if a rulenodes have the name $$, it's use for return
        if res and unnsname in self.rulenodes[-1]:
            res = self.rulenodes[-1][unnsname]
        return res

    #TODO(iopi): define what's could be send globally to all rules
    def evalRule(self, name: str, *args, **kwargs) -> node.Node:
        """Evaluate a rule by name."""
        if name not in self._rules:
            raise Exception("No rule named {}".format(name))
        self.pushRuleNodes()
        # create a slot value for the result
        self.rulenodes[-1][name] = node.Node()
        res = self._rules[name](self, *args, **kwargs)
        res = self.handleVarCtx(res, name)
        self.popRuleNodes()
        return res

    #TODO(iopi): think about hook prototypes!!!
    def evalHook(self, name: str, ctx: list) -> node.Node:
        """Evaluate a hook by name."""
        res = self.__hooks[name](self, *ctx)
        return res

### PARSING PRIMITIVES

    def peekText(self, text: str) -> bool:
        """Same as readText but doesn't consume the stream."""
        stream = self._stream
        start = stream.index
        stop = start + len(text)
        if stop > stream.eos_index:
            return False
        return stream[stream.index:stop] == text

    def readChar(self, cC: str) -> bool:
        """
        Consume the c head byte, increment current index and return True
        else return False. It use peekchar and it's the same as '' in BNF.
        """
        if self.readEOF():
            return False
        self._stream.save_context()
        if self._stream.peek_char == cC:
            self._stream.incpos()
            return self._stream.validate_context()
        return self._stream.restore_context()

    #TODO(iopi): seems not to work, could be obsolete
    def readAChar(self, cC: str) -> bool:
        """
        Consume a character if possible.
        """
        if self.readEOF():
            return False
        self._stream.save_context()
        if self._stream.index + 1 < self.eos_index:
            cC = self._stream.peek_char
            self._stream.incpos()
            return self._stream.validate_context()
        return self._stream.restore_context()

    def readUntil(self, cC: str, cInhibitor='\\') -> bool:
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
            if self._stream.peek_char == cC:
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

    def readText(self, sText: str) -> bool:
        """
        Consume a strlen(text) text at current position in the stream
        else return False.
        Same as "" in BNF
        ex : readText("ls");.
        """
        if self.readEOF():
            return False
        self._stream.save_context()
        if self.peekText(sText):
            nLength = len(sText)
            for _ in range(0, nLength):
                self._stream.incpos()
            return self._stream.validate_context()
        return self._stream.restore_context()

#    def readInteger(self) -> bool:
#        """
#        Read following BNF rule else return False
#        readInteger ::= ['0'..'9']+ ;
#        """
#        if self.readEOF():
#            return False
#        self._stream.save_context()
#        cC = self._stream.peek_char
#        if cC.isdigit():
#                self._stream.incpos()
#                while not self.readEOF():
#                    cC = self._stream.peek_char
#                    if not cC.isdigit():
#                        break
#                    self._stream.incpos()
#                return self._stream.validate_context()
#        return self._stream.restore_context()
#
#    def readIdentifier(self) -> bool:
#        """
#        Read following BNF rule else return False
#        readIdentifier ::= ['a'..'z'|'A'..'Z'|'_']
#                           ['0'..'9'|'a'..'z'|'A'..'Z'|'_']* ;
#        """
#        if self.readEOF():
#            return False
#        self._stream.save_context()
#        cC = self._stream.peek_char
#        if (cC.isalpha() or cC == '_'):
#                self._stream.incpos()
#                while not self.readEOF():
#                    cC = self._stream.peek_char
#                    if not (cC.isalpha() or cC.isdigit() or cC == '_'):
#                        break
#                    self._stream.incpos()
#                return self._stream.validate_context()
#        return self._stream.restore_context()

    def readRange(self, begin: str, end: str) -> int:
        """
        Consume head byte if it is >= begin and <= end else return false
        Same as 'a'..'z' in BNF
        """
        if self.readEOF():
            return False
        self._stream.save_context()
        cC = self._stream.peek_char
        if cC >= begin and cC <= end:
            self._stream.incpos()
            return self._stream.validate_context()
        return self._stream.restore_context()

#    def readCString(self) -> bool:
#        """
#        Read following BNF rule else return False
#        '"' -> ['/'| '"']
#        """
#        self._stream.save_context()
#        if self.readChar('\"') and self.readUntil('\"', '\\'):
#            return self._stream.validate_context()
#        return self._stream.restore_context()
#
#    def readCChar(self) -> bool:
#        #TODO(iopi): octal digit, hex digit
#        """
#        Read following BNF rule else return False
#        "'" -> [~"/" "'"]
#        """
#        self._stream.save_context()
#        if self.readChar('\'') and self.readUntil('\'', '\\'):
#            return self._stream.validate_context()
#        return self._stream.restore_context()

### IGNORE CONVENTION

    def ignoreNull(self) -> bool:
        """
        Empty ignore convention for notignore
        """
        return True

    def ignoreBlanks(self) -> bool:
        """Consume comments and whitespace characters."""
        self._stream.save_context()
        while not self.readEOF():
            if self._stream.peek_char not in " \t\r\n":
                return self._stream.validate_context()
            self._stream.incpos()
        return self._stream.validate_context()

    def skipIgnore(self):
        self._lastIgnoreIndex = self._stream.index
        self.__ignores[-1]()
        self._lastIgnore = self._stream.index != self._lastIgnoreIndex
        return True

    def undoIgnore(self) -> bool:
        if self._lastIgnore:
            delta = self._stream.index - self._lastIgnoreIndex
            if delta > 0:
                self._stream.decpos(delta)
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


class Parser(BasicParser):
    """An ascii parsing primitive library."""
    def __init__(self, *args):
        super().__init__(*args)
        self.setOneRule("Base::num", self.readInteger.__func__)
        self.setOneRule("Base::id", self.readIdentifier.__func__)
        self.setOneRule("Base::char", self.readCChar.__func__)
        self.setOneRule("Base::string", self.readCString.__func__)
        self.setOneRule("Base::eof", self.readEOF.__func__)
        self.setOneRule("Base::eol", self.readEOL.__func__)


### BASE RULES
@meta.rule(Parser, "Base::eof")
def readEOF(self) -> bool:
    """Returns true if reach end of the stream."""
    return self._stream.index == self._stream.eos_index


@meta.rule(Parser, "Base::eol")
def readEOL(self) -> bool:
    """Return True if the parser can consume an EOL byte sequence."""
    if self.readEOF():
        return False
    self._stream.save_context()
    self.readChar('\r')
    if self.readChar('\n'):
        return self._stream.validate_context()
    return self._stream.restore_context()


@meta.rule(Parser, "Base::num")
def readInteger(self) -> bool:
    """
    Read following BNF rule else return False
    readInteger ::= ['0'..'9']+ ;
    """
    if self.readEOF():
        return False
    self._stream.save_context()
    cC = self._stream.peek_char
    if cC.isdigit():
            self._stream.incpos()
            while not self.readEOF():
                cC = self._stream.peek_char
                if not cC.isdigit():
                    break
                self._stream.incpos()
            return self._stream.validate_context()
    return self._stream.restore_context()


@meta.rule(Parser, "Base::id")
def readIdentifier(self) -> bool:
    """
    Read following BNF rule else return False
    readIdentifier ::= ['a'..'z'|'A'..'Z'|'_']
                       ['0'..'9'|'a'..'z'|'A'..'Z'|'_']* ;
    """
    if self.readEOF():
        return False
    self._stream.save_context()
    cC = self._stream.peek_char
    if cC.isalpha() or cC == '_':
            self._stream.incpos()
            while not self.readEOF():
                cC = self._stream.peek_char
                if not (cC.isalpha() or cC.isdigit() or cC == '_'):
                    break
                self._stream.incpos()
            return self._stream.validate_context()
    return self._stream.restore_context()


@meta.rule(Parser, "Base::string")
def readCString(self) -> bool:
    """
    Read following BNF rule else return False
    '"' -> ['/'| '"']
    """
    self._stream.save_context()
    idx = self._stream.index
    if self.readChar('\"') and self.readUntil('\"', '\\'):
        txt = self._stream[idx:self._stream.index]
        res = node.Node(self._stream.validate_context())
        res.value = txt.strip('"')
        return res
    return self._stream.restore_context()


@meta.rule(Parser, "Base::char")
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
        res = node.Node(self._stream.validate_context())
        res.value = txt.strip("'")
        return res
    return self._stream.restore_context()


### PARSE TREE
class ParserTree:
    """Dummy Base class for all parse tree classes."""

    def __init__(self):
        pass


def is_inlinable(callable_):
    if hasattr(callable_, 'inline'):
        return callable_.inline
    if callable(callable_):
        return True
    return False


class Clauses(ParserTree):
    """A B C bnf primitive as a functor."""

    def __init__(self, *clauses):
        ParserTree.__init__(self)
        if len(clauses) == 0:
            raise TypeError()
        self.clauses = clauses

    def __call__(self, parser: BasicParser) -> bool:
        for clause in self.clauses:
            parser.skipIgnore()
            if not clause(parser):
                return False
        return True


class Scope(ParserTree):
    """functor to wrap SCOPE/rule directive or just []."""

    def __init__(self, begin: Clauses, end: Clauses, clause: Clauses):
        ParserTree.__init__(self)
        self.begin = begin
        self.end = end
        self.clause = clause

    def __call__(self, parser: BasicParser) -> node.Node:
        if self.begin(parser):
            parser.pushRuleNodes()
            res = self.clause(parser)
            parser.popRuleNodes()
            if res and self.end(parser):
                return res
        return False


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

    def __call__(self, parser: BasicParser) -> node.Node:
        return self.callObject(parser, *self.params)


class CallTrue(Call):
    """Functor to wrap arbitrary callable object in BNF clause."""

    def __call__(self) -> node.Node:
        self.callObject(*self.params)
        return True


class Capture(ParserTree):
    """functor to handle capture variables."""

    def __init__(self, tagname: str, clause: ParserTree):
        ParserTree.__init__(self)
        if not isinstance(tagname, str) or len(tagname) == 0:
            raise TypeError()
        self.tagname = tagname
        self.clause = clause

    def __call__(self, parser: BasicParser) -> node.Node:
        if parser.beginTag(self.tagname):
            parser.pushRuleNodes()
            parser.rulenodes[-1][self.tagname] = node.Node()
            res = self.clause(parser)
            parser.popRuleNodes()
            if (res and
                    parser.undoIgnore() and
                    parser.endTag(self.tagname)):
                text = parser.getTag(self.tagname)
                # wrap it in a Node instance
                if type(res) == bool:
                    res = node.Node(res)
                #TODO(iopi): should be a future capture object for multistream
                # capture
                if not hasattr(res, 'value'):
                    res.value = text
                if (len(parser.rulenodes) == 0):
                    raise BaseException("Fuck! No context for rule Nodes")
                parser.rulenodes[-1][self.tagname] = res
                return res
        return False


class Alt(ParserTree):
    """A | B bnf primitive as a functor."""

    def __init__(self, *clauses: Clauses):
        ParserTree.__init__(self)
        self.clauses = clauses

    def __call__(self, parser: BasicParser) -> node.Node:
        for clause in self.clauses:
            parser._stream.save_context()
            parser.skipIgnore()
            res = clause(parser)
            if res:
                parser._stream.validate_context()
                return res
            parser._stream.restore_context()
        return False


class RepOptional(ParserTree):
    """[]? bnf primitive as a functor."""
    def __init__(self, clause: Clauses):
        ParserTree.__init__(self)
        self.clause = clause

    def __call__(self, parser: BasicParser) -> bool:
        parser.skipIgnore()
        self.clause(parser)
        return True


class Rep0N(ParserTree):
    """[]* bnf primitive as a functor."""

    #TODO(iopi): at each turn, pop/push rulenodes
    def __init__(self, clause: Clauses):
        ParserTree.__init__(self)
        self.clause = clause

    def __call__(self, parser: BasicParser) -> bool:
        parser.skipIgnore()
        while self.clause(parser):
            parser.skipIgnore()
        return True


class Rep1N(ParserTree):
    """[]+ bnf primitive as a functor."""

    #TODO(iopi): at each turn, pop/push rulenodes
    def __init__(self, clause: Clauses):
        ParserTree.__init__(self)
        self.clause = clause

    def __call__(self, parser: BasicParser) -> bool:
        parser.skipIgnore()
        if self.clause(parser):
            parser.skipIgnore()
            while self.clause(parser):
                parser.skipIgnore()
            return True
        return False


class Rule(ParserTree):
    """Call a rule by its name."""

    #TODO(iopi): Handle additionnal value
    def __init__(self, name: str):
        ParserTree.__init__(self)
        self.name = name

    def __call__(self, parser: BasicParser) -> node.Node:
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
            if t is node.Node:
                import weakref
                valueparam.append(weakref.proxy(parser.rulenodes[-1][v]))
            elif type(v) is t:
                valueparam.append(v)
            else:
                raise TypeError("Type mismatch expected {} got {}".format(
                    t, type(v)))
        return parser.evalHook(self.name, valueparam)
