"""Entrypoint for the `semantic-release` module."""
# ruff: noqa: T201, print statements are fine here as this is for cli entry only

from __future__ import annotations

import sys
from traceback import format_exception

from semantic_release import globals
from semantic_release.cli.commands.main import main as cli_main


def main() -> None:
    try:
        cli_main(args=sys.argv[1:])
        print("semantic-release completed successfully.", file=sys.stderr)
    except KeyboardInterrupt:
        print("\n-- User Abort! --", file=sys.stderr)
        sys.exit(127)
    except Exception as err:  # noqa: BLE001, graceful error handling across application
        if globals.debug:
            print(f"{err.__class__.__name__}: {err}\n", file=sys.stderr)
            etype, value, traceback = sys.exc_info()
            print(
                str.join(
                    "",
                    format_exception(
                        etype,
                        value,
                        traceback,
                        limit=None,
                        chain=True,
                    )[:-1],
                ),
                file=sys.stderr,
            )
        print(f"::ERROR:: {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
