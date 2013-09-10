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
        self.__maxindex = self.__index = position.index
        self.__maxcol = self.__col_offset = position.col_offset
        self.__maxline = self.__lineno = position.lineno
        self.__eol = []

    @property
    def index(self) -> int:
        """The current index of the cursor."""
        return self.__index

    @property
    def lineno(self) -> int:
        """The current line number of the cursor."""
        return self.__lineno

    @property
    def col_offset(self) -> int:
        """The current column offset of the cursor."""
        return self.__col_offset

    @property
    def position(self) -> Position:
        """The current position of the cursor."""
        return Position(self.__index, self.__lineno, self.__col_offset)

    @position.setter
    def position(self, position: Position):
        self.__index = position.index
        self.__lineno = position.lineno
        self.__col_offset = position.col_offset

    @property
    def max_readed_position(self) -> Position:
        """The index of the deepest character readed."""
        return Position(self.__maxindex, self.__maxline, self.__maxcol)

    def step_next_char(self):
        """Puts the cursor on the next character."""
        self.__index += 1
        self.__col_offset += 1
        if self.__index > self.__maxindex:
            self.__maxindex = self.__index
            self.__maxcol = self.__col_offset
            self.__maxline = self.__lineno

    def step_prev_char(self):
        """Puts the cursor on the previous character."""
        self.__col_offset -= 1
        self.__index -= 1

    def step_next_line(self):
        """Sets cursor as begin of next line."""
        self.__eol.append(self.position)
        self.__lineno += 1
        self.__col_offset = 0

    def step_prev_line(self):
        """Sets cursor as end of previous line."""
        #TODO(bps): raise explicit error for unregistered eol
        assert self.__eol[-1].index == self.__index
        self.position = self.__eol.pop()


class Stream:
    """Helps keep track of stream processing progress."""
    def __init__(self, content='', name='stream'):
        self.__content = content
        self.__len = len(content)
        self.__name = name
        self._contexts = []
        self._cursor = Cursor()

    def __len__(self) -> int:
        return self.__len

    def __getitem__(self, key: int or slice) -> str:
        return self.__content.__getitem__(key)

    @property
    def name(self) -> int:
        """Name of the stream."""
        return self.__name

    @property
    def eos_index(self) -> int:
        """End Of Stream index."""
        return self.__len

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
        return self.__content[self._cursor.index]

    @property
    def last_readed_line(self) -> str:
        """Usefull string to compute error message."""
        mpos = self._cursor.max_readed_position
        mindex = mpos.index
        # search last \n
        prevline = mindex - 1 if mindex == self.eos_index else mindex
        while prevline >= 0 and self.__content[prevline] != '\n':
            prevline -= 1
        # search next \n
        nextline = mindex
        while nextline < self.eos_index and self.__content[nextline] != '\n':
            nextline += 1
        last_line = self.__content[prevline + 1:nextline]
        return last_line

    def incpos(self, length: int=1) -> int:
        """Increment the cursor to the next character."""
        if length <= 0:
            raise ValueError("length must be positive")
        for _ in range(length):
            if self._cursor.index < self.__len:
                if self.peek_char == '\n':
                    self._cursor.step_next_line()
                self._cursor.step_next_char()
        return self._cursor.index

    def decpos(self, length: int=1) -> int:
        if length <= 0:
            raise ValueError("length must be positive")
        for _ in range(length):
            if 0 < self._cursor.index:
                self._cursor.step_prev_char()
                if self.peek_char == '\n':
                    self._cursor.step_prev_line()
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
