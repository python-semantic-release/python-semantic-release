from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from jinja2 import Environment

    from semantic_release.changelog.release_history import ReleaseHistory
    from semantic_release.hvcs._base import HvcsBase


@dataclass
class ChangelogContext:
    repo_name: str
    repo_owner: str
    hvcs_type: str
    history: ReleaseHistory
    filters: tuple[Callable[..., Any], ...] = ()

    def bind_to_environment(self, env: Environment) -> Environment:
        env.globals["context"] = self
        for f in self.filters:
            env.filters[f.__name__] = f
        return env


def make_changelog_context(
    hvcs_client: HvcsBase, release_history: ReleaseHistory
) -> ChangelogContext:
    return ChangelogContext(
        repo_name=hvcs_client.repo_name,
        repo_owner=hvcs_client.owner,
        history=release_history,
        hvcs_type=hvcs_client.__class__.__name__.lower(),
        filters=(*hvcs_client.get_changelog_context_filters(),),
    )
