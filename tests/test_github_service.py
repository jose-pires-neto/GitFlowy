import unittest
from unittest.mock import MagicMock
from gitflowy.services.github_service import GitHubService


class TestGitHubService(unittest.TestCase):
    def setUp(self):
        self.mock_runner = MagicMock()
        self.service = GitHubService(runner=self.mock_runner)

    def test_create_pr(self):
        self.mock_runner.return_value = (True, "https://github.com/org/repo/pull/1")
        succ, url = self.service.create_pr("feat: test pr", "description")
        self.assertTrue(succ)
        self.mock_runner.assert_called_with(["pr", "create", "--title", "feat: test pr", "--body", "description"])

    def test_list_prs_valid(self):
        raw_json = '[{"number": 1, "title": "Add auth", "author": {"login": "octocat"}, "url": "https://github.com/pr/1"}]'
        self.mock_runner.return_value = (True, raw_json)
        succ, prs = self.service.list_prs()
        self.assertTrue(succ)
        self.assertEqual(len(prs), 1)
        self.assertEqual(prs[0]["number"], 1)
        self.assertEqual(prs[0]["title"], "Add auth")
        self.assertEqual(prs[0]["author"], "octocat")
        self.assertEqual(prs[0]["url"], "https://github.com/pr/1")

    def test_list_prs_ghost_user(self):
        """Testa autor nulo/deletado (ghost user) sem disparar TypeError."""
        raw_json = '[{"number": 2, "title": "Dependabot bump", "author": null, "url": "https://github.com/pr/2"}]'
        self.mock_runner.return_value = (True, raw_json)
        succ, prs = self.service.list_prs()
        self.assertTrue(succ)
        self.assertEqual(len(prs), 1)
        self.assertEqual(prs[0]["author"], "desconhecido")

    def test_list_prs_invalid_json(self):
        self.mock_runner.return_value = (True, "invalid json output")
        succ, prs = self.service.list_prs()
        self.assertFalse(succ)
        self.assertEqual(prs, [])

    def test_merge_pr_without_delete(self):
        self.mock_runner.return_value = (True, "Merged pull request #1")
        succ, msg = self.service.merge_pr(1, merge_type="--squash", delete_branch=False)
        self.assertTrue(succ)
        self.mock_runner.assert_called_with(["pr", "merge", "1", "--squash"])

    def test_merge_pr_with_delete(self):
        self.mock_runner.return_value = (True, "Merged pull request #1 and deleted branch")
        succ, msg = self.service.merge_pr(1, merge_type="--merge", delete_branch=True)
        self.assertTrue(succ)
        self.mock_runner.assert_called_with(["pr", "merge", "1", "--merge", "--delete-branch"])

    def test_close_pr(self):
        self.mock_runner.return_value = (True, "Closed pull request #1")
        succ, msg = self.service.close_pr(1)
        self.assertTrue(succ)
        self.mock_runner.assert_called_with(["pr", "close", "1"])


if __name__ == "__main__":
    unittest.main()
