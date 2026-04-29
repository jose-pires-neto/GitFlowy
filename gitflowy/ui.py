from rich.table import Table
from rich.panel import Panel
from rich import box
from gitflowy.theme import console
from gitflowy.core import get_branches, get_changed_files, run_git

def show_header(view="HOME", subtitle="Mergulhando no código!"):
    """Mostra o cabeçalho dinâmico no estilo Dashboard Náutico."""
    console.clear()
    
    current_branch, _ = get_branches()
    changed_files = get_changed_files()
    
    logo = """        
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣿⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣠⣤⣀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⡏⢧⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⡒⠳⠍⠉⠢⡀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡿⠟⣓⣬⣷⣶⣶⣿⠛⠒⢒⣒⡶⠖⠃⠀⠀⠀⠀⠈⢣⡀⠀
⢀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⢴⣚⣋⠉⠉⡈⠽⣿⣿⣿⡟⠀⠀⠉⠀⠀⠘⠓⠲⢶⣄⠀⠀⠀⢹⠀
⠈⠻⢶⣤⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡀⠀⣀⣴⡞⠻⠿⡏⠉⠀⠀⠀⠠⠴⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠜⠿⣆⡀⠀⠘⣧
⠀⠀⠀⠙⢿⣿⣷⣦⣄⡀⠀⠀⢀⣠⣾⣿⣿⣿⣿⠾⠶⠾⠓⠒⠒⠚⠉⠉⠀⠀⠀⠀⠀⣀⣀⡠⠤⠴⠚⠉⠀⠀⠀⠀⠙⠛⠛⠋
⠀⠀⠀⠀⠀⠻⣿⣿⣿⣿⣶⣶⠿⢿⡿⠟⠋⣨⠁⠀⠀⠀⢀⣀⣀⡠⠤⠤⢤⣤⠖⠒⠀⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠈⣿⣿⣿⣿⠓⠒⢶⣶⠖⠛⠛⠦⣄⢠⠏⠉⠀⠀⠀⠀⠀⠀⠈⠳⡄⠀⣻⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢀⣴⡿⢟⠷⠃⠀⠀⠋⠁⠀⠀⠀⠀⠘⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣴⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠛⠙⠈⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠛⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
"""
    
    if view == "HOME":
        # Tela inicial com a Logo Grande
        left_info = f"{logo}\n[bold]{subtitle}[/bold]\n\n"
    else:
        # Display dinâmico (Substitui a logo pelas informações da ação atual)
        left_info = f"\n\n[bold cyan]🌊 MODO: {view.upper()}[/bold cyan]\n[dim]{subtitle}[/dim]"
        # Preenche com linhas em branco para manter a proporção do painel igual a da logo
        left_info += "\n" * 9 
        
    left_info += f"[dim]GitFlowy 0.2.0 • Terminal UI[/dim]\n"
    left_info += f"📍 /branch: [bold magenta]{current_branch if current_branch else 'Desconhecida'}[/bold magenta]\n"
    
    if changed_files:
        left_info += f"🌊 /status: [bold yellow]{len(changed_files)} arquivo(s) modificado(s)[/bold yellow]"
    else:
        left_info += "✨ /status: [dim]Árvore limpa[/dim]"
        
    # ATUALIZADO: Usando um delimitador mais seguro para evitar quebras se a mensagem tiver \t
    success, log_out = run_git(["log", "-n", "4", "--pretty=format:%ar<||>%s"])
    
    right_info = "[#00CED1]Atividade Recente[/#00CED1]\n"
    if success and log_out:
        for line in log_out.split('\n'):
            parts = line.split('<||>')
            if len(parts) == 2:
                time_ago, msg = parts
                right_info += f"[dim]{time_ago[:10]:<10} {msg[:45]}{'...' if len(msg)>45 else ''}[/dim]\n"
    else:
        right_info += "[dim]Nenhum commit recente encontrado.[/dim]\n"
        
    right_info += "\n[#00CED1]Status dos Arquivos[/#00CED1]\n"
    if changed_files:
        display_files = changed_files[:6]
        for f in display_files:
            status = f["status"]
            path = f["path"]
            
            if "M" in status or "R" in status:
                color, icon = "blue", "📝"
            elif "??" in status or "A" in status:
                color, icon = "green", "✨"
            elif "D" in status:
                color, icon = "red", "🗑️"
            else:
                color, icon = "yellow", "📌"

            if len(path) > 40:
                path = "..." + path[-37:]

            right_info += f"[{color}]{icon} {path}[/{color}]\n"

        if len(changed_files) > 6:
            right_info += f"[dim]... e mais {len(changed_files) - 6} arquivo(s). Vá em 'Status Completo'.[/dim]\n"
    else:
        right_info += "[dim]✨ Tudo sincronizado. Nenhuma modificação pendente.[/dim]\n"

    table = Table(show_header=False, expand=True, box=None, padding=(1, 2))
    table.add_column("Esquerda", justify="center", ratio=1)
    table.add_column("Direita", justify="left", ratio=1)
    table.add_row(left_info, right_info)

    panel = Panel(
        table,
        title="[dim] GitFlowy v0.2.0 [/dim]",
        title_align="left",
        box=box.ROUNDED,
        border_style="#00CED1",
        subtitle="[dim]Autor: José Pires O.N.[/dim]",
        subtitle_align="right"
    )
    
    console.print()
    console.print(panel)
    console.print("\n[dim]" + "─" * 80 + "[/dim]\n")
