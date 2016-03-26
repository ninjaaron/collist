collist
=======
``collist`` is a simple module with only one primary function:
``collist()``, the single purpose of which is to columnate lists of
output for printing to the terminal. It is very much like the unix
command ``column``, but it works on python iterables. This package also
exports the command ``cols`` which is similar to ``column``, but with
fewer features and works better (on my system), though it has fewer
options; see ``cols --help``.

The program uses the ``tput`` command internally, and therefore only
works with POSIX.

Monkey Patch `collist` into the Python Interactive Prompt
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The Python interactive prompt print the representation of the return
value of any expression you give it.  If that return value is a list,
dictionary, or tuple, It returns the literal that will produce the
object.

When these collection objects get rather longer, printing them sucks.
``collist`` is designed to make lists of things look better. ``collist``
has a ``representation`` parameter that can be set to ``True``, and it
will output a nicely columnated repr of a python dictionary, list or
tuple. This repr is a valid python literal.

In order to get this behavior in the standard interactive prompt or
bpython, add this to your ~/.pystart:

.. code:: python

    import sys # if you haven't already.
    from collist import displayhook

    sys.displayhook = displayhook

Then, you'll get nicely columnated list, tuples and dictionaries back in
the interactive prompt.

.. code:: python
  >>> [i for i in ('foo bar bing ' * 15).split()]
  ['foo',  'bar',  'bing', 'foo',  'bar',  'bing', 'foo',  'bar',
   'bing', 'foo',  'bar',  'bing', 'foo',  'bar',  'bing', 'foo',
   'bar',  'bing', 'foo',  'bar',  'bing', 'foo',  'bar',  'bing',
   'foo',  'bar',  'bing', 'foo',  'bar',  'bing', 'foo',  'bar',
   'bing', 'foo',  'bar',  'bing', 'foo',  'bar',  'bing', 'foo',
   'bar',  'bing', 'foo',  'bar',  'bing']

Nice! This is what the people want. There is a bug at the moment where
the terminal size is stuck at whatever it was when the interactive
prompt was started. I assume this has something to do with ``tput``
getting the terminal size from sterr, but I'm not really sure. If
anyone has a fix, I will be glad to have a patch.

.. vim: tw=72
