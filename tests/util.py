from __future__ import annotations

import filecmp
import os
import secrets
import string
from contextlib import contextmanager
from itertools import zip_longest
from tempfile import NamedTemporaryFile
from typing import Iterable, Optional, TypeVar

from git import Repo


def shortuid(length: int = 8) -> str:
    alphabet = string.ascii_lowercase + string.digits

    return "".join(secrets.choice(alphabet) for _ in range(length))


def add_text_to_file(repo: Repo, filename: str, text: str | None = None):
    with open(f"{repo.working_tree_dir}/{filename}", "a+") as f:
        f.write(text or f"default text {shortuid(12)}")
        f.write("\n")

    repo.index.add(filename)


@contextmanager
def netrc_file(machine: str) -> NamedTemporaryFile:
    with NamedTemporaryFile("w") as netrc:
        # Add these attributes to use in tests as source of truth
        netrc.login_username = "username"
        netrc.login_password = "password"

        netrc.write(f"machine {machine}" + "\n")
        netrc.write(f"login {netrc.login_username}" + "\n")
        netrc.write(f"password {netrc.login_password}" + "\n")
        netrc.flush()

        yield netrc


def flatten_dircmp(dcmp: filecmp.dircmp) -> list[str]:
    return dcmp.diff_files + [
        os.sep.join((dir, file))
        for dir, cmp in dcmp.subdirs.items()
        for file in flatten_dircmp(cmp)
    ]


_R = TypeVar("_R")


def xdist_sort_hack(it: Iterable[_R]) -> Iterable[_R]:
    """
    hack for pytest-xdist
    https://pytest-xdist.readthedocs.io/en/latest/known-limitations.html#workarounds

    taking an iterable of params for a pytest.mark.parametrize decorator, this
    ensures a deterministic sort so that xdist can always work

    Being able to use `pytest -nauto` is a huge speedup on testing
    """
    return dict(enumerate(it)).values()
