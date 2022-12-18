import sys

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
