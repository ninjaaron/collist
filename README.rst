collist
=======
``collist`` is a simple module with only one primary function:
``collist()``, the single purpose of which is to columnate lists of
output for priting to the terminal. It is very much like the unix
command ``column``, but it works on python iterables. This package also
exports the command ``cols`` which is similar to ``column``, but with
fewer features and works better (on my system), though it has fewer
options; see ``cols --help``.

The program uses the ``tput`` command interally, and therefore only
works with POSIX.
