__version__ = '0.5.1'


def setup_hook(argv):
    if len(argv) > 1 and argv[1] in ['version', 'publish']:
        from semantic_release.cli import main
        main()
