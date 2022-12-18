from git import Commit


def make_commit(message: str) -> Commit:
    return Commit(repo=None, binsha=Commit.NULL_BIN_SHA, message=message)
