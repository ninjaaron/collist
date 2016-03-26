import sys
import subprocess as sp
try:
    import builtins
except ImportError:
    pass
import collections
import click


def displayhook(value):
    if value is None:
       return
    # Set '_' to None to avoid recursion
    try:
        builtins._ = None
    except:
        pass
    if isinstance(value, (list, dict, set, tuple)):
        try:
           text = collist(value, representation=True)
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


def collist(iterable, divider='  ', cols=0, representation=False):
    '''
    takes a list of strings and prints it as a list of columns that fit the
    terminal width (or a specified number of columns, with the `cols`
    parameter). Each column is divided with the string sepcified in the
    `divider` parameter (which defaults to two spaces). If `representation` is
    true, `divider` is ignored, and the list is returned as a python
    representation.
    '''
    strlist = iterable
    if representation:
        divider = ' '
        if isinstance(strlist, dict):
            strlist = [u'{}: {}'.format(repr(k), repr(v)) + u','
                       for k, v in strlist.items()]
            divchar = u'{}'
        else:
            strlist = [s.__repr__() + u',' for s in strlist]
            divchar = u'[]' if isinstance(strlist ,list) else u'()'
            divchar = u'{}' if isinstance(strlist, set) else divchar
    else:
        if isinstance(strlist, dict):
            strlist = [u'{}: {}'.format(k, v) for k, v in strlist.items()]
        strlist = [str(s).rstrip() for s in strlist]
    if len(strlist) == 0:
        click.echo('no items', err=True)
        exit(1)
    width = int(sp.check_output(['tput', 'cols']))
    width = width - 1 if representation else width
    longest = 0
    for string in strlist:
        if len(string) > longest:
            longest = len(string)
    tabs = longest
    totalcols = cols if cols else width // (tabs + len(divider))
    if totalcols > len(strlist):
        return repr(iterable) if representation else divider.join(iterable)
    split, remainder = divmod(len(strlist),  totalcols)
    if remainder != 0:
        split += 1
    if not representation:
        cols = [strlist[n*split:(n+1)*split] for n in range(totalcols)]
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
    else:
        rows = [strlist[n*totalcols:(n+1)*totalcols] for n in range(split)]
        table = []
        for row in rows:
            row = u''.join([u'{0}{1:{2}}'.format(divider, i, tabs)
                           for i in row]).lstrip()
            table.append(row)
        table[0] = divchar[0] + table[0]
        table[1:] = [u' ' + r for r in table[1:]]
        table[-1] = table[-1].rstrip()[:-1] + divchar[1]
        table = u'\n'.join(table)
    return table


@click.command()
@click.option('-n', default=0, help='number of columns')
@click.option('-d', default='  ',
        help='column seperator. defaults to two spaces')
@click.argument('filename', type=click.File('r'), default='-')
def main(filename, n, d):
    '''columnate lines from a file or stdin'''
    lines = filename.readlines()
    if isinstance(lines[0], bytes):
        lines = [l.decode('UTF-8') for l in lines]
    click.echo(collist(lines, divider=d, cols=n))
