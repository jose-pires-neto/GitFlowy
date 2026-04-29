import sys
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.console import Group
from rich import box
from gitflowy.theme import console
from gitflowy.core import get_branches, get_changed_files, run_git

# Tenta importar msvcrt (Windows) para o menu grid interativo
try:
    import msvcrt
    HAS_MSVCRT = True
except ImportError:
    HAS_MSVCRT = False


def show_header(view="HOME", subtitle="Mergulhando no código!", custom_display=None, return_panel=False):
    """Mostra o cabeçalho dinâmico no estilo Dashboard Náutico.
    Se custom_display for fornecido, ele ocupa todo o espaço do painel.
    """
    if not return_panel:
        console.clear()
    
    current_branch, _ = get_branches()
    changed_files = get_changed_files()
    
    if custom_display is not None:
        # Modo Full-Width Display
        panel_content = custom_display
    else:
        # Modo Padrão Split (Esquerda e Direita)
        logo = """        
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣴⣶⠾⠿⠿⠯⣷⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣼⣾⠛⠁⠀⠀⠀⠀⠀⠀⠈⢻⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣾⠿⠁⠀⠀⠀⢀⣤⣾⣟⣛⣛⣶⣬⣿⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣾⠟⠃⠀⠀⠀⠀⠀⣾⣿⠟⠉⠉⠉⠉⠛⠿⠟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⡟⠋⠀⠀⠀⠀⠀⠀⠀⣿⡏⣤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣠⡿⠛⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⣷⡍⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⣤⣤⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣠⣼⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠷⣤⣤⣠⣤⣤⡤⡶⣶⢿⠟⠹⠿⠄⣿⣿⠏⠀⣀⣤⡦⠀⠀⠀⠀⣀⡄
⢀⣄⣠⣶⣿⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠓⠚⠋⠉⠀⠀⠀⠀⠀⠀⠈⠛⡛⡻⠿⠿⠙⠓⢒⣺⡿⠋⠁
⠉⠉⠉⠛⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
"""
        
        if view == "HOME":
            # Tela inicial com a Logo Grande
            left_info = f"{logo}\n[bold]{subtitle}[/bold]\n\n"
        else:
            # Display dinâmico (Substitui a logo pelas informações da ação atual)
            left_info = f"\n\n[bold cyan]🌊 MODO: {view.upper()}[/bold cyan]\n[dim]{subtitle}[/dim]"
            left_info += "\n" * 9 
            
        left_info += f"[dim]GitFlowy 0.2.0 • Terminal UI[/dim]\n"
        left_info += f"📍 /branch: [bold magenta]{current_branch if current_branch else 'Desconhecida'}[/bold magenta]\n"
        
        if changed_files:
            left_info += f"🌊 /status: [bold yellow]{len(changed_files)} arquivo(s) modificado(s)[/bold yellow]"
        else:
            left_info += "✨ /status: [dim]Árvore limpa[/dim]"
            
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
        panel_content = table

    panel = Panel(
        panel_content,
        title="[dim] GitFlowy v0.2.0 [/dim]",
        title_align="left",
        box=box.ROUNDED,
        border_style="#00CED1",
        subtitle="[dim]Autor: José Pires O.N.[/dim]",
        subtitle_align="right"
    )
    
    if return_panel:
        return panel
        
    console.print()
    console.print(panel)


def grid_menu(options, cols=3):
    """
    Renders an interactive 2D grid menu using arrow keys.
    Retorna o item selecionado.
    """
    # Se não estiver no Windows (sem msvcrt), faz fallback para questionary list
    if not HAS_MSVCRT:
        import questionary
        show_header(view="HOME", subtitle="Mergulhando no código!")
        return questionary.select(
            "Execute uma ação (Modo Grid não suportado no Linux/Mac nativo):",
            choices=options
        ).ask()

    selected = 0
    
    def generate_layout(sel):
        header = show_header(view="HOME", subtitle="Mergulhando no código!", return_panel=True)
        
        table = Table(show_header=False, expand=True, box=None, padding=(1, 2))
        for _ in range(cols):
            table.add_column(justify="center", ratio=1)
            
        for i in range(0, len(options), cols):
            row = []
            for j in range(cols):
                idx = i + j
                if idx < len(options):
                    item = options[idx]
                    if idx == sel:
                        row.append(f"[bold cyan on #1a1a1a] > {item} < [/bold cyan on #1a1a1a]")
                    else:
                        row.append(f"[dim]   {item}   [/dim]")
                else:
                    row.append("")
            table.add_row(*row)
            
        grid = Panel(table, title="[cyan]Selecione uma ação (Setas para navegar, Enter para confirmar)[/cyan]", border_style="cyan", box=box.SQUARE)
        return Group(header, grid)

    # console.clear() limpa a tela ANTES de iniciar a sessão interativa (Live)
    console.clear()
    
    # Live se encarrega de atualizar sem "piscar" e sem imprimir várias linhas seguidas
    with Live(generate_layout(selected), console=console, auto_refresh=False, screen=False) as live:
        while True:
            key = msvcrt.getch()
            
            if key == b'\xe0': # Setas Especiais no Windows
                key = msvcrt.getch()
                if key == b'H': # Up
                    if selected >= cols: selected -= cols
                elif key == b'P': # Down
                    if selected + cols < len(options): selected += cols
                elif key == b'K': # Left
                    if selected % cols > 0: selected -= 1
                elif key == b'M': # Right
                    if selected % cols < cols - 1 and selected + 1 < len(options): selected += 1
            elif key in (b'\r', b'\n'): # Enter
                return options[selected]
            elif key == b'\x03': # Ctrl+C
                raise KeyboardInterrupt
                
            # Atualiza o display sem poluir
            live.update(generate_layout(selected), refresh=True)

