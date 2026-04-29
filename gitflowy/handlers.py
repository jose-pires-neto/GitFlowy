import os
from rich.table import Table
from rich.panel import Panel
from rich import box
import questionary

from gitflowy.theme import console
from gitflowy.core import get_changed_files, get_branches, run_git
from gitflowy.ui import show_header

def handle_status():
    """Exibe um status detalhado e organizado de todos os arquivos modificados."""
    show_header("Status Completo", "Visão detalhada de todas as alterações")
    files = get_changed_files()
    
    if not files:
        console.print("✨ [bold green]A árvore de trabalho está limpa![/bold green] Nenhuma modificação pendente.")
        questionary.press_any_key_to_continue("Pressione qualquer tecla para voltar...").ask()
        return

    # Tabela detalhada de modificações
    table = Table(title="📦 Arquivos Modificados (Status)", expand=True, box=box.ROUNDED)
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
            estado, color = "✨ Untracked", "green"
        elif "A" in status:
            estado, color = "✅ Adicionado", "green"
        elif "M" in status:
            estado, color = "📝 Modificado", "blue"
        elif "D" in status:
            estado, color = "🗑️ Deletado", "red"
        elif "R" in status:
            estado, color = "🔄 Renomeado", "magenta"
        
        # Desmembra o caminho para visualização em colunas
        dir_name = os.path.dirname(path)
        file_name = os.path.basename(path)
        
        if not dir_name:
            dir_name = "/" # Representa a raiz do repositório
        else:
            dir_name = f"/{dir_name}/"
            
        if "R" in status:
            # Em caso de Renomeação já registrada pelo git, exibe o fluxo todo
            file_name = raw_path
            dir_name = "🔄"
        
        table.add_row(f"[{color}]{estado}[/{color}]", f"[dim]{dir_name}[/dim]", f"[{color}]{file_name}[/{color}]")
    
    console.print(table)
    console.print(f"\n[dim]Total: {len(files)} arquivo(s) modificado(s)[/dim]\n")
    
    action = questionary.select(
        "O que deseja fazer?",
        choices=["📝 Prosseguir para Commit", "Voltar ao Menu Principal"]
    ).ask()
    
    if action == "📝 Prosseguir para Commit":
        handle_commit()

def handle_commit():
    """Fluxo de commit (Adicionar Tudo vs Selecionar)"""
    show_header("Fazer Commit", "Adicione e descreva suas alterações")
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
        # Usa o caminho exato armazenado no dicionário
        file_choices = [f["path"] for f in changed_files]
        selected_files = questionary.checkbox(
            "Selecione os arquivos para o commit:",
            choices=file_choices,
            style=questionary.Style([('highlighted', 'fg:#00CED1 bold')])
        ).ask()

        if not selected_files:
            console.print("[yellow]Nenhum arquivo selecionado.[/yellow]")
            questionary.press_any_key_to_continue("Pressione qualquer tecla para voltar...").ask()
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
    show_header("Gerenciar Branches", "Crie, navegue ou delete suas branches")
    current_branch, branches = get_branches()
    
    action = questionary.select(
        "O que deseja fazer?",
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
    show_header("Sincronização", "Envie ou baixe as alterações do servidor remoto")
    action = questionary.select(
        "Selecione uma opção de rede:",
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
    show_header("Histórico (Log)", "Linha do tempo dos commits")
    # CORREÇÃO: Usando um delimitador complexo '<||>' pois um commit pode possuir '|' no título
    success, output = run_git(["log", "-n", "10", "--pretty=format:%h<||>%s<||>%ar<||>%an"])
    if not success or not output:
        console.print("[yellow]Nenhum histórico encontrado.[/yellow]")
        questionary.press_any_key_to_continue("Pressione qualquer tecla para voltar...").ask()
        return

    table = Table(title="Histórico Recente (Últimos 10 commits)", expand=True)
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
    show_header("Guarda-Volumes (Stash)", "Guarde suas alterações temporariamente")
    action = questionary.select(
        "Selecione uma opção do Guarda-volumes:",
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
    show_header("Desfazer / Reverter", "Cuidado com ações irreversíveis!")
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
