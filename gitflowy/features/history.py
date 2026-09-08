from rich.table import Table
import questionary

from gitflowy.theme import console
from gitflowy.services.git_service import GitService
from gitflowy.ui import show_header


def handle_history(git_service: GitService = None):
    """Mostra o histórico recente de commits formatado dentro do header."""
    service = git_service or GitService()
    commits = service.get_recent_commits(limit=10)
    
    if not commits:
        show_header("Histórico (Log)", "Linha do tempo dos commits")
        console.print("[yellow]Nenhum histórico encontrado.[/yellow]")
        questionary.press_any_key_to_continue("Pressione qualquer tecla para voltar...").ask()
        return

    table = Table(title="Histórico Recente (Últimos 10 commits)", expand=True)
    table.add_column("Hash", style="cyan", no_wrap=True)
    table.add_column("Mensagem", style="white")
    table.add_column("Tempo", style="green")
    table.add_column("Autor", style="magenta")

    for c in commits:
        table.add_row(c["hash"], c["message"], c["time"], c["author"])
    
    show_header("Histórico (Log)", "Linha do tempo dos commits", custom_display=table)
    questionary.press_any_key_to_continue("\nPressione qualquer tecla para voltar...").ask()
