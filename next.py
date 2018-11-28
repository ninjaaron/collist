#!/usr/bin/env python3
from collections import abc
import compose
import os
import sys
import typing as t


class SliceView(compose.Struct):
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

    def cut(self, index: int) -> t.Tuple["SliceView", "SliceView"]:
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

    def split(self, numitems=2):
        chunksize, remainder = divmod(len(self), numitems)
        end = self
        for i in range(remainder):
            start, end = end.cut(chunksize + 1)
            yield start
        yield from end.chunk(chunksize)

    def __repr__(self):
        return "{}<{!r}>".format(type(self).__name__, self.data[self.start : self.stop])

    def __iter__(self):
        for i in range(self.start, self.stop):
            yield self.data[i]


class Column(SliceView):
    __slots__ = ()
    data: t.Sequence[str]

    @property
    def width(self) -> int:
        return max(map(len, self))


null = object()


def crossection(matrix: t.Iterable[t.Iterable], index: int):
    for array in matrix:
        try:
            yield array[index]
        except IndexError:
            yield null


class Columns(compose.Struct):
    data: t.Sequence[Column] = compose.Provider(abc.Sequence)

    @classmethod
    def new(cls, iterable: t.Iterable, ncols=1):
        if not isinstance(iterable, t.Sequence):
            iterable = list(iterable)
        cols = Column.new(iterable).split(ncols)
        return cls(list(cols))

    @classmethod
    def fromdict(cls, mapping: t.Mapping, ncols=1):
        iterable = ["{}: {}".format(*i) for i in mapping.items()]
        return cls.new(iterable, ncols)

    @property
    def items(self):
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
            yield pad.join(self.getrow(i, widths))

    def width(self, pad=""):
        return sum(col.width for col in self) + (len(self) - 1) * len(pad)

    def height(self):
        return len(self[0])

    def fitwidth(self, width, pad):
        # see if it fits on one line
        onerow = self.chunk(1)
        if onerow.width(pad) < width:
            return onerow.getrows(pad)
        del onerow
        colwidth = self.width()
        ncols = width // colwidth

        # see if an extra column can fit
        ncols += 1
        columns = self.split(ncols)
        while columns.width(pad) > width:
            ncols -= 1
            columns = columns.split(ncols)

        # see if we can scrunch the columns without making the table longer
        columns = scrunch(columns)
        return columns.getrows(pad)


def scrunch(columns):
    height = columns.height()
    bottomrow = [i for i in crossection(columns, height - 1) if i is not null]
    freespots = len(columns) - len(bottomrow)

    moved = 0
    for i, col in enumerate(reversed(columns)):
        moved += len(col)
        if moved > freespots - 1:
            break
        freespots -= len(col)
    columns = columns.split(len(columns) - i)
    if columns.height() > height:
        columns = columns.split(len(columns) + 1)
    return columns


def main():
    pad = "  "
    columns = Columns.new(sys.stdin.read().splitlines())
    twidth, _ = os.get_terminal_size()
    print(*columns.fitwidth(twidth, pad), sep="\n")


if __name__ == "__main__":
    main()
