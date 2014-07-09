import collections


"""An immutable position in a Stream.

index is the index in the Stream.
lineno is the line number of the position.
col_offset is the column offset of the position on the line.
"""
Position = collections.namedtuple('Position', 'index lineno col_offset')


class Cursor:
    """A mutable position in a Stream.

    It can be initialized or set from an immutable Position.
    """
    def __init__(self, position: Position=Position(0, 1, 1)):
        self._maxindex = self._index = position.index
        self._maxcol = self._col_offset = position.col_offset
        self._maxline = self._lineno = position.lineno
        self._eol = []

    @property
    def index(self) -> int:
        """The current index of the cursor."""
        return self._index

    @property
    def lineno(self) -> int:
        """The current line number of the cursor."""
        return self._lineno

    @property
    def col_offset(self) -> int:
        """The current column offset of the cursor."""
        return self._col_offset

    @property
    def position(self) -> Position:
        """The current position of the cursor."""
        return Position(self._index, self._lineno, self._col_offset)

    @position.setter
    def position(self, position: Position):
        self._index = position.index
        self._lineno = position.lineno
        self._col_offset = position.col_offset

    @property
    def max_readed_position(self) -> Position:
        """The index of the deepest character readed."""
        return Position(self._maxindex, self._maxline, self._maxcol)

    def step_next_char(self):
        """Puts the cursor on the next character."""
        self._index += 1
        self._col_offset += 1
        if self._index > self._maxindex:
            self._maxindex = self._index
            self._maxcol = self._col_offset
            self._maxline = self._lineno

    def step_prev_char(self):
        """Puts the cursor on the previous character."""
        self._col_offset -= 1
        self._index -= 1

    def step_next_line(self):
        """Sets cursor as beginning of next line."""
        self._eol.append(self.position)
        self._lineno += 1
        self._col_offset = 0

    def step_prev_line(self):
        """Sets cursor as end of previous line."""
        #TODO(bps): raise explicit error for unregistered eol
        #assert self._eol[-1].index == self._index
        if len(self._eol) > 0:
            self.position = self._eol.pop()


class Tag:
    """Provide capture facilities"""
    def __init__(self, stream: str, begin: int, end=0):
        self._stream = stream
        self._begin = begin
        if end == 0:
            self._end = begin
        else:
            self._end = end

    def set_begin(self, begin: int):
        self._begin = begin

    def set_end(self, end: int):
        self._end = end

    def __str__(self) -> str:
        if self._begin == self._end:
            return ""
        return self._stream[self._begin:self._end]

    def __repr__(self) -> str:
        return "strid:%d %s:%s" % (id(self._stream), self._begin, self._end)


class Stream:
    """Helps keep track of stream processing progress."""
    def __init__(self, content: str=None, name: str=None):
        self._content = content
        self._len = len(content)
        self._name = name
        self._contexts = []
        self._cursor = Cursor()
        # use to store begin:end => value
        self.value_cache = dict()

    def __len__(self) -> int:
        return self._len

    def __getitem__(self, key: int or slice) -> str:
        return self._content.__getitem__(key)

    @property
    def name(self) -> int:
        """Name of the stream."""
        return self._name

    @property
    def eos_index(self) -> int:
        """End Of Stream index."""
        return self._len

    @property
    def index(self) -> int:
        """The current position index."""
        return self._cursor.position.index

    @property
    def lineno(self) -> int:
        """The current position line number."""
        return self._cursor.lineno

    @property
    def col_offset(self) -> int:
        """The current position column offset."""
        return self._cursor.col_offset

    @property
    def peek_char(self) -> str:
        """The current position character value."""
        return self._content[self._cursor.index]

    @property
    def last_readed_line(self) -> str:
        """Usefull string to compute error message."""
        mpos = self._cursor.max_readed_position
        mindex = mpos.index
        # search last \n
        prevline = mindex - 1 if mindex == self.eos_index else mindex
        while prevline >= 0 and self._content[prevline] != '\n':
            prevline -= 1
        # search next \n
        nextline = mindex
        while nextline < self.eos_index and self._content[nextline] != '\n':
            nextline += 1
        last_line = self._content[prevline + 1:nextline]
        return last_line

    def incpos(self, length: int=1) -> int:
        """Increment the cursor to the next character."""
        if length < 0:
            raise ValueError("length must be positive")
        i = 0
        while (i < length):
            if self._cursor.index < self._len:
                if self.peek_char == '\n':
                    self._cursor.step_next_line()
                self._cursor.step_next_char()
            i += 1
        return self._cursor.index

    def decpos(self, length: int=1) -> int:
        if length < 0:
            raise ValueError("length must be positive")
        if (self._cursor.index - length) < 0:
            raise ValueError("can't go before first byte")
        i = 0
        while (i < length):
            if self.peek_char == '\n':
                self._cursor.step_prev_line()
                i += 1
            else:
                self._cursor.step_prev_char()
            i += 1
        return self._cursor.index

    def save_context(self) -> bool:
        """Save current position."""
        self._contexts.append(self._cursor.position)
        return True

    def restore_context(self) -> bool:
        """Rollback to previous saved position."""
        self._cursor.position = self._contexts.pop()
        return False

    def validate_context(self) -> bool:
        """Discard previous saved position."""
        del self._contexts[-1]
        return True
