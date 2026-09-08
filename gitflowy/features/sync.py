import subprocess
import questionary

from gitflowy.theme import console
from gitflowy.services.git_service import GitService
from gitflowy.services.github_service import GitHubService
from gitflowy.ui import show_header


def handle_sync(git_service: GitService = None, github_service: GitHubService = None):
    """Faz Push e Pull do repositório com integração opcional de Pull Request."""
    service = git_service or GitService()
    gh = github_service or GitHubService()
    
    show_header("Sincronização", "Envie ou baixe alterações do repositório remoto")
    action = questionary.select(
        "Selecione uma ação:",
        choices=["Push (Enviar alterações)", "Pull (Puxar alterações)", "Voltar"]
    ).ask()
    
    if not action or action == "Voltar":
        return
    
    current_branch, _ = service.get_branches()
    remote_name = service.get_default_remote()
    
    if "Push" in action:
        with console.status(f"[bold cyan]Enviando branch {current_branch} para {remote_name}...[/bold cyan]"):
            success, msg = service.push(remote=remote_name)
        
        show_header("Sincronização", "Resultado do Push")
        if success:
            console.print("[bold green]Push realizado com sucesso![/bold green]")
            
            # Integração opcional com GitHub CLI
            if gh.is_installed():
                console.print("\n[dim]GitHub CLI (gh) detectado no sistema.[/dim]")
                if questionary.confirm("Deseja abrir um Pull Request para esta branch agora?").ask():
                    if not gh.is_authenticated():
                        console.print("[yellow]Você precisa autenticar o GitHub CLI primeiro.[/yellow]")
                        if questionary.confirm("Deseja fazer login no GitHub agora?").ask():
                            gh_exe = gh.get_executable_path()
                            if gh_exe:
                                subprocess.run([gh_exe, "auth", "login"])
                    
                    if gh.is_authenticated():
                        last_commit = service.get_last_commit_message()
                        default_title = last_commit if last_commit else current_branch
                        
                        pr_title = questionary.text("Título do Pull Request:", default=default_title).ask()
                        if pr_title:
                            pr_body = questionary.text("Descrição (opcional):").ask()
                            
                            with console.status("[bold cyan]Criando Pull Request...[/bold cyan]", spinner="dots"):
                                succ_pr, out_pr = gh.create_pr(pr_title, pr_body if pr_body else "")
                                
                            if succ_pr:
                                console.print("[bold green]Pull Request criado com sucesso![/bold green]")
                                console.print(f"Link: [link={out_pr}]{out_pr}[/link]")
                            else:
                                console.print(f"[bold red]Erro ao criar o Pull Request:[/bold red]\n{out_pr}")
                    else:
                        console.print("[red]Operação cancelada: GitHub CLI não autenticado.[/red]")
        else:
            console.print(f"[bold red]Erro no Push:[/bold red]\n{msg}")
            
    elif "Pull" in action:
        with console.status(f"[bold cyan]Puxando alterações em {current_branch}...[/bold cyan]"):
            success, msg = service.pull()
        show_header("Sincronização", "Resultado do Pull")
        if success:
            console.print("[bold green]Pull realizado com sucesso![/bold green]")
        else:
            console.print(f"[bold red]Erro no Pull:[/bold red]\n{msg}")
                
    questionary.press_any_key_to_continue("\nPressione qualquer tecla para voltar...").ask()
