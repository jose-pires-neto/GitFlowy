import unittest
import subprocess
from unittest.mock import patch, MagicMock

from gitflowy.core import (
    run_git,
    is_git_repo,
    get_branches,
    get_changed_files,
    get_remotes,
    get_default_remote,
    get_tags,
)


class TestCore(unittest.TestCase):
    def test_run_git_success(self):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="main\n", stderr="", returncode=0)
            success, out = run_git(["branch", "--show-current"])
            self.assertTrue(success)
            self.assertEqual(out, "main")
            mock_run.assert_called_once()

    def test_run_git_failure(self):
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(
                returncode=128, cmd=["git"], stderr="fatal: not a git repository\n"
            )
            success, err = run_git(["status"])
            self.assertFalse(success)
            self.assertIn("not a git repository", err)

    def test_is_git_repo_true(self):
        with patch("gitflowy.core.run_git") as mock_run_git:
            mock_run_git.return_value = (True, "true")
            self.assertTrue(is_git_repo())

    def test_is_git_repo_false(self):
        with patch("gitflowy.core.run_git") as mock_run_git:
            mock_run_git.return_value = (False, "fatal: not a git repository")
            self.assertFalse(is_git_repo())

    def test_get_branches(self):
        with patch("gitflowy.core.run_git") as mock_run_git:
            def side_effect(args, **kwargs):
                if "--format=%(refname:short)" in args:
                    return True, "main\nfeature/auth\ndevelop"
                if "--show-current" in args:
                    return True, "feature/auth"
                return False, ""

            mock_run_git.side_effect = side_effect
            current, branches = get_branches()
            self.assertEqual(current, "feature/auth")
            self.assertEqual(branches, ["main", "feature/auth", "develop"])

    def test_get_remotes(self):
        with patch("gitflowy.core.run_git") as mock_run_git:
            mock_run_git.return_value = (True, "origin\nupstream\n")
            remotes = get_remotes()
            self.assertEqual(remotes, ["origin", "upstream"])

    def test_get_default_remote_with_origin(self):
        with patch("gitflowy.core.get_remotes") as mock_remotes:
            mock_remotes.return_value = ["upstream", "origin"]
            self.assertEqual(get_default_remote(), "origin")

    def test_get_default_remote_without_origin(self):
        with patch("gitflowy.core.get_remotes") as mock_remotes:
            mock_remotes.return_value = ["fork", "upstream"]
            self.assertEqual(get_default_remote(), "fork")

    def test_get_default_remote_empty(self):
        with patch("gitflowy.core.get_remotes") as mock_remotes:
            mock_remotes.return_value = []
            self.assertEqual(get_default_remote(), "origin")

    def test_get_changed_files_empty(self):
        with patch("gitflowy.core.run_git") as mock_run_git:
            mock_run_git.return_value = (True, "")
            files = get_changed_files()
            self.assertEqual(files, [])

    def test_get_changed_files_parsing(self):
        porcelain_output = (
            " M app.py\n"
            "?? new_file.txt\n"
            "R  old_name.py -> new_name.py\n"
            " D removed.py"
        )
        with patch("gitflowy.core.run_git") as mock_run_git:
            mock_run_git.return_value = (True, porcelain_output)
            files = get_changed_files()
            self.assertEqual(len(files), 4)

            self.assertEqual(files[0]["status"], " M")
            self.assertEqual(files[0]["path"], "app.py")

            self.assertEqual(files[1]["status"], "??")
            self.assertEqual(files[1]["path"], "new_file.txt")

            self.assertEqual(files[2]["status"], "R ")
            self.assertEqual(files[2]["path"], "new_name.py")
            self.assertEqual(files[2]["raw_path"], "old_name.py -> new_name.py")

            self.assertEqual(files[3]["status"], " D")
            self.assertEqual(files[3]["path"], "removed.py")

    def test_get_tags(self):
        tag_output = "v1.0.0<||>2026-01-01\nv0.9.0<||>2025-12-15"
        with patch("gitflowy.core.run_git") as mock_run_git:
            mock_run_git.return_value = (True, tag_output)
            tags = get_tags()
            self.assertEqual(len(tags), 2)
            self.assertEqual(tags[0], {"name": "v1.0.0", "date": "2026-01-01"})
            self.assertEqual(tags[1], {"name": "v0.9.0", "date": "2025-12-15"})


if __name__ == "__main__":
    unittest.main()
