import sys

import rich


def rprint(msg: str) -> None:
    """
    Rich-prints to stderr so that redirection of command output isn't cluttered
    """
    rich.print(msg, file=sys.stderr)
