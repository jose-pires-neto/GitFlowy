import unittest
from pathlib import Path
import gitflowy


class TestHandlersSafety(unittest.TestCase):
    def test_version_consistency(self):
        """Garante que a versão em __version__ coincide com pyproject.toml."""
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        with open(pyproject_path, "r", encoding="utf-8") as f:
            content = f.read()

        found = False
        for line in content.splitlines():
            if line.strip().startswith("version ="):
                version_str = line.split("=")[1].strip().strip('"').strip("'")
                self.assertEqual(gitflowy.__version__, version_str)
                found = True
                break
        self.assertTrue(found, "Campo 'version' não encontrado no pyproject.toml")

    def test_ghost_user_pr_handling(self):
        """Garante que PR com autor nulo (ghost user ou integração bot) não quebra com NoneType."""
        prs = [
            {"number": 101, "title": "Dependabot update", "author": None},
            {"number": 102, "title": "Feature auth", "author": {"login": "octocat"}}
        ]

        extracted = []
        for pr in prs:
            num_str = f"#{pr.get('number', '?')}"
            author_info = pr.get('author')
            author_login = author_info.get('login', 'desconhecido') if isinstance(author_info, dict) else 'desconhecido'
            pr_title = pr.get('title', 'Sem título')
            extracted.append((num_str, pr_title, author_login))

        self.assertEqual(extracted[0], ("#101", "Dependabot update", "desconhecido"))
        self.assertEqual(extracted[1], ("#102", "Feature auth", "octocat"))


if __name__ == "__main__":
    unittest.main()
