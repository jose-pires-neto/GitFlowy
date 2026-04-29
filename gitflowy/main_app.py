import sys
import questionary
from gitflowy.theme import console
from gitflowy.core import is_git_repo
from gitflowy.ui import show_header
from gitflowy.handlers import (
    handle_status, handle_commit, handle_branches,
    handle_sync, handle_history, handle_stash, handle_undo
)

def main():
    if not is_git_repo():
        console.print("[bold red]❌ Esta pasta não é um repositório Git.[/bold red]")
        console.print("Rode [yellow]git init[/yellow] primeiro!")
        sys.exit(1)

    while True:
        # A tela de início carrega a logo no painel padrão
        show_header(view="HOME", subtitle="Mergulhando no código!")
        
        choice = questionary.select(
            "Execute uma ação:",
            choices=[
                "📊 Status Completo (Ver arquivos)",
                "📝 Fazer Commit",
                "🌿 Gerenciar Branches",
                "🔄 Sincronizar (Push/Pull)",
                "📜 Ver Histórico (Log)",
                "📦 Guarda-volumes (Stash)",
                "↩️  Desfazer / Reverter",
                "🚪 Sair"
            ]
        ).ask()

        if choice == "📊 Status Completo (Ver arquivos)":
            handle_status()
        elif choice == "📝 Fazer Commit":
            handle_commit()
        elif choice == "🌿 Gerenciar Branches":
            handle_branches()
        elif choice == "🔄 Sincronizar (Push/Pull)":
            handle_sync()
        elif choice == "📜 Ver Histórico (Log)":
            handle_history()
        elif choice == "📦 Guarda-volumes (Stash)":
            handle_stash()
        elif choice == "↩️  Desfazer / Reverter":
            handle_undo()
        elif choice == "🚪 Sair" or not choice:
            console.print("\n[dim]Até logo! Continue mergulhando no código. 🌊[/dim]")
            break
