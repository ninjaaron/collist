import compose
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


null = object()


def crossection(matrix: t.Sequence[t.Sequence], index: int):
    for sequence in matrix:
        try:
            yield sequence[index]
        except IndexError:
            yield null
