import sys
import questionary
from gitflowy.theme import console
from gitflowy.core import is_git_repo
from gitflowy.ui import interactive_menu
from gitflowy.handlers import (
    handle_status, handle_commit, handle_branches,
    handle_sync, handle_history, handle_stash, handle_undo, handle_tags,
    handle_pull_requests
)

def main():
    if not is_git_repo():
        console.print("[bold red]Erro: Esta pasta não é um repositório Git válido.[/bold red]")
        console.print("Navegue até um projeto Git ou inicialize com: [yellow]git init[/yellow]")
        sys.exit(1)

    menu_choices = [
        questionary.Separator("── Operações ──────────────────────────"),
        "Fazer Commit",
        "Status Completo",
        "Sincronização (Push / Pull)",
        questionary.Separator("── Repositório ────────────────────────"),
        "Branches",
        "Histórico de Commits",
        "Tags (Releases)",
        "Stash (Alterações Temporárias)",
        "Pull Requests (GitHub)",
        questionary.Separator("── Manutenção ─────────────────────────"),
        "Desfazer / Reverter",
        questionary.Separator("───────────────────────────────────────"),
        "Sair"
    ]

    while True:
        choice = interactive_menu(menu_choices, prompt="O que deseja fazer no repositório?")

        if choice == "Fazer Commit":
            handle_commit()
        elif choice == "Status Completo":
            handle_status()
        elif choice == "Sincronização (Push / Pull)":
            handle_sync()
        elif choice == "Branches":
            handle_branches()
        elif choice == "Histórico de Commits":
            handle_history()
        elif choice == "Tags (Releases)":
            handle_tags()
        elif choice == "Stash (Alterações Temporárias)":
            handle_stash()
        elif choice == "Desfazer / Reverter":
            handle_undo()
        elif choice == "Pull Requests (GitHub)":
            handle_pull_requests()
        elif choice == "Sair" or not choice:
            console.print("\n[dim]Sessão encerrada.[/dim]")
            break
