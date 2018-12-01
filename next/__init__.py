#!/usr/bin/env python3
from collections import abc
import compose
import typing as t
from .sliceview import Slice, null, crossection


class Column(Slice):
    __slots__ = ()
    data: t.Sequence[str]

    @property
    def width(self) -> int:
        return max(map(len, self))

    def widthasrow(self, pad="") -> int:
        return sum(len(i) for i in self.data) + (len(self.data) - 1) * len(pad)

    @classmethod
    def new(cls, data, *args, **kwargs):
        if not isinstance(data, t.Sequence):
            data = tuple(data)
        return super().new(data, *args, **kwargs)


class Columns(compose.Struct):
    data: t.Sequence[Column] = compose.Provider(abc.Sequence)

    @classmethod
    def new(cls, iterable: t.Iterable, ncols=1):
        return cls(Column.new(iterable).split(ncols))

    @classmethod
    def fromdict(cls, mapping: t.Mapping, ncols=1):
        iterable = ["{}: {}".format(*i) for i in mapping.items()]
        return cls.new(iterable, ncols)

    @property
    def items(self) -> t.Sequence[str]:
        return self[0].data

    def split(self, ncols=1):
        return self.new(self.items, ncols)

    def chunk(self, chunksize):
        return type(self)(tuple(Column.new(self.items).chunk(chunksize)))

    def getrow(self, index: int, widths):
        for width, item in zip(widths, crossection(self, index)):
            if item is null:
                item = ""
            yield "{:{}}".format(item, width)

    def getrows(self, pad=""):
        widths = [c.width for c in self]
        for i in range(len(self[0])):
            yield pad.join(self.getrow(i, widths)).rstrip()

    def width(self, pad=""):
        return sum(col.width for col in self) + (len(self) - 1) * len(pad)

    def height(self):
        return max(len(item) for item in self)

    def scrunch(self):
        height = self.height()
        bottomrow = [i for i in crossection(self, height - 1) if i is not null]
        freespots = len(self) - len(bottomrow)

        moved = 0
        for i, col in enumerate(reversed(self)):
            moved += len(col)
            if moved > freespots - 1:
                break
            freespots -= len(col)
        columns = self.split(len(self) - i)
        if columns.height() > height:
            columns = columns.split(len(columns) + 1)
        return columns

    def fill(self, width: int, pad: str, grow=True):
        return self._fill(width, pad, len(self), grow)

    def _fill(self, width, pad, ncols, grow=True):
        cw = self.width(pad)
        if cw > width and cw > 1:
            return self.split(ncols - 1).fill(width, pad, False)
        elif cw < width and grow:
            return self.split(ncols + 1).fill(width, pad)
        else:
            return self


def columnate(iterable, width, pad):
    column = Column.new(iterable)
    if column.widthasrow(pad) <= width:
        return (pad.join(column.data),)
    ncols = width // column.width
    if ncols == 0:
        return column.data
    columns = Columns(column.split(ncols)).fill(width, pad).scrunch()
    return columns.getrows(pad)


def center(rows, width):
    rows = tuple(rows)
    maxrow = max(map(len, rows))
    prepad = " " * ((width - maxrow) // 2)
    for row in rows:
        yield prepad + row


class Row(Slice):
    __slots__ = ()
    data: t.Sequence[str]

    @classmethod
    def new(cls, data, *args, **kwargs):
        if not isinstance(data, t.Sequence):
            data = tuple(data)
        return super().new(data, *args, **kwargs)


class Rows(compose.Struct):
    data: t.Sequence[Slice] = compose.Provider(abc.Sequence)
    items = Columns.items
    _fill = Columns._fill

    @classmethod
    def new(cls, iterable, ncols=1):
        return cls(tuple(Row.new(iterable).chunk(ncols)))

    def split(self, ncols=1):
        return self.new(self.items, ncols)

    def getcol(self, idx):
        return (i for i in crossection(self, idx) if i is not null)

    def getcols(self):
        return [self.getcol(i) for i in range(len(self[0]))]

    def colwidth(self, idx):
        return max(len(i) for i in self.getcol(idx))

    def colwidths(self):
        return [self.colwidth(i) for i in range(len(self[0]))]

    def getrows(self, pad=""):
        widths = self.colwidths()
        for row in self:
            yield pad.join(
                "{:{}}".format(name, width) for name, width in zip(row, widths)
            ).rstrip()

    def height(self):
        return len(tuple(crossection(self, 0)))

    def width(self, pad=""):
        widths = self.colwidths()
        return sum(widths) + len(pad) * (len(widths) - 1)

    def fill(self, width: int, pad: str, grow=True):
        return self._fill(width, pad, len(self[0]), grow)

    def scrunch(self):
        height = self.height()
        freespots = len(self[0]) - len(self[-1])

        moved = 0
        for i, col in enumerate(reversed(self.getcols())):
            col = tuple(col)
            moved += len(col)
            if moved > freespots - 1:
                break
            freespots -= len(col)
        rows = self.split(len(self[0]) - i)
        if rows.height() > height:
            rows = rows.split(len(rows[0]) + 1)
        return rows

    
def nicerows(iterable, width, pad):
    rows = Rows.new(iterable)
    ncols = width // max(len(item) for item in rows.items)
    if ncols == 0:
        return rows.items
    rows = rows.split().fill(width, pad).scrunch()
    return rows.getrows(pad)
