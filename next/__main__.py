import os
import sys
from .__init__ import columnate, nicerows


def main():
    pad = "  "
    twidth, _ = os.get_terminal_size()
    # rows = columnate(sys.stdin.read().splitlines(), twidth, pad)
    rows = nicerows(sys.stdin.read().splitlines(), twidth, pad)
    print(*rows, sep="\n")


if __name__ == "__main__":
    main()
