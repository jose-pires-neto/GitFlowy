import os
import sys
from rich.table import Table
from rich.panel import Panel
from rich import box
import questionary

from gitflowy import __version__
from gitflowy.theme import console
from gitflowy.core import get_branches, get_changed_files, run_git


def clear_screen():
    """Limpa a tela visível e o buffer de scrollback do terminal de forma consistente."""
    if os.name == "nt":
        os.system("cls")
    else:
        # \033[H posiciona o cursor no início
        # \033[2J limpa a viewport visível
        # \033[3J limpa o buffer de scrollback (macOS Terminal, iTerm2, xterm, etc.)
        sys.stdout.write("\033[H\033[2J\033[3J")
        sys.stdout.flush()


def show_header(view="HOME", subtitle="Mergulhando no código!", custom_display=None, return_panel=False):
    """Mostra o cabeçalho dinâmico no estilo Dashboard Náutico.
    Se custom_display for fornecido, ele ocupa todo o espaço do painel.
    """
    if not return_panel:
        clear_screen()
    
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
            left_info = f"\n\n[bold cyan]MODO: {view.upper()}[/bold cyan]\n[dim]{subtitle}[/dim]"
            left_info += "\n" * 9 
            
        left_info += f"[dim]GitFlowy v{__version__} • Terminal UI[/dim]\n"
        left_info += f"Branch: [bold magenta]{current_branch if current_branch else 'Desconhecida'}[/bold magenta]\n"
        
        if changed_files:
            left_info += f"Status: [bold yellow]{len(changed_files)} arquivo(s) modificado(s)[/bold yellow]"
        else:
            left_info += "Status: [dim]Árvore limpa[/dim]"
            
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
                    color, tag = "blue", "[M]"
                elif "??" in status or "A" in status:
                    color, tag = "green", "[+]"
                elif "D" in status:
                    color, tag = "red", "[-]"
                else:
                    color, tag = "yellow", "[?]"

                if len(path) > 38:
                    path = "..." + path[-35:]

                right_info += f"[{color}]{tag:<4} {path}[/{color}]\n"

            if len(changed_files) > 6:
                right_info += f"[dim]... e mais {len(changed_files) - 6} arquivo(s). Vá em 'Status Completo'.[/dim]\n"
        else:
            right_info += "[dim]Tudo sincronizado. Nenhuma modificação pendente.[/dim]\n"

        table = Table(show_header=False, expand=True, box=None, padding=(1, 2))
        table.add_column("Esquerda", justify="center", ratio=1)
        table.add_column("Direita", justify="left", ratio=1)
        table.add_row(left_info, right_info)
        panel_content = table

    panel = Panel(
        panel_content,
        title=f"[dim] GitFlowy v{__version__} [/dim]",
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


def interactive_menu(choices, prompt="O que deseja fazer no repositório?"):
    """
    Limpa a tela, exibe o cabeçalho e renderiza o menu de seleção interativo.
    Retorna o item selecionado.
    """
    show_header(view="HOME", subtitle="Mergulhando no código!")
    return questionary.select(
        prompt,
        choices=choices,
        use_shortcuts=False
    ).ask()
