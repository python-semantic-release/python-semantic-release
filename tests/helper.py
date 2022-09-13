import secrets
import string
from typing import Optional

from git import Repo


def shortuid(length: int = 8) -> str:
    alphabet = string.ascii_lowercase + string.digits

    return "".join(secrets.choice(alphabet) for _ in range(length))


def add_text_to_file(repo: Repo, filename: str, text: Optional[str] = None):

    with open(f"{repo.working_tree_dir}/{filename}", "a+") as f:
        f.write(text or f"default text {shortuid(12)}")
        f.write("\n")

    repo.index.add(filename)

