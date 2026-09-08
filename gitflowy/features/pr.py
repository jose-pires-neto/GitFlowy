import subprocess
import webbrowser
from rich.table import Table
import questionary

from gitflowy.theme import console
from gitflowy.services.git_service import GitService
from gitflowy.services.github_service import GitHubService
from gitflowy.ui import show_header


def handle_pull_requests(git_service: GitService = None, github_service: GitHubService = None):
    """Gerenciamento de Pull Requests via GitHub CLI."""
    service = git_service or GitService()
    gh = github_service or GitHubService()

    if not gh.is_installed():
        show_header("Pull Requests", "Integração com GitHub")
        console.print("[bold red]O GitHub CLI (gh) não foi encontrado no seu sistema.[/bold red]")
        console.print("Para gerenciar Pull Requests pelo terminal, instale o gh: https://cli.github.com/")
        questionary.press_any_key_to_continue("\nPressione qualquer tecla para voltar...").ask()
        return

    if not gh.is_authenticated():
        show_header("Pull Requests", "Autenticação Necessária")
        console.print("[yellow]O GitHub CLI (gh) está instalado, mas você não está logado na sua conta.[/yellow]")
        if questionary.confirm("Deseja fazer o login no GitHub agora?").ask():
            gh_exe = gh.get_executable_path()
            if gh_exe:
                subprocess.run([gh_exe, "auth", "login"])
            
            if not gh.is_authenticated():
                console.print("[red]\nAutenticação não concluída.[/red]")
                questionary.press_any_key_to_continue("Pressione qualquer tecla para voltar...").ask()
                return
        else:
            return

    while True:
        show_header("Gerenciar Pull Requests", "Crie, avalie e faça merge de PRs no GitHub")
        
        action = questionary.select(
            "O que deseja fazer?",
            choices=[
                "Criar novo Pull Request",
                "Listar e gerenciar PRs abertos",
                "Voltar"
            ]
        ).ask()
        
        if not action or action == "Voltar":
            break
            
        if action == "Criar novo Pull Request":
            current_branch, _ = service.get_branches()
            last_commit = service.get_last_commit_message()
            default_title = last_commit if last_commit else current_branch
            
            pr_title = questionary.text("Título do Pull Request:", default=default_title).ask()
            if pr_title:
                pr_body = questionary.text("Descrição (opcional):").ask()
                
                with console.status("[bold cyan]Criando Pull Request...[/bold cyan]", spinner="dots"):
                    succ_pr, out_pr = gh.create_pr(pr_title, pr_body if pr_body else "")
                    
                show_header("Gerenciar Pull Requests", "Resultado")
                if succ_pr:
                    console.print("[bold green]Pull Request criado com sucesso![/bold green]")
                    console.print(f"Link: [link={out_pr.strip()}]{out_pr.strip()}[/link]")
                else:
                    console.print(f"[bold red]Erro ao criar o Pull Request:[/bold red]\n{out_pr}")
                questionary.press_any_key_to_continue("\nPressione qualquer tecla para continuar...").ask()
                
        elif action == "Listar e gerenciar PRs abertos":
            with console.status("[bold cyan]Buscando Pull Requests abertos...[/bold cyan]", spinner="dots"):
                succ_list, prs = gh.list_prs(limit=30)
                
            if not succ_list or not prs:
                show_header("Pull Requests Abertos", "Lista vazia")
                console.print("[yellow]Nenhum Pull Request aberto encontrado.[/yellow]")
                questionary.press_any_key_to_continue("\nPressione qualquer tecla para continuar...").ask()
                continue
                
            table = Table(title="Pull Requests Abertos", expand=True)
            table.add_column("ID", style="cyan", justify="right")
            table.add_column("Título", style="white")
            table.add_column("Autor", style="magenta")
            
            choices = []
            for pr in prs:
                num_str = f"#{pr['number']}"
                table.add_row(num_str, pr["title"], pr["author"])
                choices.append(questionary.Choice(title=f"{num_str} - {pr['title']} ({pr['author']})", value=pr))
                
            choices.append(questionary.Choice(title="Voltar", value=None))
            
            show_header("Pull Requests Abertos", "Selecione um PR para gerenciar", custom_display=table)
            
            selected_pr = questionary.select(
                "Qual Pull Request deseja gerenciar?",
                choices=choices
            ).ask()
            
            if not selected_pr:
                continue
                
            pr_action = questionary.select(
                f"Gerenciando PR #{selected_pr['number']} ({selected_pr['title']})",
                choices=[
                    "Fazer merge do PR",
                    "Fechar PR (sem merge)",
                    "Abrir no navegador",
                    "Voltar"
                ]
            ).ask()
            
            if not pr_action or pr_action == "Voltar":
                continue
                
            if pr_action == "Fazer merge do PR":
                merge_type = questionary.select(
                    "Qual método de merge deseja usar?",
                    choices=[
                        questionary.Choice(title="Merge (Create a merge commit)", value="--merge"),
                        questionary.Choice(title="Squash (Squash and merge)", value="--squash"),
                        questionary.Choice(title="Rebase (Rebase and merge)", value="--rebase")
                    ]
                ).ask()
                
                if merge_type and questionary.confirm(f"Confirma o merge do PR #{selected_pr['number']}?").ask():
                    delete_remote = questionary.confirm("Deseja deletar a branch remota após o merge?", default=False).ask()
                    with console.status("[bold cyan]Realizando merge...[/bold cyan]", spinner="dots"):
                        succ_merge, out_merge = gh.merge_pr(selected_pr["number"], merge_type=merge_type, delete_branch=delete_remote)
                        
                    show_header("Pull Requests", "Resultado do Merge")
                    if succ_merge:
                        console.print(f"[bold green]Pull Request #{selected_pr['number']} mergeado com sucesso![/bold green]")
                    else:
                        console.print(f"[bold red]Erro ao realizar merge:[/bold red]\n{out_merge}")
                        
            elif pr_action == "Fechar PR (sem merge)":
                if questionary.confirm(f"Tem certeza que deseja FECHAR o PR #{selected_pr['number']} sem fazer merge?").ask():
                    with console.status("[bold cyan]Fechando PR...[/bold cyan]", spinner="dots"):
                        succ_close, out_close = gh.close_pr(selected_pr["number"])
                    show_header("Pull Requests", "Resultado")
                    if succ_close:
                        console.print(f"[bold green]Pull Request #{selected_pr['number']} fechado com sucesso![/bold green]")
                    else:
                        console.print(f"[bold red]Erro ao fechar PR:[/bold red]\n{out_close}")
                        
            elif pr_action == "Abrir no navegador":
                webbrowser.open(selected_pr["url"])
                console.print(f"[green]Navegador aberto em: {selected_pr['url']}[/green]")
                
            questionary.press_any_key_to_continue("\nPressione qualquer tecla para continuar...").ask()
