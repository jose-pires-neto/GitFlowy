import os
from rich.table import Table
from rich import box
import questionary

from gitflowy.theme import console
from gitflowy.services.git_service import GitService
from gitflowy.ui import show_header


def handle_status(git_service: GitService = None):
    """Exibe um status detalhado e organizado de todos os arquivos modificados."""
    service = git_service or GitService()
    files = service.get_status()
    
    if not files:
        show_header("Status Completo", "Visão detalhada de todas as alterações")
        console.print("[bold green]A árvore de trabalho está limpa![/bold green] Nenhuma modificação pendente.")
        questionary.press_any_key_to_continue("Pressione qualquer tecla para voltar...").ask()
        return

    table = Table(title="Arquivos Modificados (Status)", expand=True, box=box.ROUNDED)
    table.add_column("Estado", justify="center", style="bold", width=18)
    table.add_column("Diretório", style="cyan")
    table.add_column("Arquivo", style="white")

    for f in files:
        status = f["status"]
        path = f["path"]
        raw_path = f["raw_path"]
        
        color = "white"
        estado = status.strip()
        
        if "??" in status:
            estado, color = "Untracked", "green"
        elif "A" in status:
            estado, color = "Adicionado", "green"
        elif "M" in status:
            estado, color = "Modificado", "blue"
        elif "D" in status:
            estado, color = "Deletado", "red"
        elif "R" in status:
            estado, color = "Renomeado", "magenta"
        
        dir_name = os.path.dirname(path)
        file_name = os.path.basename(path)
        
        if not dir_name:
            dir_name = "/"
        else:
            dir_name = f"/{dir_name}/"
            
        if "R" in status:
            file_name = raw_path
            dir_name = "-> "
        
        table.add_row(f"[{color}]{estado}[/{color}]", f"[dim]{dir_name}[/dim]", f"[{color}]{file_name}[/{color}]")
    
    show_header("Status Completo", f"Total: {len(files)} arquivo(s) modificado(s)", custom_display=table)
    
    action = questionary.select(
        "O que deseja fazer?",
        choices=["Prosseguir para Commit", "Voltar ao Menu Principal"]
    ).ask()
    
    if action == "Prosseguir para Commit":
        from gitflowy.features.commit import handle_commit
        handle_commit(service)
