class IndentedWriter:
    def __init__(self, indent=4*' '):
        self._indent = indent
        self._cur_indent = 0
        self.lines = []

    def incr(self):
        self._cur_indent += 1

    def decr(self):
        if self._cur_indent > 0:
            self._cur_indent -= 1

    def _add_line(self, l):
        self.lines.append((self._cur_indent * self._indent) + l.rstrip())

    def append(self, s):
        if not isinstance(s, str):
            s = str(s)
        if len(s) == 0:
            self._add_line('')
        else:
            for l in s.splitlines():
                self._add_line(l)

    def __str__(self):
        s = ''
        for line in self.lines:
            s += line + '\n'
        return s