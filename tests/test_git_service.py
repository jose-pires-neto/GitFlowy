import unittest
from unittest.mock import MagicMock
from gitflowy.services.git_service import GitService


class TestGitService(unittest.TestCase):
    def setUp(self):
        self.mock_runner = MagicMock()
        self.service = GitService(runner=self.mock_runner)

    def test_is_repo_true(self):
        self.mock_runner.return_value = (True, "true\n")
        self.assertTrue(self.service.is_repo())
        self.mock_runner.assert_called_with(["rev-parse", "--is-inside-work-tree"])

    def test_is_repo_false(self):
        self.mock_runner.return_value = (False, "fatal: not a git repo")
        self.assertFalse(self.service.is_repo())

    def test_get_status_empty(self):
        self.mock_runner.return_value = (True, "")
        files = self.service.get_status()
        self.assertEqual(files, [])

    def test_get_status_parsed(self):
        output = " M app.py\n?? test.py\nR  old.py -> new.py"
        self.mock_runner.return_value = (True, output)
        files = self.service.get_status()
        self.assertEqual(len(files), 3)
        self.assertEqual(files[0]["status"], " M")
        self.assertEqual(files[0]["path"], "app.py")
        self.assertEqual(files[1]["status"], "??")
        self.assertEqual(files[1]["path"], "test.py")
        self.assertEqual(files[2]["status"], "R ")
        self.assertEqual(files[2]["path"], "new.py")
        self.assertEqual(files[2]["raw_path"], "old.py -> new.py")

    def test_get_branches(self):
        def side_effect(args):
            if "--format=%(refname:short)" in args:
                return True, "main\nfeature/auth\n"
            if "--show-current" in args:
                return True, "feature/auth\n"
            return False, ""
        self.mock_runner.side_effect = side_effect
        current, branches = self.service.get_branches()
        self.assertEqual(current, "feature/auth")
        self.assertEqual(branches, ["main", "feature/auth"])

    def test_checkout(self):
        self.mock_runner.return_value = (True, "Switched to branch 'main'")
        succ, msg = self.service.checkout("main")
        self.assertTrue(succ)
        self.mock_runner.assert_called_with(["checkout", "main"])

    def test_create_branch(self):
        self.mock_runner.return_value = (True, "Switched to a new branch 'feat/test'")
        succ, msg = self.service.create_branch("feat/test")
        self.assertTrue(succ)
        self.mock_runner.assert_called_with(["checkout", "-b", "feat/test"])

    def test_delete_branch_safe(self):
        self.mock_runner.return_value = (True, "Deleted branch feat/test")
        succ, msg = self.service.delete_branch("feat/test", force=False)
        self.assertTrue(succ)
        self.mock_runner.assert_called_with(["branch", "-d", "feat/test"])

    def test_delete_branch_force(self):
        self.mock_runner.return_value = (True, "Deleted branch feat/test")
        succ, msg = self.service.delete_branch("feat/test", force=True)
        self.assertTrue(succ)
        self.mock_runner.assert_called_with(["branch", "-D", "feat/test"])

    def test_add_all(self):
        self.mock_runner.return_value = (True, "")
        succ, msg = self.service.add(["."])
        self.assertTrue(succ)
        self.mock_runner.assert_called_with(["add", "."])

    def test_add_specific(self):
        self.mock_runner.return_value = (True, "")
        succ, msg = self.service.add(["file1.py", "file2.py"])
        self.assertTrue(succ)
        self.mock_runner.assert_called_with(["add", "--", "file1.py", "file2.py"])

    def test_commit(self):
        self.mock_runner.return_value = (True, "[main 1234567] Test commit")
        succ, msg = self.service.commit("feat: initial commit")
        self.assertTrue(succ)
        self.mock_runner.assert_called_with(["commit", "-m", "feat: initial commit"])

    def test_commit_with_files(self):
        self.mock_runner.return_value = (True, "")
        succ, msg = self.service.commit("feat: initial", files=["file1.py"])
        self.assertTrue(succ)

    def test_push_standard(self):
        self.mock_runner.return_value = (True, "")
        succ, msg = self.service.push()
        self.assertTrue(succ)
        self.mock_runner.assert_called_with(["push"])

    def test_push_upstream_retry(self):
        def side_effect(args):
            if args == ["push"]:
                return False, "fatal: The current branch has no upstream branch. To push the current branch and set the remote as upstream, use\n git push --set-upstream origin feat"
            if "--set-upstream" in args:
                return True, "Everything up-to-date"
            if args == ["remote"]:
                return True, "origin"
            if args == ["branch", "--format=%(refname:short)"]:
                return True, "feat"
            if args == ["branch", "--show-current"]:
                return True, "feat"
            return False, ""
        self.mock_runner.side_effect = side_effect
        succ, msg = self.service.push()
        self.assertTrue(succ)

    def test_pull(self):
        self.mock_runner.return_value = (True, "Already up to date.")
        succ, msg = self.service.pull()
        self.assertTrue(succ)
        self.mock_runner.assert_called_with(["pull"])

    def test_get_recent_commits(self):
        output = "abc1234<||>feat: add login<||>2 hours ago<||>John Doe\ndef5678<||>fix: bug<||>1 day ago<||>Jane Doe"
        self.mock_runner.return_value = (True, output)
        commits = self.service.get_recent_commits(limit=2)
        self.assertEqual(len(commits), 2)
        self.assertEqual(commits[0]["hash"], "abc1234")
        self.assertEqual(commits[0]["message"], "feat: add login")
        self.assertEqual(commits[0]["time"], "2 hours ago")
        self.assertEqual(commits[0]["author"], "John Doe")

    def test_stash_operations(self):
        self.mock_runner.return_value = (True, "Saved working directory")
        self.service.stash_save("wip")
        self.mock_runner.assert_called_with(["stash", "push", "-m", "wip"])

        self.service.stash_pop()
        self.mock_runner.assert_called_with(["stash", "pop"])

        self.service.stash_list()
        self.mock_runner.assert_called_with(["stash", "list"])

        self.service.stash_clear()
        self.mock_runner.assert_called_with(["stash", "clear"])

    def test_tag_operations(self):
        self.mock_runner.return_value = (True, "v1.0.0<||>2026-01-01")
        tags = self.service.get_tags()
        self.assertEqual(len(tags), 1)

        self.service.create_tag("v1.0.0", "Release 1.0.0")
        self.mock_runner.assert_called_with(["tag", "-a", "v1.0.0", "-m", "Release 1.0.0"])

        self.service.delete_tag("v1.0.0")
        self.mock_runner.assert_called_with(["tag", "-d", "v1.0.0"])

    def test_undo_operations(self):
        self.mock_runner.return_value = (True, "")
        self.service.soft_reset("HEAD~1")
        self.mock_runner.assert_called_with(["reset", "--soft", "HEAD~1"])

        self.service.revert("abcdef")
        self.mock_runner.assert_called_with(["revert", "--no-edit", "abcdef"])

        self.mock_runner.return_value = (True, "")
        succ, msg = self.service.discard_all_changes()
        self.assertTrue(succ)


if __name__ == "__main__":
    unittest.main()
