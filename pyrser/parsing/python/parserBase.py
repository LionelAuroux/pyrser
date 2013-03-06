# Copyright (C) 2012 Candiotti Adrien 
# Copyright (C) 2013 Lionel Auroux
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# 
# See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from pyrser.parsing.python.parserStream import ParserStream
from pyrser.node import Node
from pyrser import meta

class ParserBase(object):
    """
    An ascii parsing primitive library.
    """
    def __init__(self, sStream = ""):
        self.__lStream = [ParserStream(sStream, "root")]
        self.__stackIgnored = [self.ignoreBlanks]
        self.__rules = {}
        self.__hooks = {}
        self._lastIgnoreIndex = 0
        self._skipIgnore = self.__stackIgnored[-1]
        # public
        self.ruleNodes = [{}]
        # decorator rule handling
        if hasattr(ParserBase, 'class_rule_list'):
            for k,v in ParserBase.class_rule_list.items():
                bound_method = v.__get__(self, ParserBase)
                self.setOneRule(k, bound_method)
        # decorator hook handling
        if hasattr(ParserBase, 'class_hook_list'):
            for k,v in ParserBase.class_hook_list.items():
                bound_method = v.__get__(self, ParserBase)
                self.setHooks({k : bound_method})

### PUBLIC ACCESSOR

    def getStream(self) -> str:
        """
        Return current used Stream.
        """
        return self.__lStream[-1]

    def printStream(self, nIndex = 0):
        """
        Print current real stream contained.
        """
        return self.getStream().printStream(nIndex)

### READ ONLY @property

    @property
    def rules(self) -> dict:
        """
        Return the grammar dict
        """
        return self.__rules

    @property
    def streamName(self) -> str:
        """
        Return current Stream name.
        """
        return self.getStream().name

    @property
    def streamLen(self) -> int:
        """
        Return the len of the current stream.
        """
        return self.getStream().contentLen

    @property
    def streamNbr(self) -> int:
        return len(self.__lStream)

    @property
    def columnNbr(self) -> int:
        """
        Return the number of column that was parsed.
        """
        return self.getStream().columnNbr

    @property
    def lineNbr(self) -> int:
        """
        Return the number of line that was parsed.
        """
        return self.getStream().lineNbr

    @property
    def index(self) -> int:
        """
        Return the index value.
        This value is used by the parser to point current byte.
        """
        return self.getStream().index

    @property
    def eofIndex(self) -> int:
        """
        Return the index of the EOF
        """
        return self.getStream().eofIndex

    @property
    def peekChar(self) -> str:
        """
        Test if head byte is equal to c and return true else return false.
        """
        return self.getStream().peekChar

### CONTEXT PRIMITIVES

    def saveContext(self) -> bool:
        """
        Stack the current index position.
        """
        return Node(self.getStream().saveContext())

    def restoreContext(self) -> bool:
        """
        Pop the last index position and set current stream index to this value.
        """
        return Node(self.getStream().restoreContext())

    def validContext(self) -> bool:
        """
        Pop all useless contexts to keep one context only.
        """
        return Node(self.getStream().validContext())

### Rule Nodes

    def pushRuleNodes(self) -> bool:
        """
        Push context variable to store rule nodes
        """
        # outer scope visible in local
        if (len(self.ruleNodes) > 0):
            self.ruleNodes.append(self.ruleNodes[-1].copy())
        return True

    def popRuleNodes(self) -> bool:
        """
        Pop context variable that store rule nodes
        """
        if (len(self.ruleNodes) > 0):
            self.ruleNodes.pop()
        return True

### STREAM

    def parsedStream(self, sNewStream : str, sName = "new"):
        """
        Push a new Stream into the parser.
        All subsequent called functions will parse this new stream,
        until the 'popStream' function is called.
        """
        self.__lStream.append(ParserStream(sNewStream, sName))

    def popStream(self):
        """
        Pop the last Stream pushed on to the parser stack.
        """
        self.__lStream.pop()


    def incPos(self) -> int:
        """
        Increment current index, column and line count.
        Should not be used, or only when sure.
        """
        return self.getStream().incPos()

### VARIABLE PRIMITIVES

# TODO: change for beginTag,endTag,getTag for multicapture, and typesetting at endTag (i.e: readCChar,readCString need transcoding)
    def beginTag(self, sName : str) -> Node:
        """
        Save the current index under the given name.
        """
        return Node(self.getStream().beginTag(sName))

    def endTag(self, sName : str) -> Node:
        """
        Extract the string between the saved index value and the current one.
        """
        return Node(self.getStream().endTag(sName))

    def getTag(self, sName : str) -> str:
        """
        Extract the string previously saved.
        """
        return self.getStream().getTag(sName)

####

    def setRules(self, rules : dict) -> bool:
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
        if namespaces == None:
            namespaces = [rule_name]
        lstname = []
        namespaces.reverse()
        for name in namespaces:
            lstname.insert(0, name)
            strname = "::".join(lstname)
            self.__rules[strname] = callobject
        return True

    def setHooks(self, hook : dict) -> bool:
        """
        Merge internal hooks set with the given hook
        """
        self.__hooks.update(hook)
        return True

    def handleVarCtx(self, res : Node, name : str) -> Node:
        unnsname = name.split("::")[-1]
        # default behavior the returned node is transfered
        # if a ruleNodes have the name $$, it's use for return
        if (res and (unnsname in self.ruleNodes[-1])):
            res = self.ruleNodes[-1][unnsname]
            #print("HANDLE %s: %s" % (unnsname, res))
        return res

    # TODO: define what's could be send globally to all rules
    def evalRule(self, name : str, *args, **kvargs) -> Node:
        """
        Evaluate the rule by its name
        """
        self.pushRuleNodes()
        # create a slot value for the result
        self.ruleNodes[-1][name] = Node()
        res = self.__rules[name](*args, **kvargs)
        res = self.handleVarCtx(res, name)
        self.popRuleNodes()
        return res

    def evalHook(self, name : str, ctx : list) -> Node:
        """
        Evaluate the hook by its name
        """
        # TODO: think of hooks prototype!!!
        res = self.__hooks[name](*ctx)
        return res

### PARSING PRIMITIVES

    def peekText(self, sText) -> bool:
        """
        Same as readText but doesn't consume the stream.
        """
        nLength = len(sText)
        nSubIndex = self.index + nLength
        if nSubIndex > self.getStream().eofIndex:
            return False
        sSubString = self.getStream().getContentAbsolute(self.getStream().index, nSubIndex)
        return sText == sSubString

    def readChar(self, cC : str) -> bool:
        """
        Consume the c head byte, increment current index and return True
        else return False. It use peekchar and it's the same as '' in BNF.
        """
        if self.readEOF():
            return False
        self.saveContext()
        if self.peekChar == cC:
            self.incPos()
            return self.validContext()
        return self.restoreContext()

    # TODO: seems to not working, could be obsolete
    def readAChar(self, cC : str) -> bool:
        """
        Consume a character if possible.
        """
        if self.readEOF():
            return False
        self.saveContext()
        if self.index + 1 < self.eofIndex:
            cC = self.peekChar
            self.incPos()
            return self.validContext()
        return self.restoreContext()

    def readUntil(self, cC : str, cInhibitor = '\\') -> bool:
        """
        Consume the stream while the c byte is not read, else return false
        ex : if stream is " abcdef ", readUntil("d"); consume "abcd".
        """
        if self.readEOF():
            return False
        self.saveContext()
        while not self.readEOF():
            if self.peekChar == cInhibitor:
                self.incPos() # Deletion of the inhibitor.
                self.incPos() # Deletion of the inhibited character.
            if self.peekChar == cC:
                self.incPos()
                return self.validContext()
            self.incPos()
        return self.restoreContext()

    def readUntilEOF(self) -> bool:
        """
        Consume all the stream. Same as EOF in BNF
        """
        if self.readEOF():
            return True
        self.saveContext()
        while self.index != self.eofIndex:
            self.incPos()
        return self.validContext()

    def readText(self, sText : str) -> bool:
        """
        Consume a strlen(text) text at current position in the stream
        else return False.
        Same as "" in BNF
        ex : readText("ls");.
        """
        if self.readEOF():
            return False
        self.saveContext()
        if self.peekText(sText):
            nLength = len(sText)
            for _ in range(0, nLength):
                self.incPos()
            return self.validContext()
        return self.restoreContext()

    def readRange(self, begin : str, end : str) -> int:
        """
        Consume head byte if it is >= begin and <= end else return false
        Same as 'a'..'z' in BNF
        """
        if self.readEOF():
            return False
        self.saveContext()
        cC = self.peekChar
        if cC >= begin and cC <= end:
            self.incPos()
            return self.validContext()
        return self.restoreContext()

### IGNORE CONVENTION

    def ignoreNull(self) -> bool:
        """
        Empty ignore convention for notignore
        """
        return True

    def ignoreBlanks(self) -> bool:
        """
        Consume comments and whitespace characters.
        """
        self.saveContext()
        while not self.readEOF():
            if self.peekChar not in " \t\r\n":
                return self.validContext()
            self.incPos()
        return self.validContext()

    def pushIgnore(self, ignoreConvention) -> bool:
        """
        Set the ignore convention
        """
        self.__stackIgnored.append(ignoreConvention)
        self._skipIgnore = self.__stackIgnored[-1]
        return True

    def popIgnore(self) -> bool:
        """
        Remove the last ignore convention
        """
        self.__stackIgnored.pop()
        self._skipIgnore = self.__stackIgnored[-1]
        return True

    def skipIgnore(self) -> bool:
        self._lastIgnoreIndex = self.index
        self._skipIgnore()
        self._lastIgnore = (self.index != self._lastIgnoreIndex)
        return True

    def undoIgnore(self) -> bool:
        if self._lastIgnore:
            delta = self.index - self._lastIgnoreIndex
            if delta > 0:
                self.getStream().decPosOf(delta)
                self._lastIgnoreIndex = self.index
        return True

### BASE RULES
@meta.rule(ParserBase, "Base::eof")
def readEOF(self) -> bool:
    """
    Returns true if reach end of the stream.
    """
    return self.index == self.eofIndex

@meta.rule(ParserBase, "Base::eol")
def readEOL(self) -> bool:
    """
    Return True if the parser can consume an EOL byte sequence.
    """
    if self.readEOF():
        return False
    self.saveContext()
    self.readChar('\r')
    if self.readChar('\n'):
        return self.validContext()
    return self.restoreContext()

@meta.rule(ParserBase, "Base::num")
def readInteger(self) -> bool:
    """
    Read following BNF rule else return False
    readInteger ::= ['0'..'9']+ ;
    """
    if self.readEOF():
        return False
    self.saveContext()
    cC = self.peekChar
    if cC.isdigit():
            self.incPos()
            while not self.readEOF():
                cC = self.peekChar
                if not cC.isdigit():
                    break
                self.incPos()
            return self.validContext()
    return self.restoreContext()

@meta.rule(ParserBase, "Base::id")
def readIdentifier(self) -> bool:
    """
    Read following BNF rule else return False
    readIdentifier ::= ['a'..'z'|'A'..'Z'|'_']['0'..'9'|'a'..'z'|'A'..'Z'|'_']* ;
    """
    if self.readEOF():
        return False
    self.saveContext()
    cC = self.peekChar
    if (cC.isalpha() or cC == '_'):
            self.incPos()
            while not self.readEOF():
                cC = self.peekChar
                if not (cC.isalpha() or cC.isdigit() or cC == '_'):
                    break
                self.incPos()
            return self.validContext()
    return self.restoreContext()

@meta.rule(ParserBase, "Base::string")
def readCString(self) -> bool:
    """
    Read following BNF rule else return False
    '"' -> ['/'| '"']
    """
    self.saveContext()
    idx = self.index
    if self.readChar('\"') and self.readUntil('\"', '\\'):
        txt = self.getStream().getContentRelative(idx)
        res = Node(self.validContext())
        res.value = txt.strip('"')
        return res
    return self.restoreContext()

@meta.rule(ParserBase, "Base::char")
def readCChar(self) -> bool:
    # TODO: octal digit, hex digit
    """
    Read following BNF rule else return False
    "'" -> [~"/" "'"]
    """
    self.saveContext()
    idx = self.index
    if self.readChar('\'') and self.readUntil('\'', '\\'):
        txt = self.getStream().getContentRelative(idx)
        res = Node(self.validContext())
        res.value = txt.strip("'")
        return res
    return self.restoreContext()

### PARSE TREE

class ParserTree:
    """
    Dummy Base class for all parse tree classes
    """
    def __init__(self):
        pass

class Clauses(ParserTree):
    """
    A B C bnf primitive as a functor
    """
    def __init__(self, parser : ParserBase, *clauses):
        ParserTree.__init__(self)
        self.parser = parser
        self.clauses = clauses
    def __call__(self) -> bool:
        for clause in self.clauses:
            self.parser.skipIgnore()
            if not clause():
                return False
        return True

class Scope(ParserTree):
    """
    functor to wrap SCOPE/rule directive or just []
    """
    def __init__(self, parser : ParserBase, begin : Clauses, end : Clauses, clause : Clauses):
        ParserTree.__init__(self)
        self.parser = parser
        self.begin = begin
        self.end = end
        self.clause = clause
    def __call__(self) -> Node:
        if self.begin():
            self.parser.pushRuleNodes()
            res = self.clause()
            self.parser.popRuleNodes()
            if res and self.end():
                return res
        return False

class Call(ParserTree):
    """Functor to wrap arbitrary call to method of ParserBase in BNF clause."""

    def __init__(self, callObject, *params):
        ParserTree.__init__(self)
        self.callObject = callObject
        self.params = params

    def __call__(self) -> Node:
        return self.callObject(*self.params)


class CallTrue(Call):
    """Functor to wrap arbitrary callable object in BNF clause."""

    def __call__(self) -> Node:
        self.callObject(*self.params)
        return True


class Capture(ParserTree):
    """
    functor to handle capture variables
    """
    def __init__(self, parser : ParserBase, tagname : str, clause : Clauses):
        ParserTree.__init__(self)
        if not isinstance(parser, ParserBase):
            raise Exception("Bad Type For parser as parameter 2")
        self.tagname = tagname
        self.parser = parser
        self.clause = clause
    def __call__(self) -> Node:
        if self.parser.beginTag(self.tagname):
            self.parser.pushRuleNodes()
            self.parser.ruleNodes[-1][self.tagname] = Node()
            res = self.clause()
            self.parser.popRuleNodes()
            if res and self.parser.undoIgnore() and self.parser.endTag(self.tagname):
                text = self.parser.getTag(self.tagname)
                # wrap it in a Node instance
                if type(res) == bool:
                    res = Node(res)
                # TODO: better than a bare copy, just an instance of a future capture object (for multi-stream capture)
                if not hasattr(res, 'value'):
                    res.value = text
                if (len(self.parser.ruleNodes) == 0):
                    raise BaseException("Fuck! No context for rule Nodes")
                #print("Capture %s as %s" % (self.tagname, res))
                self.parser.ruleNodes[-1][self.tagname] = res
                return res
        return False

class Alt(ParserTree):
    """
    A | B bnf primitive as a functor
    """
    def __init__(self, parser : ParserBase, *clauses : Clauses):
        ParserTree.__init__(self)
        self.parser = parser
        self.clauses = clauses
    def __call__(self) -> Node:
        for clause in self.clauses:
            self.parser.saveContext()
            self.parser.skipIgnore()
            res = clause()
            if res:
                self.parser.validContext()
                return res
            self.parser.restoreContext()
        return False

class RepOptional(ParserTree):
    """
    []? bnf primitive as a functor
    """
    def __init__(self, parser : ParserBase, clause : Clauses):
        ParserTree.__init__(self)
        self.parser = parser
        self.clause = clause
    def __call__(self) -> bool:
        self.parser.skipIgnore()
        self.clause()
        return True

class Rep0N(ParserTree):
    """
    []* bnf primitive as a functor
    """
    # TODO: at each turn, pop/push ruleNodes
    def __init__(self, parser : ParserBase, clause : Clauses):
        ParserTree.__init__(self)
        self.parser = parser
        self.clause = clause
    def __call__(self) -> bool:
        self.parser.skipIgnore()
        while self.clause():
            self.parser.skipIgnore()
        return True

class Rep1N(ParserTree):
    """
    []+ bnf primitive as a functor
    """
    # TODO: at each turn, pop/push ruleNodes
    def __init__(self, parser : ParserBase, clause : Clauses):
        ParserTree.__init__(self)
        self.parser = parser
        self.clause = clause
    def __call__(self) -> bool:
        self.parser.skipIgnore()
        if self.clause():
            self.parser.skipIgnore()
            while self.clause():
                self.parser.skipIgnore()
            return True
        return False

class Rule(ParserTree):
    """
    call a rule by his name
    """
    # TODO: Handle additionnal value
    def __init__(self, parser : ParserBase, name : str):
        ParserTree.__init__(self)
        self.parser = parser
        self.name = name
    def __call__(self) -> Node:
        return self.parser.evalRule(self.name)

class Hook(ParserTree):
    """
    call a hook by his name
    """
    def __init__(self, parser : ParserBase, name : str, param : list):
        ParserTree.__init__(self)
        self.parser = parser
        self.name = name
        # compose the list of value param, check type
        self.param = []
        for vt in param:
            v, t = vt
            if type(t) is not type:
                raise Exception("Must be pair of value and type (i.e: int, str, Node)")
            self.param.append(vt)
    def __call__(self) -> bool:
        valueparam = []
        for vt in self.param:
            v, t = vt
            if t is Node:
                import weakref
                valueparam.append(weakref.proxy(self.parser.ruleNodes[-1][v]))
            elif type(v) is t:
                valueparam.append(v)
            else:
                raise Exception("Type mismatch get a %s, expected %s" % (type(v), t))
        return self.parser.evalHook(self.name, valueparam)
