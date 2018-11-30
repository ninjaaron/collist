#!/usr/bin/env python3
from collections import abc
import compose
import os
import sys
import typing as t


class Slice(compose.Struct):
    data: t.Sequence
    start: int
    stop: int

    @classmethod
    def new(cls, data, start=0, stop=None):
        if stop is None:
            stop = len(data)
        return cls(data, start, stop)

    def absidx(self, index: int):
        if index >= 0:
            return self.start + index
        else:
            return self.stop + index

    def boundscheck(self, index: int):
        idx = self.absidx(index)
        if idx >= self.stop or idx < self.start:
            raise IndexError("Index out of bounds")
        return idx

    def __getitem__(self, index: t.Union[slice, int]):
        if isinstance(index, int):
            return self.data[self.boundscheck(index)]
        else:
            if index.start is None:
                start = self.start
            else:
                start = self.boundscheck(index.start)

            if index.stop is None:
                stop = self.stop
            else:
                stop = self.boundscheck(index.stop - 1) + 1
            return type(self)(self.data, start, stop)

    def __len__(self):
        return self.stop - self.start

    def cut(self, index: int) -> t.Tuple["Slice", "Slice"]:
        return self[:index], self[index:]

    def chunk(self, chunksize: int):
        end = self
        while True:
            try:
                start, end = end.cut(chunksize)
                yield start
            except IndexError:
                yield end
                break

    def split(self, numitems: int = 2) -> t.List["Slice"]:
        new = []
        chunksize, remainder = divmod(len(self), numitems)
        end = self
        for i in range(remainder):
            start, end = end.cut(chunksize + 1)
            new.append(start)
        new.extend(end.chunk(chunksize))
        return new

    def __repr__(self):
        name = type(self).__name__
        copy = self.data[self.start : self.stop]
        return "{}<{!r}>".format(name, copy)

    def __iter__(self):
        for i in range(self.start, self.stop):
            yield self.data[i]


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


null = object()


def crossection(matrix: t.Sequence[t.Sequence], index: int):
    for sequence in matrix:
        try:
            yield sequence[index]
        except IndexError:
            yield null


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
        return type(self)(list(Column.new(self.items).chunk(chunksize)))

    def getrow(self, index: int, widths):
        for width, item in zip(widths, crossection(self, index)):
            if item is null:
                return
            yield "{:{}}".format(item, width)

    def getrows(self, pad=""):
        widths = [c.width for c in self]
        for i in range(len(self[0])):
            yield pad.join(self.getrow(i, widths)).rstrip()

    def width(self, pad=""):
        return sum(col.width for col in self) + (len(self) - 1) * len(pad)

    def height(self):
        return len(self[0])

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
        cw = self.width(pad)
        ncols = len(self)
        if cw > width and cw > 1:
            return self.split(ncols - 1).fill(width, pad, False)
        elif cw < width and grow:
            return self.split(ncols + 1).fill(width, pad)
        else:
            return self


def fill(iterable, width, pad):
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


def main():
    pad = "  "
    twidth, _ = os.get_terminal_size()
    rows = fill(sys.stdin.read().splitlines(), twidth, pad)
    print(*rows, sep="\n")


if __name__ == "__main__":
    main()
