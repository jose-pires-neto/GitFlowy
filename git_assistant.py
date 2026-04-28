import os
import subprocess
import sys

# Verificação de dependências para garantir que o script funcione
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    import questionary
except ImportError:
    print("⚠️  Dependências ausentes! Para a interface bonita, instale:")
    print("👉 pip install rich questionary")
    sys.exit(1)

console = Console()

def run_git(args):
    """Executa um comando git de forma silenciosa e retorna o output."""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        console.print(f"[bold red]Erro no Git:[/bold red] {e.stderr.strip()}")
        sys.exit(1)

def is_git_repo():
    """Verifica se a pasta atual é um repositório Git."""
    return os.path.isdir(".git") or subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], capture_output=True).returncode == 0

def get_changed_files():
    """Obtém a lista de arquivos modificados, adicionados ou deletados."""
    output = run_git(["status", "--porcelain"])
    if not output:
        return []
    
    files = []
    for line in output.split("\n"):
        if len(line) > 2:
            # Pega apenas o caminho do arquivo (ignora o status 'M ', '??')
            file_path = line[3:]
            files.append(file_path)
    return files

def main():
    # 1. Boas-vindas Elegante
    console.print()
    console.print(Panel("[bold cyan]✨ GitFlowy CLI[/bold cyan]\n[dim]Assistente de Commits Semânticos[/dim]", expand=False, border_style="cyan"))
    console.print()

    # 2. Validação
    if not is_git_repo():
        console.print("[bold red]❌ Esta pasta não é um repositório Git.[/bold red]")
        console.print("Rode [yellow]git init[/yellow] primeiro!")
        sys.exit(1)

    changed_files = get_changed_files()
    if not changed_files:
        console.print("🌿 [bold green]A árvore de trabalho está limpa![/bold green] Nenhum arquivo modificado para commitar.")
        sys.exit(0)

    # 3. Seleção de Arquivos (Staging)
    selected_files = questionary.checkbox(
        "Selecione os arquivos para adicionar ao commit (Use Espaço para selecionar, Enter para confirmar):",
        choices=changed_files,
        style=questionary.Style([('highlighted', 'fg:#00ffff bold')])
    ).ask()

    if not selected_files:
        console.print("[yellow]Nenhum arquivo selecionado. Operação cancelada.[/yellow]")
        sys.exit(0)

    # 4. Tipo de Commit (Conventional Commits)
    commit_type = questionary.select(
        "Qual é o tipo da sua alteração?",
        choices=[
            "feat:     ✨ Nova funcionalidade",
            "fix:      🐛 Correção de bug",
            "docs:     📚 Apenas documentação",
            "style:    💎 Formatação, pontuação (não afeta o código)",
            "refactor: ♻️  Refatoração (nem nova feature, nem correção)",
            "test:     🚨 Adição ou correção de testes",
            "chore:    🔧 Manutenção, dependências, build"
        ]
    ).ask()

    if not commit_type:
        sys.exit(0)

    # Limpa a escolha para pegar só a tag (ex: 'feat')
    commit_tag = commit_type.split(":")[0]

    # 5. Escopo e Mensagem
    commit_scope = questionary.text("Qual o escopo dessa alteração? (Opcional, ex: auth, ui, api):").ask()
    commit_message = questionary.text("Descreva a alteração em poucas palavras:").ask()

    if not commit_message:
        console.print("[bold red]❌ A mensagem é obrigatória.[/bold red]")
        sys.exit(1)

    # 6. Construção da mensagem final
    scope_str = f"({commit_scope})" if commit_scope else ""
    final_message = f"{commit_tag}{scope_str}: {commit_message}"

    console.print(f"\n[dim]Mensagem gerada:[/dim] [bold white]{final_message}[/bold white]")
    
    confirm = questionary.confirm("Confirmar e executar o commit?").ask()
    
    if not confirm:
        console.print("[yellow]Operação cancelada pelo usuário.[/yellow]")
        sys.exit(0)

    # 7. Execução Mágica (git add + git commit)
    with console.status("[bold cyan]Adicionando arquivos e commitando...[/bold cyan]", spinner="dots"):
        for file in selected_files:
            run_git(["add", file])
        
        run_git(["commit", "-m", final_message])

    # 8. Sucesso!
    console.print()
    console.print(Panel(f"🚀 [bold green]Commit realizado com sucesso![/bold green]\n[dim]{len(selected_files)} arquivo(s) enviados.[/dim]", expand=False, border_style="green"))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Assistente encerrado.[/yellow]")
        sys.exit(0)