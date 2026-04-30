import os
import subprocess
import sys
import shutil
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

import platform

def get_gh_executable():
    """Retorna o caminho do executável do gh. Procura em locais comuns se não estiver no PATH."""
    gh_path = shutil.which("gh")
    if gh_path:
        return gh_path
        
    # Tratamento para quando acabou de instalar no Windows e o PATH não atualizou no terminal atual
    if platform.system() == "Windows":
        common_paths = [
            r"C:\Program Files\GitHub CLI\gh.exe",
            os.path.expandvars(r"%LocalAppData%\Programs\GitHub CLI\gh.exe")
        ]
        
        # Busca recursiva rápida na pasta do WinGet caso a versão mude no nome da pasta
        winget_dir = os.path.expandvars(r"%LocalAppData%\Microsoft\WinGet\Packages")
        if os.path.exists(winget_dir):
            for d in os.listdir(winget_dir):
                if d.lower().startswith("github.cli"):
                    path = os.path.join(winget_dir, d, "gh.exe")
                    if os.path.exists(path):
                        common_paths.append(path)
                        
        for path in common_paths:
            if os.path.exists(path):
                return path
                
    return None

def has_gh_cli():
    """Verifica se o GitHub CLI (gh) está instalado."""
    return get_gh_executable() is not None

def check_gh_auth():
    """Verifica se o usuário está autenticado no GitHub CLI."""
    gh_exe = get_gh_executable()
    if not gh_exe:
        return False
    
    try:
        # Redireciona a saída de erro padrão para stdout e checa se o comando tem sucesso
        result = subprocess.run([gh_exe, "auth", "status"], capture_output=True, text=True)
        return result.returncode == 0
    except subprocess.CalledProcessError:
        return False

def run_gh(args):
    """Executa um comando do GitHub CLI."""
    gh_exe = get_gh_executable()
    if not gh_exe:
        return False, "GitHub CLI (gh) não encontrado no sistema."
        
    try:
        result = subprocess.run(
            [gh_exe] + args,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            check=True
        )
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else (e.stdout.strip() if e.stdout else str(e))
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

def get_tags():
    """Retorna a lista de tags existentes no repositório com suas datas de criação."""
    success, output = run_git(["tag", "-l", "--format=%(refname:short)<||>%(creatordate:short)", "--sort=-creatordate"])
    if not success or not output: return []
    
    tags = []
    for line in output.split('\n'):
        if '<||>' in line:
            tag, date = line.split('<||>')
            if tag:
                tags.append({"name": tag, "date": date})
    return tags

