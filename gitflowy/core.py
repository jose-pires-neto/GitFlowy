import os
import subprocess
import sys
from gitflowy.theme import console

def run_git(args, exit_on_error=False):
    """Executa um comando git de forma silenciosa. Retorna (sucesso, output_ou_erro)."""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            encoding='utf-8', # CORREÇÃO 3: Previne quebra de encoding no Windows
            errors='replace',
            check=True
        )
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else (e.stdout.strip() if e.stdout else str(e))
        if exit_on_error:
            console.print(f"[bold red]Erro crítico no Git:[/bold red] {error_msg}")
            sys.exit(1)
        return False, error_msg

def is_git_repo():
    """Verifica se a pasta atual é um repositório Git."""
    return os.path.isdir(".git") or run_git(["rev-parse", "--is-inside-work-tree"])[0]

def get_changed_files():
    """Obtém a lista de arquivos modificados, adicionados ou deletados."""
    # CORREÇÃO 2: Evita aspas e usa -uall para mostrar arquivos dentro de pastas untracked
    success, output = run_git(["-c", "core.quotePath=false", "status", "--porcelain", "-uall"])
    if not success or not output:
        return []
    
    files = []
    for line in output.split("\n"):
        if len(line) > 2:
            status = line[:2]
            raw_path = line[3:]
            # Trata o caso de arquivos renomeados no Git (ex: R  old -> new)
            actual_path = raw_path.split(" -> ")[-1] if " -> " in raw_path else raw_path
            
            # Trabalhando com Dicionário, eliminamos bugs de fatiamento de strings
            files.append({
                "status": status,
                "raw_path": raw_path,
                "path": actual_path
            })
    return files

def get_branches():
    """Retorna a branch atual e uma lista de todas as branches locais."""
    success, output = run_git(["branch", "--format=%(refname:short)"])
    if not success: return "", []
    
    branches = output.split("\n")
    
    success, current = run_git(["branch", "--show-current"])
    current_branch = current if success else ""
    
    return current_branch, [b for b in branches if b]
