"""
Features package for GitFlowy.
Each module encapsulates a distinct domain action of the CLI.
"""

from gitflowy.features.status import handle_status
from gitflowy.features.commit import handle_commit
from gitflowy.features.branch import handle_branches
from gitflowy.features.sync import handle_sync
from gitflowy.features.history import handle_history
from gitflowy.features.stash import handle_stash
from gitflowy.features.tags import handle_tags
from gitflowy.features.undo import handle_undo
from gitflowy.features.pr import handle_pull_requests

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
