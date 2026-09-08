from rich.table import Table
import questionary

from gitflowy.theme import console
from gitflowy.services.git_service import GitService
from gitflowy.ui import show_header


def handle_undo(git_service: GitService = None):
    """Ferramentas para desfazer ações (Reset, Restore, Revert)."""
    service = git_service or GitService()
    default_undo_table = Table(title="Opções de Reversão", expand=True)
    default_undo_table.add_column("Ação", style="bold cyan")
    default_undo_table.add_column("Descrição", style="white")
    default_undo_table.add_row("Desfazer Último Commit", "Apaga o commit mas preserva os arquivos modificados (Seguro)")
    default_undo_table.add_row("Reverter Commit", "Cria um commit reverso anulando uma alteração específica")
    default_undo_table.add_row("Descartar Alterações", "Descarta todas as alterações não commitadas (Irreversível)")
    
    show_header("Desfazer / Reverter", "Ações de reversão de histórico", custom_display=default_undo_table)
    
    action = questionary.select(
        "O que você deseja desfazer?",
        choices=[
            "Desfazer último commit (mantendo arquivos)",
            "Reverter commit específico (git revert)",
            "Descartar todas as alterações não commitadas",
            "Voltar"
        ]
    ).ask()

    if not action or action == "Voltar":
        return

    if action == "Desfazer último commit (mantendo arquivos)":
        if questionary.confirm("Isso vai apagar o último commit do histórico, mas seus arquivos continuarão modificados. Continuar?").ask():
            success, out = service.soft_reset("HEAD~1")
            show_header("Desfazer / Reverter", "Resultado")
            console.print("[green]Último commit desfeito! Arquivos mantidos na sua máquina.[/green]" if success else f"[red]Erro: {out}[/red]")
            
    elif action == "Reverter commit específico (git revert)":
        commits_data = service.get_recent_commits(limit=15)
        if not commits_data:
            console.print("[yellow]Nenhum histórico encontrado para reverter.[/yellow]")
            questionary.press_any_key_to_continue("Pressione qualquer tecla para voltar...").ask()
            return
            
        table = Table(title="Últimos 15 Commits (Revert)", expand=True)
        table.add_column("Hash", style="cyan", no_wrap=True)
        table.add_column("Mensagem", style="white")
        table.add_column("Tempo", style="green")

        choices = []
        for c in commits_data:
            choices.append(questionary.Choice(title=f"{c['hash']} - {c['message'][:50]}", value=c["hash"]))
            table.add_row(c["hash"], c["message"][:40] + ("..." if len(c["message"]) > 40 else ""), c["time"])
                
        show_header("Desfazer / Reverter", "Selecione o commit para reverter", custom_display=table)
        
        target_commit = questionary.select(
            "Qual commit você deseja reverter?",
            choices=choices + [questionary.Choice(title="Cancelar", value=None)]
        ).ask()
        
        if not target_commit:
            return
            
        with console.status(f"[bold cyan]Revertendo commit {target_commit}...[/bold cyan]", spinner="dots"):
            success, out = service.revert(target_commit)
            
        show_header("Desfazer / Reverter", "Resultado do Revert")
        if success:
            console.print(f"[bold green]Commit {target_commit} revertido com sucesso![/bold green]")
        else:
            console.print(f"[bold red]Conflito ao reverter o commit {target_commit}:[/bold red]")
            console.print("[yellow]Você precisará resolver os conflitos manualmente e concluir o commit.[/yellow]")

    elif action == "Descartar todas as alterações não commitadas":
        if questionary.confirm("PERIGO: Isso apagará todas as modificações não commitadas de forma IRREVERSÍVEL. Continuar?").ask():
            success, msg = service.discard_all_changes()
            show_header("Desfazer / Reverter", "Resultado")
            if success:
                console.print("[green]Árvore de trabalho limpa. Todas as alterações locais foram descartadas.[/green]")
            else:
                console.print(f"[red]Erro ao limpar:\n{msg}[/red]")

    questionary.press_any_key_to_continue("\nPressione qualquer tecla para voltar...").ask()
