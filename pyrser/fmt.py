## Helping formating classes for to_c

class   indentable:
    """
    base of all fmt objects
    """
    def __init__(self):
        self._indent = 0
        self._lsdata = None

    def __repr__(self):
        txt = str(type(self))
        if len(self._lsdata) > 0:
            txt += '('
            for d in self._lsdata:
                txt += ', ' + repr(d)
            txt += ')'
        return txt

    @property
    def lsdata(self) -> list:
        return self._lsdata

    def set_indent(self, indent :int=0):
        self._indent = indent
        for i in self._lsdata:
            if hasattr(i, 'set_indent'):
                i.set_indent(indent)

    def catend(self, dst :str, src :str) -> str:
        res = dst
        if len(res) > 0 and res[-1] == '\n':
            res += "    " * self._indent
        res += src
        return res

    def dump(self, idx=0) -> str:
        idt = " " * idx
        content = "%sfmt.%s indent level = %d\n" % (idt, type(self), self._indent)
        if self._lsdata != None:
            for i in self._lsdata:
                if hasattr(i, 'dump'):
                    content += i.dump(idx + 1)
                else:
                    content += idt + ' ' + repr(i) + "\n"
        return content

class   block(indentable):
    """
    for {}, (), []
    """
    def __init__(self, beginby :str, endby :str, lsdata :list):
        indentable.__init__(self)
        self._beginby = beginby
        self._endby = endby
        self._lsdata = lsdata

    def __str__(self):
        content = ""
        if self._lsdata != None:
            sz = len(self._lsdata)
            for i in range(sz):
                if hasattr(self._lsdata[i], 'set_indent'):
                    self._lsdata[i].set_indent(self._indent)
                content += str(self._lsdata[i])
        return self._beginby + self.catend(content, self._endby)

class   sep(indentable):
    """
    for all list seperated by a char
    """
    def __init__(self, ch :str, lsdata :list):
        indentable.__init__(self)
        self._ch = ch
        self._lsdata = lsdata

    def __str__(self):
        content = ""
        if self._lsdata != None:
            sz = len(self._lsdata)
            for i in range(sz):
                if hasattr(self._lsdata[i], 'set_indent'):
                    self._lsdata[i].set_indent(self._indent)
                content = self.catend(content, str(self._lsdata[i]))
                if i < sz - 1:
                    content += self._ch
        return content

class   end(indentable):
    """
    for all list that end by a char
    """
    def __init__(self, ch :str, lsdata :list):
        indentable.__init__(self)
        self._ch = ch
        self._lsdata = lsdata

    def __str__(self):
        content = ""
        if self._lsdata != None:
            sz = len(self._lsdata)
            for i in range(sz):
                if hasattr(self._lsdata[i], 'set_indent'):
                    self._lsdata[i].set_indent(self._indent)
                content = self.catend(content, str(self._lsdata[i]))
                content += self._ch
        return content

class   tab(indentable):
    """
    to handle indentation level
    """
    def __init__(self, lsdata :list):
        indentable.__init__(self)
        self._lsdata = lsdata

    def set_indent(self, indent :int=0):
        self._indent = indent + 1
        for i in self._lsdata:
            if hasattr(i, 'set_indent'):
                i.set_indent(self._indent)

    def __str__(self):
        content = ""
        if self._lsdata != None:
            sz = len(self._lsdata)
            for i in range(sz):
                if hasattr(self._lsdata[i], 'set_indent'):
                    self._lsdata[i].set_indent(self._indent)
                if type(self._lsdata[i]) is not tab:
                    content += "    " * self._indent + str(self._lsdata[i])
                else:
                    content += str(self._lsdata[i])
        return content
