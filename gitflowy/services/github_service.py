"""
GitHubService: Encapsulates GitHub CLI (gh) operations.
Decouples GitHub API interactions and JSON parsing from UI code.
"""

import json
from typing import Callable, Optional, Tuple, List, Dict
from gitflowy.core import (
    run_gh as default_run_gh,
    has_gh_cli,
    check_gh_auth,
    get_gh_executable,
)


class GitHubService:
    def __init__(self, runner: Optional[Callable] = None):
        self._run_gh = runner or default_run_gh

    def is_installed(self) -> bool:
        """Verifica se o binário gh está instalado e acessível no sistema."""
        return has_gh_cli()

    def is_authenticated(self) -> bool:
        """Verifica se o usuário está autenticado no GitHub CLI."""
        return check_gh_auth()

    def get_executable_path(self) -> Optional[str]:
        """Retorna o caminho do executável gh."""
        return get_gh_executable()

    def create_pr(self, title: str, body: str = "") -> Tuple[bool, str]:
        """Cria um Pull Request."""
        args = ["pr", "create", "--title", title, "--body", body]
        return self._run_gh(args)

    def list_prs(self, limit: int = 30) -> Tuple[bool, List[Dict]]:
        """
        Retorna lista de Pull Requests abertos.
        Garante parsing seguro mesmo se autor for nulo (ghost user ou integração).
        """
        args = ["pr", "list", "--json", "number,title,author,url", "--limit", str(limit)]
        success, output = self._run_gh(args)
        if not success:
            return False, []
        
        try:
            raw_prs = json.loads(output)
        except (json.JSONDecodeError, TypeError):
            return False, []
        
        normalized_prs = []
        for pr in raw_prs:
            author_data = pr.get("author")
            author_login = author_data.get("login", "desconhecido") if isinstance(author_data, dict) else "desconhecido"
            normalized_prs.append({
                "number": pr.get("number", 0),
                "title": pr.get("title", "Sem título"),
                "author": author_login,
                "url": pr.get("url", "")
            })
        return True, normalized_prs

    def merge_pr(self, number: int, merge_type: str = "--merge", delete_branch: bool = False) -> Tuple[bool, str]:
        """Executa merge de um Pull Request com método configurável (--merge, --squash, --rebase)."""
        args = ["pr", "merge", str(number), merge_type]
        if delete_branch:
            args.append("--delete-branch")
        return self._run_gh(args)

    def close_pr(self, number: int) -> Tuple[bool, str]:
        """Fecha um Pull Request sem mesclar."""
        return self._run_gh(["pr", "close", str(number)])
