import secrets
import string
from itertools import zip_longest
from typing import Optional, List, Tuple

from git import Repo


def shortuid(length: int = 8) -> str:
    alphabet = string.ascii_lowercase + string.digits

    return "".join(secrets.choice(alphabet) for _ in range(length))


def add_text_to_file(repo: Repo, filename: str, text: Optional[str] = None):
    with open(f"{repo.working_tree_dir}/{filename}", "a+") as f:
        f.write(text or f"default text {shortuid(12)}")
        f.write("\n")

    repo.index.add(filename)


def diff_strings(str_a: str, str_b: str) -> Tuple[List[Tuple[int, str]], List[Tuple[int, str]]]:
    deleted = []
    added = []
    for pos, (left, right) in enumerate(zip_longest(str_a, str_b, fillvalue=None)):
        if left == right:
            continue
        if left is not None:
            deleted.append((pos, left))
        if right is not None:
            added.append((pos, right))
    return deleted, added
