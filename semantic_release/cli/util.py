"""
Utilities for command-line functionality
"""
import sys
from textwrap import dedent, indent

import rich


def rprint(msg: str) -> None:
    """
    Rich-prints to stderr so that redirection of command output isn't cluttered
    """
    rich.print(msg, file=sys.stderr)


def noop_report(msg: str) -> None:
    """
    Rich-prints a msg with a standard prefix to report when an action is not being
    taken due to a "noop" flag
    """
    fullmsg = "[bold cyan]:shield: semantic-release 'noop' mode is enabled! " + msg
    rprint(fullmsg)


def indented(msg: str, prefix: str = " " * 4) -> str:
    """
    Convenience function for text-formatting for the console.

    Ensures the least indented line of the msg string is indented by ``prefix`` with
    consistent alignment of the remainder of ``msg`` irrespective of the level of
    indentation in the Python source code
    """
    return indent(dedent(msg), prefix=prefix)
