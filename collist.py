#!/usr/bin/env python3

from __future__ import unicode_literals
import subprocess as sp

def collist(strlist, divider='  ', cols=None):
    '''
    takes a list of strings and prints it as a list of columns that fit the
    terminal width
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
                table += '\n{0:{1}}'.format(head, tabs)
            else:
                try:
                    table += '{0}{1:{2}}'.format(divider, col[row], tabs)
                except IndexError:
                    pass
    table = '\n'.join(table.splitlines()[1:])
    print(table.expandtabs(tabs + len(divider)))


def main():
    import sys
    f = open(sys.argv[1]) if sys.argv[1:2] else sys.stdin
    lines = f.readlines()
    if isinstance(lines[0], bytes):
        lines = [l.decode('UTF-8') for l in lines]
    collist(lines)
