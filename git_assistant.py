import os
import subprocess
import sys

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.table import Table
    from rich import box
    import questionary
except ImportError:
    print("⚠️  Dependências ausentes! Para a interface bonita, instale:")
    print("👉 pip install rich questionary")
    sys.exit(1)

console = Console()

# --- TEMA OCEAN (Estilo Global - GitFlowy) ---
custom_style = questionary.Style([
    ('qmark', 'fg:#00CED1 bold'),       # Marca > ciano
    ('question', 'bold default'),       # Texto da pergunta
    ('answer', 'fg:#00BFFF bold'),      # Resposta preenchida
    ('pointer', 'fg:#00CED1 bold'),     # Seta de navegação ciano
    ('highlighted', 'fg:#00BFFF bold'), # Item atual na lista
    ('selected', 'fg:#48D1CC bold'),    # Item de checkbox marcado
    ('instruction', 'fg:#858585'),      # Dicas (cinza)
])

# Aplicando o tema e o marcador '>' em todos os prompts automaticamente (Monkey Patch)
def apply_theme_with_qmark(func):
    def wrapper(*args, **kwargs):
        kwargs['style'] = custom_style
        kwargs.setdefault('qmark', '>')
        return func(*args, **kwargs)
    return wrapper

def apply_theme_only(func):
    def wrapper(*args, **kwargs):
        kwargs['style'] = custom_style
        return func(*args, **kwargs)
    return wrapper

questionary.select = apply_theme_with_qmark(questionary.select)
questionary.checkbox = apply_theme_with_qmark(questionary.checkbox)
questionary.text = apply_theme_with_qmark(questionary.text)
questionary.confirm = apply_theme_with_qmark(questionary.confirm)
# CORREÇÃO 1: press_any_key não recebe qmark, recebe apenas o estilo visual.
questionary.press_any_key_to_continue = apply_theme_only(questionary.press_any_key_to_continue)
# ----------------------------------------

def run_git(args, exit_on_error=False):
    """Executa um comando git de forma silenciosa. Retorna (sucesso, output_ou_erro)."""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            encoding='utf-8', # CORREÇÃO 3: Previne quebra de encoding no Windows
            errors='replace',
            check=True
        )
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else (e.stdout.strip() if e.stdout else str(e))
        if exit_on_error:
            console.print(f"[bold red]Erro crítico no Git:[/bold red] {error_msg}")
            sys.exit(1)
        return False, error_msg

def is_git_repo():
    """Verifica se a pasta atual é um repositório Git."""
    return os.path.isdir(".git") or run_git(["rev-parse", "--is-inside-work-tree"])[0]

def get_changed_files():
    """Obtém a lista de arquivos modificados, adicionados ou deletados."""
    # CORREÇÃO 2: Evita que o Git coloque aspas em arquivos com caracteres especiais (ç, acentos)
    success, output = run_git(["-c", "core.quotePath=false", "status", "--porcelain"])
    if not success or not output:
        return []
    
    files = []
    for line in output.split("\n"):
        if len(line) > 2:
            status = line[:2]
            file_path = line[3:]
            files.append(f"{status} {file_path}")
    return files

def get_branches():
    """Retorna a branch atual e uma lista de todas as branches locais."""
    success, output = run_git(["branch", "--format=%(refname:short)"])
    if not success: return "", []
    
    branches = output.split("\n")
    
    success, current = run_git(["branch", "--show-current"])
    current_branch = current if success else ""
    
    return current_branch, [b for b in branches if b]

def show_header():
    """Mostra o cabeçalho no estilo Dashboard Náutico."""
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
    
    left_info = f"{logo}\n[bold]Mergulhando no código![/bold]\n\n"
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
            status = f[:2]
            path = f[3:]
            
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
            right_info += f"[dim]... e mais {len(changed_files) - 6} arquivo(s) modificado(s).[/dim]\n"
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


def handle_commit():
    """Fluxo de commit (Adicionar Tudo vs Selecionar)"""
    changed_files = get_changed_files()
    
    if not changed_files:
        console.print("🌿 [bold green]A árvore de trabalho está limpa![/bold green] Nenhum arquivo para commitar.")
        questionary.press_any_key_to_continue("Pressione qualquer tecla para voltar...").ask()
        return

    add_mode = questionary.select(
        "Como deseja adicionar os arquivos?",
        choices=[
            "🚀 Adicionar TUDO (git add .)",
            "🎯 Selecionar arquivos manualmente",
            "❌ Cancelar"
        ]
    ).ask()

    if add_mode == "❌ Cancelar" or not add_mode:
        return

    selected_files = []
    if "TUDO" in add_mode:
        selected_files = ["."]
    else:
        file_choices = [f[3:] for f in changed_files]
        selected_files = questionary.checkbox(
            "Selecione os arquivos para o commit:",
            choices=file_choices,
            style=questionary.Style([('highlighted', 'fg:#00CED1 bold')])
        ).ask()

        if not selected_files:
            console.print("[yellow]Nenhum arquivo selecionado.[/yellow]")
            return

    commit_type = questionary.select(
        "Qual é o tipo da sua alteração?",
        choices=[
            "feat:     ✨ Nova funcionalidade",
            "fix:      🐛 Correção de bug",
            "docs:     📚 Apenas documentação",
            "style:    💎 Formatação, pontuação",
            "refactor: ♻️  Refatoração",
            "test:     🚨 Testes",
            "chore:    🔧 Manutenção, dependências"
        ]
    ).ask()

    if not commit_type: return
    commit_tag = commit_type.split(":")[0]

    commit_scope = questionary.text("Qual o escopo? (Opcional, ex: auth, ui):").ask()
    commit_message = questionary.text("Descreva a alteração:").ask()

    if not commit_message:
        console.print("[bold red]❌ A mensagem é obrigatória.[/bold red]")
        questionary.press_any_key_to_continue("Pressione qualquer tecla para voltar...").ask()
        return

    scope_str = f"({commit_scope})" if commit_scope else ""
    final_message = f"{commit_tag}{scope_str}: {commit_message}"

    console.print(f"\n[dim]Mensagem gerada:[/dim] [bold white]{final_message}[/bold white]")
    if not questionary.confirm("Confirmar commit?").ask():
        return

    with console.status("[bold cyan]Commitando...[/bold cyan]", spinner="dots"):
        if selected_files == ["."]:
            run_git(["add", "."])
        else:
            # Ao invés de loop for lento, passa a lista toda pro subprocess
            run_git(["add", "--"] + selected_files)
        
        success, err = run_git(["commit", "-m", final_message])

    if success:
        console.print(Panel("🚀 [bold green]Commit realizado com sucesso![/bold green]", expand=False, border_style="green"))
    else:
        console.print(f"[bold red]Erro ao commitar:[/bold red]\n{err}")
    
    questionary.press_any_key_to_continue("\nPressione qualquer tecla para voltar ao menu...").ask()

def handle_branches():
    """Gerenciador de Branches visual"""
    current_branch, branches = get_branches()
    
    action = questionary.select(
        "Gerenciar Branches - O que deseja fazer?",
        choices=[
            "🔄 Trocar de Branch",
            "🌱 Criar Nova Branch",
            "🗑️  Deletar Branch",
            "Voltar"
        ]
    ).ask()

    if not action or action == "Voltar":
        return

    if "Trocar" in action:
        options = [b for b in branches if b != current_branch]
        if not options:
            console.print("[yellow]Não há outras branches para trocar.[/yellow]")
            questionary.press_any_key_to_continue("Pressione qualquer tecla para voltar...").ask()
            return
            
        target = questionary.select("Para qual branch deseja mudar?", choices=options).ask()
        if target:
            success, msg = run_git(["checkout", target])
            console.print(f"[green]Mudou para a branch '{target}'[/green]" if success else f"\n[red]Erro:\n{msg}[/red]")
            questionary.press_any_key_to_continue("Pressione qualquer tecla para voltar...").ask()

    elif "Criar" in action:
        new_branch = questionary.text("Nome da nova branch:").ask()
        if new_branch:
            success, msg = run_git(["checkout", "-b", new_branch])
            console.print(f"[green]Branch '{new_branch}' criada e ativada![/green]" if success else f"[red]Erro: {msg}[/red]")
            questionary.press_any_key_to_continue("Pressione qualquer tecla para voltar...").ask()
            
    elif "Deletar" in action:
        options = [b for b in branches if b != current_branch and b not in ["main", "master"]]
        if not options:
            console.print("[yellow]Não há branches seguras para deletar (não é possível deletar a branch atual ou main/master).[/yellow]")
            questionary.press_any_key_to_continue("Pressione qualquer tecla para voltar...").ask()
            return
            
        target = questionary.select("Qual branch deseja deletar?", choices=options).ask()
        if target and questionary.confirm(f"Tem certeza que deseja deletar '{target}'?").ask():
            success, msg = run_git(["branch", "-D", target])
            console.print(f"[green]Branch '{target}' deletada![/green]" if success else f"[red]Erro: {msg}[/red]")
            questionary.press_any_key_to_continue("Pressione qualquer tecla para voltar...").ask()

def handle_sync():
    """Faz Push e Pull do repositório"""
    action = questionary.select(
        "Sincronização",
        choices=["⬆️  Push (Enviar alterações)", "⬇️  Pull (Puxar alterações)", "Voltar"]
    ).ask()
    
    if not action or action == "Voltar": return
    
    current_branch, _ = get_branches()
    
    if "Push" in action:
        with console.status(f"[bold cyan]Enviando branch {current_branch} para o remote...[/bold cyan]"):
            success, msg = run_git(["push"])
            if not success and "set-upstream" in msg:
                success, msg = run_git(["push", "--set-upstream", "origin", current_branch])
        
        if success:
            console.print("[bold green]✅ Push realizado com sucesso![/bold green]")
        else:
            console.print(f"[bold red]❌ Erro no Push:[/bold red]\n{msg}")
            
    elif "Pull" in action:
         with console.status(f"[bold cyan]Puxando alterações em {current_branch}...[/bold cyan]"):
            success, msg = run_git(["pull"])
            if success:
                console.print("[bold green]✅ Pull realizado com sucesso![/bold green]")
            else:
                console.print(f"[bold red]❌ Erro no Pull:[/bold red]\n{msg}")
                
    questionary.press_any_key_to_continue("\nPressione qualquer tecla para voltar...").ask()


def handle_history():
    """Mostra o histórico recente de commits em uma tabela bonita."""
    # CORREÇÃO: Usando um delimitador complexo '<||>' pois um commit pode possuir '|' no título
    success, output = run_git(["log", "-n", "10", "--pretty=format:%h<||>%s<||>%ar<||>%an"])
    if not success or not output:
        console.print("[yellow]Nenhum histórico encontrado.[/yellow]")
        questionary.press_any_key_to_continue("Pressione qualquer tecla para voltar...").ask()
        return

    table = Table(title="Histórico Recente (Últimos 10 commits)")
    table.add_column("Hash", style="cyan", no_wrap=True)
    table.add_column("Mensagem", style="white")
    table.add_column("Tempo", style="green")
    table.add_column("Autor", style="magenta")

    for line in output.split("\n"):
        parts = line.split("<||>")
        if len(parts) == 4:
            table.add_row(parts[0], parts[1], parts[2], parts[3])
    
    console.print(table)
    questionary.press_any_key_to_continue("\nPressione qualquer tecla para voltar...").ask()


def handle_stash():
    """Gerencia o stash (área de rascunho)."""
    action = questionary.select(
        "Guarda-volumes (Stash)",
        choices=[
            "📦 Guardar alterações (Stash Save)",
            "📥 Recuperar últimas alterações (Stash Pop)",
            "📋 Listar itens guardados",
            "🗑️  Limpar tudo (Stash Clear)",
            "Voltar"
        ]
    ).ask()

    if not action or action == "Voltar": return

    if "Guardar" in action:
        msg = questionary.text("Nome/Mensagem para esse rascunho (opcional):").ask()
        args = ["stash", "push", "-m", msg] if msg else ["stash"]
        success, out = run_git(args)
        console.print(f"[green]{out}[/green]" if success else f"[red]Erro: {out}[/red]")
        
    elif "Recuperar" in action:
        success, out = run_git(["stash", "pop"])
        console.print(f"[green]{out}[/green]" if success else f"[red]Erro: {out}[/red]")
        
    elif "Listar" in action:
        success, out = run_git(["stash", "list"])
        if out: console.print(f"[cyan]{out}[/cyan]")
        else: console.print("[yellow]Guarda-volumes está vazio.[/yellow]")
        
    elif "Limpar" in action:
        if questionary.confirm("Tem certeza? Isso apagará todos os stashes!").ask():
            success, out = run_git(["stash", "clear"])
            console.print("[green]Stash limpo com sucesso![/green]" if success else f"[red]Erro: {out}[/red]")

    questionary.press_any_key_to_continue("\nPressione qualquer tecla para voltar...").ask()


def handle_undo():
    """Ferramentas para desfazer ações (Reset, Restore)."""
    action = questionary.select(
        "O que você deseja desfazer?",
        choices=[
            "↩️  Desfazer último commit (Mantendo os arquivos)",
            "🔥 Descartar TODAS as alterações não commitadas",
            "Voltar"
        ]
    ).ask()

    if not action or action == "Voltar": return

    if "Desfazer último commit" in action:
        if questionary.confirm("Isso vai apagar o último commit do histórico, mas seus arquivos continuarão modificados. Continuar?").ask():
            success, out = run_git(["reset", "--soft", "HEAD~1"])
            console.print("[green]Último commit desfeito! Arquivos mantidos na sua máquina.[/green]" if success else f"[red]Erro: {out}[/red]")
    elif "Descartar TODAS" in action:
        if questionary.confirm("PERIGO: Isso apagará todas as modificações atuais de forma IRREVERSÍVEL. Continuar?").ask():
            success1, out1 = run_git(["reset", "--hard"])
            success2, out2 = run_git(["clean", "-fd"])
            if success1 and success2:
                console.print("[green]Árvore de trabalho limpa. Todas as alterações foram descartadas.[/green]")
            else:
                console.print(f"[red]Erro ao limpar:\n{out1}\n{out2}[/red]")

    questionary.press_any_key_to_continue("\nPressione qualquer tecla para voltar...").ask()


def main():
    if not is_git_repo():
        console.print("[bold red]❌ Esta pasta não é um repositório Git.[/bold red]")
        console.print("Rode [yellow]git init[/yellow] primeiro!")
        sys.exit(1)

    while True:
        show_header()
        
        choice = questionary.select(
            "Execute uma ação:",
            choices=[
                "📝 Fazer Commit",
                "🌿 Gerenciar Branches",
                "🔄 Sincronizar (Push/Pull)",
                "📜 Ver Histórico (Log)",
                "📦 Guarda-volumes (Stash)",
                "↩️  Desfazer / Reverter",
                "🚪 Sair"
            ]
        ).ask()

        if choice == "📝 Fazer Commit":
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

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Assistente encerrado.[/yellow]")
        sys.exit(0)