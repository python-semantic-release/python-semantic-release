__version__ = '0.7.0'


def setup_hook(argv):
    """
    A hook to be used in setup.py to enable `python setup.py publish`.

    :param argv: sys.argv
    """
    if len(argv) > 1 and argv[1] in ['version', 'publish']:
        from semantic_release.cli import main
        main()
