"""
GitService: Encapsulates pure Git operations, decoupling logic from terminal UI.
Supports dependency injection of git runner for testability.
"""

from typing import Callable, Optional, Tuple, List, Dict
from gitflowy.core import (
    run_git as default_run_git,
    is_git_repo,
    get_changed_files,
    get_branches,
    get_tags,
    get_remotes,
    get_default_remote,
)


class GitService:
    def __init__(self, runner: Optional[Callable] = None):
        self._run_git = runner or default_run_git

    def is_repo(self) -> bool:
        """Verifica se o diretório atual está dentro de um repositório Git válido."""
        success, output = self._run_git(["rev-parse", "--is-inside-work-tree"])
        return success and output.strip() == "true"

    def get_status(self) -> List[Dict[str, str]]:
        """Obtém lista de arquivos modificados com status, raw_path e path."""
        success, output = self._run_git(["-c", "core.quotePath=false", "status", "--porcelain", "-uall"])
        if not success or not output:
            return []
        
        files = []
        for line in output.split("\n"):
            if len(line) > 2:
                status = line[:2]
                raw_path = line[3:]
                actual_path = raw_path.split(" -> ")[-1] if " -> " in raw_path else raw_path
                files.append({
                    "status": status,
                    "raw_path": raw_path,
                    "path": actual_path
                })
        return files

    def get_branches(self) -> Tuple[str, List[str]]:
        """Retorna (branch_atual, lista_de_todas_branches)."""
        success, output = self._run_git(["branch", "--format=%(refname:short)"])
        if not success:
            return "", []
        
        branches = [b.strip() for b in output.split("\n") if b.strip()]
        
        success_cur, current = self._run_git(["branch", "--show-current"])
        current_branch = current.strip() if success_cur else ""
        
        return current_branch, branches

    def checkout(self, branch: str) -> Tuple[bool, str]:
        """Alterna para uma branch existente."""
        return self._run_git(["checkout", branch])

    def create_branch(self, name: str) -> Tuple[bool, str]:
        """Cria e ativa uma nova branch."""
        return self._run_git(["checkout", "-b", name])

    def delete_branch(self, name: str, force: bool = False) -> Tuple[bool, str]:
        """Deleta uma branch (segura por padrão com -d, ou forçada com -D)."""
        flag = "-D" if force else "-d"
        return self._run_git(["branch", flag, name])

    def add(self, files: List[str]) -> Tuple[bool, str]:
        """Adiciona arquivos ao staging."""
        if files == ["."] or files == [":/"]:
            return self._run_git(["add", "."])
        return self._run_git(["add", "--"] + files)

    def commit(self, message: str, files: Optional[List[str]] = None) -> Tuple[bool, str]:
        """Adiciona arquivos opcionais e realiza commit com a mensagem fornecida."""
        if files:
            add_succ, add_err = self.add(files)
            if not add_succ:
                return False, add_err
        return self._run_git(["commit", "-m", message])

    def get_remotes(self) -> List[str]:
        """Retorna a lista de nomes de repositórios remotos configurados."""
        success, output = self._run_git(["remote"])
        if not success or not output:
            return []
        return [r.strip() for r in output.split("\n") if r.strip()]

    def get_default_remote(self) -> str:
        """Retorna o remoto padrão (origin se existir, ou o primeiro disponível)."""
        remotes = self.get_remotes()
        if not remotes:
            return "origin"
        if "origin" in remotes:
            return "origin"
        return remotes[0]

    def push(self, branch: Optional[str] = None, remote: Optional[str] = None, set_upstream: bool = False) -> Tuple[bool, str]:
        """Executa push da branch para o remote com tratamento automático de upstream."""
        target_remote = remote or self.get_default_remote()
        current_branch, _ = self.get_branches()
        target_branch = branch or current_branch

        if set_upstream:
            return self._run_git(["push", "--set-upstream", target_remote, target_branch])

        success, msg = self._run_git(["push"])
        if not success and "set-upstream" in msg:
            return self._run_git(["push", "--set-upstream", target_remote, target_branch])
        return success, msg

    def pull(self) -> Tuple[bool, str]:
        """Puxa alterações do servidor remoto."""
        return self._run_git(["pull"])

    def get_recent_commits(self, limit: int = 10) -> List[Dict[str, str]]:
        """Retorna lista dos commits mais recentes com hash, mensagem, tempo e autor."""
        success, output = self._run_git(["log", f"-n", str(limit), "--pretty=format:%h<||>%s<||>%ar<||>%an"])
        if not success or not output:
            return []
        
        commits = []
        for line in output.split("\n"):
            parts = line.split("<||>")
            if len(parts) == 4:
                commits.append({
                    "hash": parts[0],
                    "message": parts[1],
                    "time": parts[2],
                    "author": parts[3]
                })
        return commits

    def get_last_commit_message(self) -> str:
        """Retorna a mensagem do último commit realizado."""
        success, output = self._run_git(["log", "-1", "--pretty=format:%s"])
        return output.strip() if success else ""

    def stash_save(self, message: Optional[str] = None) -> Tuple[bool, str]:
        """Guarda alterações no stash com mensagem opcional."""
        args = ["stash", "push", "-m", message] if message else ["stash"]
        return self._run_git(args)

    def stash_pop(self) -> Tuple[bool, str]:
        """Recupera as últimas alterações do stash."""
        return self._run_git(["stash", "pop"])

    def stash_list(self) -> Tuple[bool, str]:
        """Lista alterações salvas no stash."""
        return self._run_git(["stash", "list"])

    def stash_clear(self) -> Tuple[bool, str]:
        """Limpa todos os stashes."""
        return self._run_git(["stash", "clear"])

    def get_tags(self) -> List[Dict[str, str]]:
        """Retorna lista de tags com nome e data."""
        success, output = self._run_git(["tag", "-l", "--format=%(refname:short)<||>%(creatordate:short)", "--sort=-creatordate"])
        if not success or not output:
            return []
        
        tags = []
        for line in output.split("\n"):
            if "<||>" in line:
                tag, date = line.split("<||>")
                if tag:
                    tags.append({"name": tag, "date": date})
        return tags

    def create_tag(self, name: str, message: Optional[str] = None) -> Tuple[bool, str]:
        """Cria uma tag anotada."""
        msg = message if message else f"Release {name}"
        return self._run_git(["tag", "-a", name, "-m", msg])

    def delete_tag(self, name: str, remote: Optional[str] = None) -> Tuple[bool, str]:
        """Deleta tag local e opcionalmente do remote."""
        success, msg = self._run_git(["tag", "-d", name])
        if not success:
            return False, msg
        
        if remote:
            succ_rem, msg_rem = self._run_git(["push", "--delete", remote, name])
            if not succ_rem:
                return True, f"Deletada localmente, mas falhou no remoto: {msg_rem}"
        return True, msg

    def push_tags(self, remote: Optional[str] = None) -> Tuple[bool, str]:
        """Envia todas as tags locais para o remoto."""
        target_remote = remote or self.get_default_remote()
        return self._run_git(["push", "--tags", target_remote])

    def soft_reset(self, target: str = "HEAD~1") -> Tuple[bool, str]:
        """Desfaz commit(s) mantendo arquivos modificados na árvore de trabalho."""
        return self._run_git(["reset", "--soft", target])

    def revert(self, commit_hash: str) -> Tuple[bool, str]:
        """Cria commit reverso sem abrir editor interativo."""
        return self._run_git(["revert", "--no-edit", commit_hash])

    def discard_all_changes(self) -> Tuple[bool, str]:
        """Descarta todas as alterações locais rastreadas e não rastreadas."""
        success1, out1 = self._run_git(["reset", "--hard"])
        success2, out2 = self._run_git(["clean", "-fd"])
        if success1 and success2:
            return True, "Árvore de trabalho limpa."
        return False, f"{out1}\n{out2}".strip()
