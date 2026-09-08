from rich.panel import Panel
import questionary

from gitflowy.theme import console
from gitflowy.services.git_service import GitService
from gitflowy.ui import show_header


def handle_commit(git_service: GitService = None):
    """Fluxo guiado de Conventional Commits."""
    service = git_service or GitService()
    show_header("Fazer Commit", "Adicione e descreva suas alterações")
    changed_files = service.get_status()
    
    if not changed_files:
        console.print("[bold green]A árvore de trabalho está limpa![/bold green] Nenhum arquivo para commitar.")
        questionary.press_any_key_to_continue("Pressione qualquer tecla para voltar...").ask()
        return

    add_mode = questionary.select(
        "Como deseja adicionar os arquivos?",
        choices=[
            "Adicionar todos os arquivos (git add .)",
            "Selecionar arquivos manualmente",
            "Cancelar"
        ]
    ).ask()

    if add_mode == "Cancelar" or not add_mode:
        return

    selected_files = []
    if "todos" in add_mode:
        selected_files = ["."]
    else:
        file_choices = [f["path"] for f in changed_files]
        selected_files = questionary.checkbox(
            "Selecione os arquivos para o commit:",
            choices=file_choices
        ).ask()

        if not selected_files:
            console.print("[yellow]Nenhum arquivo selecionado.[/yellow]")
            questionary.press_any_key_to_continue("Pressione qualquer tecla para voltar...").ask()
            return

    # Limpa a tela antes de solicitar a mensagem para evitar acúmulo visual
    show_header("Fazer Commit", "Defina o tipo e a mensagem do commit")

    commit_type = questionary.select(
        "Qual é o tipo da sua alteração (Conventional Commits)?",
        choices=[
            "feat:     Nova funcionalidade",
            "fix:      Correção de bug",
            "docs:     Documentação",
            "style:    Formatação ou estilo de código",
            "refactor: Refatoração de código",
            "test:     Testes automatizados",
            "chore:    Manutenção e dependências"
        ]
    ).ask()

    if not commit_type:
        return
    commit_tag = commit_type.split(":")[0]

    commit_scope = questionary.text("Qual o escopo? (Opcional, ex: auth, ui):").ask()
    commit_message = questionary.text("Descreva a alteração:").ask()

    if not commit_message:
        console.print("[bold red]A mensagem é obrigatória.[/bold red]")
        questionary.press_any_key_to_continue("Pressione qualquer tecla para voltar...").ask()
        return

    scope_str = f"({commit_scope})" if commit_scope else ""
    final_message = f"{commit_tag}{scope_str}: {commit_message}"

    console.print(f"\n[dim]Mensagem formatada:[/dim] [bold white]{final_message}[/bold white]")
    if not questionary.confirm("Confirmar commit?").ask():
        return

    with console.status("[bold cyan]Executando commit...[/bold cyan]", spinner="dots"):
        success, err = service.commit(final_message, files=selected_files)

    show_header("Fazer Commit", "Resultado da operação")
    if success:
        console.print(Panel("[bold green]Commit realizado com sucesso![/bold green]", expand=False, border_style="green"))
    else:
        console.print(f"[bold red]Erro ao commitar:[/bold red]\n{err}")
    
    questionary.press_any_key_to_continue("\nPressione qualquer tecla para voltar ao menu...").ask()
