from rich.table import Table
import questionary

from gitflowy.theme import console
from gitflowy.services.git_service import GitService
from gitflowy.ui import show_header


def handle_tags(git_service: GitService = None):
    """Gerenciador de Tags (Releases)."""
    service = git_service or GitService()
    tags = service.get_tags()
    
    table = Table(title="Tags (Releases)", expand=True)
    table.add_column("Tag", style="cyan", no_wrap=True)
    table.add_column("Data de Criação", style="white")
    
    if tags:
        for t in tags:
            table.add_row(t["name"], t["date"])
    else:
        table.add_row("[dim]Nenhuma tag encontrada[/dim]", "")
        
    show_header("Gerenciador de Tags", "Crie, envie e apague tags de versão", custom_display=table)
    
    action = questionary.select(
        "O que deseja fazer com as Tags?",
        choices=[
            "Criar nova Tag",
            "Enviar Tags para o remoto (push --tags)",
            "Deletar uma Tag",
            "Voltar"
        ]
    ).ask()
    
    if not action or action == "Voltar":
        return
    
    if action == "Criar nova Tag":
        tag_name = questionary.text("Nome da Tag (ex: v1.0.0):").ask()
        if tag_name:
            tag_msg = questionary.text("Mensagem/Descrição da Tag (opcional):").ask()
            success, out = service.create_tag(tag_name, tag_msg if tag_msg else None)
            show_header("Gerenciador de Tags", "Resultado")
            if success:
                console.print(f"[bold green]Tag {tag_name} criada com sucesso no commit atual![/bold green]")
            else:
                console.print(f"[bold red]Erro ao criar Tag:[/bold red]\n{out}")
                
    elif action == "Enviar Tags para o remoto (push --tags)":
        remote_name = service.get_default_remote()
        with console.status(f"[bold cyan]Enviando tags para {remote_name}...[/bold cyan]", spinner="dots"):
            success, out = service.push_tags(remote_name)
        show_header("Gerenciador de Tags", "Resultado")
        if success:
            console.print("[bold green]Todas as Tags foram enviadas com sucesso![/bold green]")
        else:
            console.print(f"[bold red]Erro ao enviar Tags:[/bold red]\n{out}")
            
    elif action == "Deletar uma Tag":
        if not tags:
            console.print("[yellow]Não há tags para deletar.[/yellow]")
            questionary.press_any_key_to_continue("Pressione qualquer tecla para voltar...").ask()
            return
            
        target = questionary.select(
            "Qual Tag você deseja deletar?",
            choices=[t["name"] for t in tags] + ["Cancelar"]
        ).ask()
        
        if target and target != "Cancelar":
            if questionary.confirm(f"Tem certeza que deseja apagar a tag '{target}'?").ask():
                remote_name = service.get_default_remote()
                with console.status(f"[bold cyan]Apagando tag '{target}'...[/bold cyan]", spinner="dots"):
                    success, out = service.delete_tag(target, remote=remote_name)
                show_header("Gerenciador de Tags", "Resultado")
                if success:
                    console.print(f"[green]Tag '{target}' deletada com sucesso.[/green]")
                else:
                    console.print(f"[red]Erro ao deletar tag: {out}[/red]")
                    
    questionary.press_any_key_to_continue("\nPressione qualquer tecla para voltar...").ask()
