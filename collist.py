import subprocess as sp
import click

def collist(strlist, divider='  ', cols=0):
    '''
    takes a list of strings and prints it as a list of columns that fit the
    terminal width (or a specified number of columns, with the `cols`
    parameter.
    '''
    strlist = [s.rstrip() for s in strlist]
    width = int(sp.check_output(['tput', 'cols']))
    longest = 0
    for string in strlist:
        if len(string) > longest:
            longest = len(string)
    tabs = longest
    totalcols = cols if cols else width // (tabs + len(divider))
    if totalcols > len(strlist):
        totalcols = len(strlist)
    split, remainder = divmod(len(strlist),  totalcols)
    if remainder != 0:
        split += 1
    cols = [strlist[n*split:(n+1)*split] for n in range(totalcols)]
    while len(cols[0]) > len(cols[-1]):
        cols[-1].append('')
    table = ''
    for row, head in enumerate(cols[0]):
        for n, col in enumerate(cols):
            if n == 0:
                table += u'\n{0:{1}}'.format(head, tabs)
            else:
                try:
                    table += u'{0}{1:{2}}'.format(divider, col[row], tabs)
                except IndexError:
                    pass
    table = '\n'.join(table.splitlines()[1:])
    print(table.expandtabs(tabs + len(divider)))


@click.command()
@click.option('-n', default=0, help='number of columns')
@click.option('-d', default='  ',
        help='column seperator. defaults to two spaces')
@click.argument('filename', required=False)
def main(filename, n, d):
    '''columnate lines from a file or stdin'''
    import sys
    f = open(filename) if filename else sys.stdin
    lines = f.readlines()
    if isinstance(lines[0], bytes):
        lines = [l.decode('UTF-8') for l in lines]
    collist(lines, divider=d, cols=n)
