## Helping class for pretty printing


class indentable:
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
            list_set_indent(self._lsdata, self._indent)
        self._is_indented = True


def catend(dst: str, src: str, indent) -> str:
    """cat two strings but handle \n for tabulation"""
    res = dst
    txtsrc = src
    if not isinstance(src, str):
        txtsrc = str(src)
    for c in list(txtsrc):
        if len(res) > 0 and res[-1] == '\n':
            res += (indentable.char_indent * indentable.num_indent) * \
                   (indent - 1) + c
        else:
            res += c
    return res


def list_set_indent(lst: list, indent: int=1):
    """recurs into list for indentation"""
    for i in lst:
        if isinstance(i, indentable):
            i.set_indent(indent)
        if isinstance(i, list):
            list_set_indent(i, indent)


def list_to_str(lst: list, content: str, indent: int=1):
    """recurs into list for string computing """
    for i in lst:
        if isinstance(i, indentable):
            content = i.to_str(content, indent)
        elif isinstance(i, list):
            content = list_to_str(i, content, indent)
        elif isinstance(i, str):
            content = catend(content, i, indent)
    return content


class block(indentable):
    """
    for {}, (), []
    """
    def __init__(self, beginby: str, endby: str, lsdata: list):
        indentable.__init__(self)
        self._beginby = beginby
        self._endby = endby
        if lsdata is None:
            raise Exception("lsdata can't be None")
        self._lsdata = lsdata

    def to_str(self, res: str, parent_indent) -> str:
        self.set_indent()
        content = catend(res, self._beginby, parent_indent)
        if isinstance(self._lsdata, indentable):
            return catend(self._lsdata.to_str(content, self._indent),
                          self._endby, parent_indent)
        if isinstance(self._lsdata, list):
            content = list_to_str(self._lsdata, content, self._indent)
        return catend(content, self._endby, parent_indent)


class sep(indentable):
    """
    for all list seperated by a char
    """
    def __init__(self, ch: str, lsdata: list):
        indentable.__init__(self)
        self._ch = ch
        if lsdata is None:
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
                elif isinstance(self._lsdata[i], list):
                    content = list_to_str(self._lsdata[i], content,
                                          self._indent)
                else:
                    content = catend(content, self._lsdata[i], self._indent)
                if i < sz - 1:
                    content = catend(content, self._ch, self._indent)
        return content


class end(indentable):
    """
    for all list that end by a char
    """
    def __init__(self, ch: str, lsdata: list):
        indentable.__init__(self)
        self._ch = ch
        if lsdata is None:
            raise Exception("lsdata can't be None")
        self._lsdata = lsdata

    def to_str(self, res: str, parent_indent) -> str:
        self.set_indent()
        content = res
        if isinstance(self._lsdata, indentable):
            return catend(self._lsdata.to_str(res, self._indent), self._ch,
                          self._indent)
        if isinstance(self._lsdata, list):
            for i in self._lsdata:
                if isinstance(i, indentable):
                    content = i.to_str(content, self._indent)
                elif isinstance(i, list):
                    content = list_to_str(i, content, self._indent)
                else:
                    content = catend(content, i, self._indent)
                content = catend(content, self._ch, self._indent)
        return content


class tab(indentable):
    """
    to handle indentation level
    """
    def __init__(self, lsdata: indentable):
        indentable.__init__(self)
        if lsdata is None:
            raise Exception("lsdata can't be None")
        self._lsdata = lsdata

    def set_indent(self, indent: int=1):
        if self._is_indented:
            return
        self._indent = indent + 1
        if isinstance(self._lsdata, indentable):
            self._lsdata.set_indent(self._indent)
        if isinstance(self._lsdata, list):
            list_set_indent(self._lsdata, self._indent)
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
                elif isinstance(i, list):
                    content = list_to_str(i, content, self._indent)
                else:
                    content = catend(content, i, self._indent)
        return content
