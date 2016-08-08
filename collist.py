#!/usr/bin/env python3
# coding = UTF-8
import sys
import subprocess as sp
import pprint
from functools import reduce
try:
    import builtins
except ImportError:
    pass
import collections
import click
try:
    from pyedpiper import Stream
except ImportError:
    class Stream:
        pass


def displayhook(value):
    if value is None or repr(value) == 'None':
       return
    # Set '_' to None to avoid recursion
    try:
        builtins._ = None
    except:
        pass
    if isinstance(value, Stream):
        value = value.state
    if isinstance(value, (list, dict, set, tuple)):
        try:
           text = representation(value)
        except ZeroDivisionError:
            text = repr(value)
    else:
        text = repr(value)
    try:
        sys.stdout.write(text)
    except UnicodeEncodeError:
        bytes = text.encode(sys.stdout.encoding, 'backslashreplace')
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout.buffer.write(bytes)
        else:
            text = bytes.decode(sys.stdout.encoding, 'strict')
            sys.stdout.write(text)
    sys.stdout.write("\n")
    try:
        builtins._ = value
    except:
        pass


def _get_table_size(strlist, divider=u' ', cols=0):
    width = int(sp.check_output(['tput', 'cols']))
    tabs = reduce(lambda x, y: x if x > y else y, map(len, strlist), 0)
    totalcols = cols if cols else width // (tabs + len(divider))
    if not totalcols:
        totalcols = 1
    col_len, remainder = divmod(len(strlist), totalcols)
    if remainder != 0:
        col_len += 1
    return width, totalcols, col_len, tabs


def collist(iterable, divider=u'  ', cols=0):
    '''
    takes a list of strings and prints it as a list of columns that fit the
    terminal width (or a specified number of columns, with the `cols`
    parameter). Each column is divided with the string sepcified in the
    `divider` parameter (which defaults to two spaces).
    '''
    strlist = iterable
    if isinstance(strlist, dict):
        strlist = (u'{}: {}'.format(k, v) for k, v in strlist.items())
    strlist = [str(s).rstrip() for s in strlist]
    width, totalcols, col_len, tabs = _get_table_size(strlist, divider, cols)
    if totalcols == 1:
        return '\n'.join(strlist)
    if not cols:
        short_list = divider.join(strlist)
        if len(short_list) <= width:
            return short_list

    cols = [strlist[n*col_len:(n+1)*col_len] for n in range(totalcols)]
    while len(cols[0]) > len(cols[-1]):
        cols[-1].append(u'')
    table = u''
    for row, head in enumerate(cols[0]):
        for n, col in enumerate(cols):
            if n == 0:
                table += u'\n{0:{1}}'.format(head, tabs)
            else:
                try:
                    table += u'{0}{1:{2}}'.format(divider, col[row], tabs)
                except IndexError:
                    pass
    table = u'\n'.join(table.splitlines()[1:])
    return table


def representation(iterable):
    '''print a columnated representation of a python literal. falls back to
    pprint.pformat values at the top level are too long for the terminal.
    '''
    cols = 0
    if isinstance(iterable, dict):
        strlist = [u'{}: {}'.format(repr(k), repr(v)) + u','
                   for k, v in iterable.items()]
        divchar = u'{}'
    else:
        strlist = [s.__repr__() + u',' for s in iterable]
        divchar = u'[]' if isinstance(iterable, list) else u'()'
        divchar = u'{}' if isinstance(iterable, set) else divchar
    try:
        width, totalcols, col_len, tabs = _get_table_size(strlist)
    except TypeError:
        return divchar
    if len(repr(iterable)) <= width:
        return repr(iterable)
    elif totalcols == 1:
        return pprint.pformat(iterable)
    width = width - 1
    rows = [strlist[n*totalcols:(n+1)*totalcols] for n in range(col_len)]
    table = []
    for row in rows:
        row = u''.join([u' {0:{1}}'.format(i, tabs)
                       for i in row]).lstrip()
        table.append(row)
    table[0] = divchar[0] + table[0]
    table[1:] = [u' ' + r for r in table[1:]]
    table[-1] = table[-1].rstrip()[:-1] + divchar[1]
    table = u'\n'.join(table)
    return table


@click.command()
@click.option('-c', default=0, help='number of columns')
@click.option('-d', default='  ',
        help='column seperator. defaults to two spaces')
@click.argument('filename', type=click.File('r'), default='-')
def main(filename, c, d):
    '''columnate lines from a file or stdin'''
    lines = filename.readlines()
    click.echo(collist(lines, divider=d, cols=c))

if __name__ == '__main__':
    main()
