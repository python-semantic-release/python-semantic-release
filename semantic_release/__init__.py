"""Semantic Release
"""
__version__ = "7.32.1"


from .errors import UnknownCommitMessageStyleError  # noqa; noqa
from .errors import ImproperConfigurationError, SemanticReleaseBaseError


def setup_hook(argv: list):
    """
    A hook to be used in setup.py to enable `python setup.py publish`.

    :param argv: sys.argv
    """
    if len(argv) > 1 and argv[1] in ["version", "publish", "changelog"]:
        from .cli import main

        main()
