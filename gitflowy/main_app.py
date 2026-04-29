import sys
import questionary
from gitflowy.theme import console
from gitflowy.core import is_git_repo
from gitflowy.ui import show_header, grid_menu
from gitflowy.handlers import (
    handle_status, handle_commit, handle_branches,
    handle_sync, handle_history, handle_stash, handle_undo, handle_tags
)

def main():
    if not is_git_repo():
        console.print("[bold red]❌ Esta pasta não é um repositório Git.[/bold red]")
        console.print("Rode [yellow]git init[/yellow] primeiro!")
        sys.exit(1)

    # Organização das opções na ordem de uso para formar o Grid 3x3 perfeito
    options = [
        "📝 Fazer Commit",
        "📊 Status Completo",
        "🔄 Sync (Push/Pull)",
        "🌿 Branches",
        "📜 Histórico (Log)",
        "🏷️  Tags (Releases)",
        "📦 Stash (Guarda)",
        "↩️  Reverter",
        "🚪 Sair"
    ]

    while True:
        # A tela de início carrega a logo no painel padrão e agora exibe o grid interativo
        choice = grid_menu(options, cols=3)

        if choice == "📊 Status Completo":
            handle_status()
        elif choice == "📝 Fazer Commit":
            handle_commit()
        elif choice == "🌿 Branches":
            handle_branches()
        elif choice == "🔄 Sync (Push/Pull)":
            handle_sync()
        elif choice == "📜 Histórico (Log)":
            handle_history()
        elif choice == "🏷️  Tags (Releases)":
            handle_tags()
        elif choice == "📦 Stash (Guarda)":
            handle_stash()
        elif choice == "↩️  Reverter":
            handle_undo()
        elif choice == "🚪 Sair" or not choice:
            console.print("\n[dim]Até logo! Continue mergulhando no código. 🌊[/dim]")
            break
