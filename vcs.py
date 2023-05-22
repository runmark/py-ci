import os

import pygit2


def get_last_commit_id(repo_path: str) -> str:
    repo_path = os.path.expandvars(repo_path)
    repo = pygit2.Repository(repo_path)
    return str(repo.head.target)
