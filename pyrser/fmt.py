## Helping formating classes for to_c

class   indentable:
    """
    base of all fmt objects
    """
    char_indent = " "
    num_indent = 4

    def __init__(self):
        self._indent = 0
        self._is_indented = False
        self._lsdata = None

    def to_str(self, res: str) -> str:
        pass

    def __str__(self):
        self.set_indent()
        strinit = (self.char_indent * self.num_indent) * (self._indent - 1)
        return self.to_str(strinit, self._indent)

    def __repr__(self):
        txt = str(type(self))
        if hasattr(self, '_beginby'):
            txt += repr(self._beginby)
        if hasattr(self, '_endby'):
            txt += repr(self._endby)
        if hasattr(self, '_ch'):
            txt += repr(self._ch)
        if self._lsdata != None and len(self._lsdata) > 0:
            txt += '(\n'
            for d in self._lsdata:
                txt += '     ' + repr(d) + "\n"
            txt += ')\n'
        return txt

    @property
    def lsdata(self) -> list:
        return self._lsdata

    def set_indent(self, indent: int=1):
        if self._is_indented:
            return
        self._indent = indent
        if isinstance(self._lsdata, indentable):
            self._lsdata.set_indent(self._indent)
        if isinstance(self._lsdata, list):
            for i in self._lsdata:
                if isinstance(i, self.__class__):
                    if not i._is_indented:
                        i.set_indent(indent)
        self._is_indented = True
    
    # copy char by char and handle \n for tabulation!!!
    def catend(self, dst :str, src :str, _indent) -> str:
        res = dst
        for c in list(src):
            if len(res) > 0 and res[-1] == '\n':
                res += (self.char_indent * self.num_indent) * (_indent - 1) + c
            else:
                res += c
        return res

class   block(indentable):
    """
    for {}, (), []
    """
    def __init__(self, beginby :str, endby :str, lsdata :list):
        indentable.__init__(self)
        self._beginby = beginby
        self._endby = endby
        if lsdata == None:
            raise Exception("lsdata can't be None")
        self._lsdata = lsdata


    def to_str(self, res: str, parent_indent) -> str:
        self.set_indent()
        content = self.catend(res, self._beginby, parent_indent)
        if isinstance(self._lsdata, indentable):
            return self.catend(self._lsdata.to_str(content, self._indent), self._endby, parent_indent)
        if isinstance(self._lsdata, list):
            for i in self._lsdata:
                if isinstance(i, indentable):
                    # FIX 
                    content = i.to_str(content, self._indent)
                else:
                    content = self.catend(content, i, self._indent)
        return self.catend(content, self._endby, parent_indent)

class   sep(indentable):
    """
    for all list seperated by a char
    """
    def __init__(self, ch :str, lsdata :list):
        indentable.__init__(self)
        self._ch = ch
        if lsdata == None:
            raise Exception("lsdata can't be None")
        self._lsdata = lsdata

    def to_str(self, res: str, parent_indent) -> str:
        self.set_indent()
        content = res
        if isinstance(self._lsdata, indentable):
            return self._lsdata.to_str(res, self._indent)
        if isinstance(self._lsdata, list):
            sz = len(self._lsdata)
            for i in range(sz):
                if isinstance(self._lsdata[i], indentable):
                    content = self._lsdata[i].to_str(content, self._indent)
                else:
                    content = self.catend(content, self._lsdata[i], self._indent)
                if i < sz - 1:
                    content = self.catend(content, self._ch, self._indent)
        return content

class   end(indentable):
    """
    for all list that end by a char
    """
    def __init__(self, ch :str, lsdata :list):
        indentable.__init__(self)
        self._ch = ch
        if lsdata == None:
            raise Exception("lsdata can't be None")
        self._lsdata = lsdata

    def to_str(self, res: str, parent_indent) -> str:
        self.set_indent()
        content = res
        if isinstance(self._lsdata, indentable):
            return self.catend(self._lsdata.to_str(res, self._indent), self._ch, self._indent)
        if isinstance(self._lsdata, list):
            for i in self._lsdata:
                if isinstance(i, indentable):
                    content = i.to_str(content, self._indent)
                else:
                    content = self.catend(content, i, self._indent)
                content = self.catend(content, self._ch, self._indent)
        return content

class   tab(indentable):
    """
    to handle indentation level
    """
    def __init__(self, lsdata: indentable):
        indentable.__init__(self)
        if lsdata == None:
            raise Exception("lsdata can't be None")
        self._lsdata = lsdata

    def set_indent(self, indent: int=1):
        if self._is_indented:
            return
        self._indent = indent + 1
        if isinstance(self._lsdata, indentable):
            self._lsdata.set_indent(self._indent)
        if isinstance(self._lsdata, list):
            for i in self._lsdata:
                if isinstance(i, indentable):
                    i.set_indent(self._indent)
        self._is_indented = True

    def to_str(self, res: str, parent_indent) -> str:
        self.set_indent()
        if isinstance(self._lsdata, indentable):
            return self._lsdata.to_str(res, self._indent)
        if isinstance(self._lsdata, list):
            content = res
            for i in self._lsdata:
                if isinstance(i, indentable):
                    content = i.to_str(content, self._indent)
                else:
                    content = self.catend(content, i, self._indent)
        return content
