from pyrser import meta
from pyrser.parsing.parserStream import Stream
from pyrser.parsing.node import Node
import weakref

class BasicParser(object):
    """Emtpy basic parser, contains no rule nor hook.

    Unless you know what you are doing, use Parser instead of this class.

    """
    rules = {}

    def __init__(self, content: str=''):
        self.__hooks = {}
        self._ignores = [BasicParser.ignore_blanks]
        self.__streams = [Stream(content, "root")]
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
        if (len(self.rulenodes) > 0):
            del self.rulenodes[-1]
        return True

### STREAM

    def parsedStream(self, sNewStream : str, sName="new"):
        """Push a new Stream into the parser.
        All subsequent called functions will parse this new stream,
        until the 'popStream' function is called.
        """
        self.__streams.append(Stream(sNewStream, sName))

    def popStream(self):
        """Pop the last Stream pushed on to the parser stack."""
        self.__streams.pop()

### VARIABLE PRIMITIVES

# TODO: change for beginTag,endTag,getTag for multicapture, and typesetting at endTag (i.e: readCChar,readCString need transcoding)
    def beginTag(self, name: str) -> Node:
        """        Save the current index under the given name.
        """
        self.__tags[name] = {'begin' : self._stream.index}
        return Node(True)

    def endTag(self, name: str) -> Node:
        """Extract the string between the saved index value and the current one."""
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
        namespaces = rule_name.split(".")
        if namespaces is None:
            namespaces = [rule_name]
        lstname = []
        namespaces.reverse()
        for name in namespaces:
            lstname.insert(0, name)
            strname = ".".join(lstname)
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
        if (res and (unnsname in self.rulenodes[-1])):
            res = self.rulenodes[-1][unnsname]
            #print("HANDLE %s: %s" % (unnsname, res))
        return res

    # TODO: define what's could be send globally to all rules
    def evalRule(self, name : str, *args, **kvargs) -> Node:
        """
        Evaluate the rule by its name
        """
        self.pushRuleNodes()
        # create a slot value for the result
        #print("VAL RULE!!!! %s" % name)
        self.rulenodes[-1][name] = Node()
        #print("NEW STACK0 %r" % self.rulenodes[0])
        #print("NEW STACK1 %r" % self.rulenodes[1])
        res = self._rules[name](self) # TODO: think about rule proto? global data etc...
        res = self.handleVarCtx(res, name)
        #print("POP IN EVAL RULE")
        self.popRuleNodes()
        return res

    def evalHook(self, name: str, ctx: list) -> Node:
        """Evaluate the hook by its name"""
        # TODO: think of hooks prototype!!!
        return self.__hooks[name](self, *ctx)

### PARSING PRIMITIVES

    def peekText(self, text: str) -> bool:
        """Same as readText but doesn't consume the stream."""
        start = self._stream.index
        stop = start + len(text)
        if stop > self._stream.eos_index:
            return False
        return self._stream[self._stream.index:stop] == text

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
                self._stream.incpos() # Deletion of the inhibitor.
                self._stream.incpos() # Deletion of the inhibited character.
            if self._stream.peek_char == cC:
                self._stream.incpos()
                return self._stream.validate_context()
            self._stream.incpos()
        return self._stream.restore_context()

    def readUntilEOF(self) -> bool:
        """
        Consume all the stream. Same as EOF in BNF
        """
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
        ii = self._stream.index
        self._stream.save_context()
        if self.peekText(sText):
            nLength = len(sText)
            for _ in range(0, nLength):
                self._stream.incpos()
            iii = self._stream.index
            print("READ %s %s %s" % (sText, ii, iii))
            return self._stream.validate_context()
        return self._stream.restore_context()

    def readRange(self, begin: str, end: str) -> int:
        """
        Consume head byte if it is >= begin and <= end else return false
        Same as 'a'..'z' in BNF
        """
        if self.readEOF():
            return False
        c = self._stream.peek_char
        if c >= begin and c <= end:
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
        self._ignores.append(ignoreConvention)
        return True

    def popIgnore(self) -> bool:
        """Remove the last ignore convention"""
        self._ignores.pop()
        return True

    def skipIgnore(self) -> bool:
        self._lastIgnoreIndex = self._stream.index
        self._ignores[-1](self)
        self._lastIgnore = (self._stream.index != self._lastIgnoreIndex)
        return True

    def undoIgnore(self) -> bool:
        print("testvar %s testexpr %s" % (self._lastIgnore, self._stream.index != self._lastIgnoreIndex))
        if self._lastIgnore:
            self._stream.decpos(self._stream.index - self._lastIgnoreIndex)
            self._lastIgnoreIndex = self._stream.index
        return True

class Parser(BasicParser):
    """An ascii parsing primitive library."""
    def __init__(self, *args):
        super().__init__(*args)

### BASE RULES
@meta.rule(Parser, "Base.eof")
def readEOF(self) -> bool:
    """Returns true if reach end of the stream."""
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

@meta.rule(Parser, "Base.id")
def readIdentifier(self) -> bool:
    """
    Read following BNF rule else return False
    readIdentifier ::=  ['a'..'z'|'A'..'Z'|'_']
                        ['0'..'9'|'a'..'z'|'A'..'Z'|'_']* ;
    """
    if self.readEOF():
        return False
    self._stream.save_context()
    ii = self._stream.index
    cC = self._stream.peek_char
    if (cC.isalpha() or cC == '_'):
            self._stream.incpos()
            while not self.readEOF():
                cC = self._stream.peek_char
                if not (cC.isalpha() or cC.isdigit() or cC == '_'):
                    break
                self._stream.incpos()
            iii = self._stream.index
            print("grep id %s endid %s" % (self._stream[ii:iii], iii))
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
    # TODO: octal digit, hex digit
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

### PARSE TREE

class ParserTree:
    """Dummy Base class for all parse tree classes
    
    common property:
        pt if contain a ParserTree
        ptlist if contain a list of ParserTree
    """
    def __init__(self):
        pass

class Seq(ParserTree):
    """A B C bnf primitive as a functor"""

    def __init__(self, *ptlist: ParserTree):
        ParserTree.__init__(self)
        if len(ptlist) == 0:
            raise TypeError("Expected Seq")
        self.ptlist = ptlist

    def __call__(self, parser: BasicParser) -> bool:
        for pt in self.ptlist:
            parser.skipIgnore()
            if not pt(parser):
                return False
        return True

class Alt(ParserTree):
    """A | B bnf primitive as a functor."""

    def __init__(self, *ptlist: ParserTree):
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

class Scope(ParserTree):
    """functor to wrap SCOPE/rule directive or just []"""

    def __init__(self, begin: Seq, end: Seq, pt: ParserTree):
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
    """functor to handle capture variables."""
    def __init__(self, tagname: str, pt: ParserTree):
        ParserTree.__init__(self)
        if not isinstance(tagname, str) or len(tagname) == 0:
            raise TypeError("Bad type for tagname")
        self.tagname = tagname
        self.pt = pt

    def __call__(self, parser: BasicParser) -> Node:
        if parser.beginTag(self.tagname):
            parser.rulenodes[-1][self.tagname] = Node()
            res = self.pt(parser)
            print("apresCLAUSE: %d" % parser._stream.index)
            if (res and 
                    #parser.undoIgnore() and
                    parser.endTag(self.tagname)):
                text = parser.getTag(self.tagname)
                # wrap it in a Node instance
                if type(res) is bool:
                    res = Node(res)
                #TODO(iopi): should be a future capture object for multistream
                if not hasattr(res, 'value'):
                    res.value = text
                if (len(parser.rulenodes) == 0):
                    raise BaseException("Fuck! No context for rule Nodes")
                print("Capture %s as %s" % (self.tagname, res))
                parser.rulenodes[-1][self.tagname] = res
                return res
        return False

class RepOptional(ParserTree):
    """[]? bnf primitive as a functor"""

    def __init__(self, pt: ParserTree):
        ParserTree.__init__(self)
        self.pt = pt
    def __call__(self, parser: BasicParser) -> bool:
        parser.skipIgnore()
        self.pt(parser)
        return True

class Rep0N(ParserTree):
    """[]* bnf primitive as a functor"""

    # TODO: at each turn, pop/push rulenodes
    def __init__(self, pt: ParserTree):
        ParserTree.__init__(self)
        self.pt = pt

    def __call__(self, parser: BasicParser) -> bool:
        parser.skipIgnore()
        while self.pt(parser):
            parser.skipIgnore()
        return True

class Rep1N(ParserTree):
    """[]+ bnf primitive as a functor"""

    # TODO: at each turn, pop/push rulenodes
    def __init__(self, pt: ParserTree):
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
    """call a rule by his name"""

    # TODO: Handle additionnal value
    def __init__(self, name: str):
        ParserTree.__init__(self)
        self.name = name

    def __call__(self, parser: BasicParser) -> Node:
        return parser.evalRule(self.name)

class Hook(ParserTree):
    """call a hook by his name"""

    def __init__(self, name: str, param: [(object, type)]):
        ParserTree.__init__(self)
        #self.parser = copy.copy(parser)
        self.name = name
        # compose the list of value param, check type
        for v, t in param:
            if type(t) is not type:
                raise TypeError("Must be pair of value and type (i.e: int, str, Node)")
        self.param = param

    def __call__(self, parser: BasicParser) -> bool:
        #print("PARSER OBJECT %s" % parser)
        #print("ALL STACK %r" % parser.rulenodes)
        valueparam = []
        for v, t in self.param:
            if t is Node:
                valueparam.append(weakref.proxy(parser.rulenodes[-1][v]))
            elif type(v) is t:
                valueparam.append(v)
            else:
                raise TypeError("Type mismatch expected {} got {}".format(t, type(v)))
        return parser.evalHook(self.name, valueparam)
