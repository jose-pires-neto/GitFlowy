"""
Facade module re-exporting all handlers from gitflowy.features.
Preserves backwards compatibility while keeping the architecture cleanly modular.
"""

from gitflowy.features import (
    handle_status,
    handle_commit,
    handle_branches,
    handle_sync,
    handle_history,
    handle_stash,
    handle_tags,
    handle_undo,
    handle_pull_requests,
)

__all__ = [
    "handle_status",
    "handle_commit",
    "handle_branches",
    "handle_sync",
    "handle_history",
    "handle_stash",
    "handle_tags",
    "handle_undo",
    "handle_pull_requests",
]
