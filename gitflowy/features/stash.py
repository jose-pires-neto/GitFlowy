import questionary

from gitflowy.theme import console
from gitflowy.services.git_service import GitService
from gitflowy.ui import show_header


def handle_stash(git_service: GitService = None):
    """Gerencia o stash (área de rascunho)."""
    service = git_service or GitService()
    show_header("Stash", "Guarde suas alterações temporariamente")
    action = questionary.select(
        "Selecione uma opção:",
        choices=[
            "Guardar alterações (stash save)",
            "Recuperar últimas alterações (stash pop)",
            "Listar itens guardados (stash list)",
            "Limpar tudo (stash clear)",
            "Voltar"
        ]
    ).ask()

    if not action or action == "Voltar":
        return

    if "Guardar" in action:
        msg = questionary.text("Nome/Mensagem para esse rascunho (opcional):").ask()
        success, out = service.stash_save(msg if msg else None)
        show_header("Stash", "Resultado")
        console.print(f"[green]{out}[/green]" if success else f"[red]Erro: {out}[/red]")
        
    elif "Recuperar" in action:
        success, out = service.stash_pop()
        show_header("Stash", "Resultado")
        console.print(f"[green]{out}[/green]" if success else f"[red]Erro: {out}[/red]")
        
    elif "Listar" in action:
        success, out = service.stash_list()
        show_header("Stash", "Itens Guardados")
        if out:
            console.print(f"[cyan]{out}[/cyan]")
        else:
            console.print("[yellow]O stash está vazio.[/yellow]")
        
    elif "Limpar" in action:
        if questionary.confirm("Tem certeza? Todos os stashes serão apagados permanentemente.").ask():
            success, out = service.stash_clear()
            show_header("Stash", "Resultado")
            console.print("[green]Stash limpo com sucesso![/green]" if success else f"[red]Erro: {out}[/red]")

    questionary.press_any_key_to_continue("\nPressione qualquer tecla para voltar...").ask()
