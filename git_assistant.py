import os
import subprocess
import sys

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.table import Table
    import questionary
except ImportError:
    print("⚠️  Dependências ausentes! Para a interface bonita, instale:")
    print("👉 pip install rich questionary")
    sys.exit(1)

console = Console()

def run_git(args, exit_on_error=False):
    """Executa um comando git de forma silenciosa. Retorna (sucesso, output_ou_erro)."""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() or e.stdout.strip()
        if exit_on_error:
            console.print(f"[bold red]Erro crítico no Git:[/bold red] {error_msg}")
            sys.exit(1)
        return False, error_msg

def is_git_repo():
    """Verifica se a pasta atual é um repositório Git."""
    return os.path.isdir(".git") or run_git(["rev-parse", "--is-inside-work-tree"])[0]

def get_changed_files():
    """Obtém a lista de arquivos modificados, adicionados ou deletados."""
    success, output = run_git(["status", "--porcelain"])
    if not success or not output:
        return []
    
    files = []
    for line in output.split("\n"):
        if len(line) > 2:
            # Pega o caminho do arquivo e o status
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
    """Mostra o cabeçalho estilizado."""
    console.clear()
    console.print()
    console.print(Panel("[bold cyan]🌊 GitFlowy CLI[/bold cyan]\n[dim]Seu assistente Git definitivo[/dim]", expand=False, border_style="cyan"))
    
    # Mostra a branch atual
    current_branch, _ = get_branches()
    if current_branch:
        console.print(f"📍 Branch atual: [bold magenta]{current_branch}[/bold magenta]\n")

# --- MÓDULOS DE FUNCIONALIDADES ---

def handle_commit():
    """Fluxo de commit (Adicionar Tudo vs Selecionar)"""
    changed_files = get_changed_files()
    
    if not changed_files:
        console.print("🌿 [bold green]A árvore de trabalho está limpa![/bold green] Nenhum arquivo para commitar.")
        questionary.press_any_key_to_continue("Pressione qualquer tecla para voltar...").ask()
        return

    # 1. Modo de Staging
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
        selected_files = ["."] # Representa todos os arquivos
    else:
        # Pega apenas os nomes dos arquivos, tirando o prefixo de status
        file_choices = [f[3:] for f in changed_files]
        selected_files = questionary.checkbox(
            "Selecione os arquivos para o commit:",
            choices=file_choices,
            style=questionary.Style([('highlighted', 'fg:#00ffff bold')])
        ).ask()

        if not selected_files:
            console.print("[yellow]Nenhum arquivo selecionado.[/yellow]")
            return

    # 2. Tipo de Commit (Conventional Commits)
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

    # 3. Escopo e Mensagem
    commit_scope = questionary.text("Qual o escopo? (Opcional, ex: auth, ui):").ask()
    commit_message = questionary.text("Descreva a alteração:").ask()

    if not commit_message:
        console.print("[bold red]❌ A mensagem é obrigatória.[/bold red]")
        questionary.press_any_key_to_continue().ask()
        return

    scope_str = f"({commit_scope})" if commit_scope else ""
    final_message = f"{commit_tag}{scope_str}: {commit_message}"

    console.print(f"\n[dim]Mensagem gerada:[/dim] [bold white]{final_message}[/bold white]")
    if not questionary.confirm("Confirmar commit?").ask():
        return

    # 4. Execução
    with console.status("[bold cyan]Commitando...[/bold cyan]", spinner="dots"):
        if selected_files == ["."]:
            run_git(["add", "."])
        else:
            for file in selected_files:
                run_git(["add", file])
        
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
        # Remove a branch atual da lista de opções de troca
        options = [b for b in branches if b != current_branch]
        if not options:
            console.print("[yellow]Não há outras branches para trocar.[/yellow]")
            questionary.press_any_key_to_continue().ask()
            return
            
        target = questionary.select("Para qual branch deseja mudar?", choices=options).ask()
        if target:
            success, msg = run_git(["checkout", target])
            console.print(f"[green]Mudou para a branch '{target}'[/green]" if success else f"[red]Erro: {msg}[/red]")
            questionary.press_any_key_to_continue().ask()

    elif "Criar" in action:
        new_branch = questionary.text("Nome da nova branch:").ask()
        if new_branch:
            success, msg = run_git(["checkout", "-b", new_branch])
            console.print(f"[green]Branch '{new_branch}' criada e ativada![/green]" if success else f"[red]Erro: {msg}[/red]")
            questionary.press_any_key_to_continue().ask()
            
    elif "Deletar" in action:
        options = [b for b in branches if b != current_branch and b != "main" and b != "master"]
        if not options:
            console.print("[yellow]Não há branches seguras para deletar.[/yellow]")
            questionary.press_any_key_to_continue().ask()
            return
            
        target = questionary.select("Qual branch deseja deletar?", choices=options).ask()
        if target and questionary.confirm(f"Tem certeza que deseja deletar '{target}'?").ask():
            success, msg = run_git(["branch", "-D", target])
            console.print(f"[green]Branch '{target}' deletada![/green]" if success else f"[red]Erro: {msg}[/red]")
            questionary.press_any_key_to_continue().ask()

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
            # Tenta um push simples. Se falhar por falta de upstream, tenta definir.
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


def main():
    if not is_git_repo():
        console.print("[bold red]❌ Esta pasta não é um repositório Git.[/bold red]")
        console.print("Rode [yellow]git init[/yellow] primeiro!")
        sys.exit(1)

    while True:
        show_header()
        
        choice = questionary.select(
            "O que você deseja fazer?",
            choices=[
                "📝 Fazer Commit",
                "🌿 Gerenciar Branches",
                "🔄 Sincronizar (Push/Pull)",
                "🚪 Sair"
            ],
            style=questionary.Style([('highlighted', 'fg:#00ffff bold')])
        ).ask()

        if choice == "📝 Fazer Commit":
            handle_commit()
        elif choice == "🌿 Gerenciar Branches":
            handle_branches()
        elif choice == "🔄 Sincronizar (Push/Pull)":
            handle_sync()
        elif choice == "🚪 Sair" or not choice:
            console.print("\n[dim]Até logo! Continue commitando com estilo. 🌊[/dim]")
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Assistente encerrado.[/yellow]")
        sys.exit(0)