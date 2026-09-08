from rich.panel import Panel
from rich.tree import Tree
import questionary

from gitflowy.theme import console
from gitflowy.services.git_service import GitService
from gitflowy.ui import show_header


def handle_branches(git_service: GitService = None):
    """Gerenciador de Branches visual."""
    service = git_service or GitService()
    current_branch, branches = service.get_branches()
    
    tree = Tree("[bold green]Repositório Local[/bold green]", guide_style="bold cyan")
    primary_branch = next((b for b in branches if b in ["main", "master"]), None)
    
    if primary_branch:
        is_current = " [bold magenta](atual)[/bold magenta]" if primary_branch == current_branch else ""
        main_node = tree.add(f"* [bold cyan]{primary_branch}[/bold cyan]{is_current}")
        
        for b in branches:
            if b != primary_branch:
                if b == current_branch:
                    main_node.add(f"- [bold magenta]{b}[/bold magenta] [dim](atual)[/dim]")
                else:
                    main_node.add(f"- [cyan]{b}[/cyan]")
    else:
        for b in branches:
            if b == current_branch:
                tree.add(f"- [bold magenta]{b}[/bold magenta] [dim](atual)[/dim]")
            else:
                tree.add(f"- [cyan]{b}[/cyan]")
            
    tree_panel = Panel(tree, title="Estrutura de Branches", border_style="cyan", expand=True)
    show_header("Gerenciar Branches", "Crie, navegue ou delete suas branches", custom_display=tree_panel)
    
    action = questionary.select(
        "O que deseja fazer?",
        choices=[
            "Trocar de branch",
            "Criar nova branch",
            "Deletar branch",
            "Voltar"
        ]
    ).ask()

    if not action or action == "Voltar":
        return

    if action == "Trocar de branch":
        options = [b for b in branches if b != current_branch]
        if not options:
            console.print("[yellow]Não há outras branches locais para alternar.[/yellow]")
            questionary.press_any_key_to_continue("Pressione qualquer tecla para voltar...").ask()
            return
            
        target = questionary.select("Para qual branch deseja mudar?", choices=options).ask()
        if target:
            success, msg = service.checkout(target)
            show_header("Gerenciar Branches", "Resultado")
            console.print(f"[green]Mudou para a branch '{target}'[/green]" if success else f"\n[red]Erro:\n{msg}[/red]")
            questionary.press_any_key_to_continue("Pressione qualquer tecla para voltar...").ask()

    elif action == "Criar nova branch":
        new_branch = questionary.text("Nome da nova branch:").ask()
        if new_branch:
            success, msg = service.create_branch(new_branch)
            show_header("Gerenciar Branches", "Resultado")
            console.print(f"[green]Branch '{new_branch}' criada e ativada![/green]" if success else f"[red]Erro: {msg}[/red]")
            questionary.press_any_key_to_continue("Pressione qualquer tecla para voltar...").ask()
            
    elif action == "Deletar branch":
        options = [b for b in branches if b != current_branch and b not in ["main", "master"]]
        if not options:
            console.print("[yellow]Não há branches seguras para deletar (não é possível deletar a branch atual ou main/master).[/yellow]")
            questionary.press_any_key_to_continue("Pressione qualquer tecla para voltar...").ask()
            return
            
        target = questionary.select("Qual branch deseja deletar?", choices=options).ask()
        if target and questionary.confirm(f"Confirma a exclusão de '{target}'?").ask():
            success, msg = service.delete_branch(target, force=False)
            if not success:
                console.print(f"[yellow]Atenção: A branch '{target}' possui commits não mesclados![/yellow]")
                if questionary.confirm("Deseja FORÇAR a exclusão (-D)? Os commits não mesclados serão PERDIDOS permanentemente.").ask():
                    success, msg = service.delete_branch(target, force=True)
                    console.print(f"[green]Branch '{target}' deletada forçadamente![/green]" if success else f"[red]Erro: {msg}[/red]")
            else:
                console.print(f"[green]Branch '{target}' deletada com segurança![/green]")
            questionary.press_any_key_to_continue("Pressione qualquer tecla para voltar...").ask()
