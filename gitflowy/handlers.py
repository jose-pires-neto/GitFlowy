import os
import json
import subprocess
import webbrowser
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich import box
import questionary

from gitflowy.theme import console
from gitflowy.core import (
    get_changed_files, get_branches, get_tags, get_default_remote,
    run_git, has_gh_cli, run_gh, check_gh_auth, get_gh_executable
)
from gitflowy.ui import show_header


def handle_status():
    """Exibe um status detalhado e organizado de todos os arquivos modificados."""
    files = get_changed_files()
    
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
        handle_commit()


def handle_commit():
    """Fluxo de commit guiado."""
    show_header("Fazer Commit", "Adicione e descreva suas alterações")
    changed_files = get_changed_files()
    
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
        if selected_files == ["."]:
            run_git(["add", "."])
        else:
            run_git(["add", "--"] + selected_files)
        
        success, err = run_git(["commit", "-m", final_message])

    show_header("Fazer Commit", "Resultado da operação")
    if success:
        console.print(Panel("[bold green]Commit realizado com sucesso![/bold green]", expand=False, border_style="green"))
    else:
        console.print(f"[bold red]Erro ao commitar:[/bold red]\n{err}")
    
    questionary.press_any_key_to_continue("\nPressione qualquer tecla para voltar ao menu...").ask()


def handle_branches():
    """Gerenciador de Branches visual."""
    current_branch, branches = get_branches()
    
    tree = Tree("[bold green]Repositório Local[/bold green]", guide_style="bold cyan")
    primary_branch = next((b for b in branches if b in ["main", "master"]), None)
    
    if primary_branch:
        is_current = " [bold magenta](atual)[/bold magenta]" if primary_branch == current_branch else ""
        main_node = tree.add(f"* [bold cyan]{primary_branch}[/bold cyan]{is_current}")
        
        for b in branches:
            if b != primary_branch:
                if b == current_branch:
                    main_node.add(f"- [bold magenta]{b}[/bold magenta] [dim](atual)[/dim]")
                else:
                    main_node.add(f"- [cyan]{b}[/cyan]")
    else:
        for b in branches:
            if b == current_branch:
                tree.add(f"- [bold magenta]{b}[/bold magenta] [dim](atual)[/dim]")
            else:
                tree.add(f"- [cyan]{b}[/cyan]")
            
    tree_panel = Panel(tree, title="Estrutura de Branches", border_style="cyan", expand=True)
    show_header("Gerenciar Branches", "Crie, navegue ou delete suas branches", custom_display=tree_panel)
    
    action = questionary.select(
        "O que deseja fazer?",
        choices=[
            "Trocar de branch",
            "Criar nova branch",
            "Deletar branch",
            "Voltar"
        ]
    ).ask()

    if not action or action == "Voltar":
        return

    if action == "Trocar de branch":
        options = [b for b in branches if b != current_branch]
        if not options:
            console.print("[yellow]Não há outras branches locais para alternar.[/yellow]")
            questionary.press_any_key_to_continue("Pressione qualquer tecla para voltar...").ask()
            return
            
        target = questionary.select("Para qual branch deseja mudar?", choices=options).ask()
        if target:
            success, msg = run_git(["checkout", target])
            show_header("Gerenciar Branches", "Resultado")
            console.print(f"[green]Mudou para a branch '{target}'[/green]" if success else f"\n[red]Erro:\n{msg}[/red]")
            questionary.press_any_key_to_continue("Pressione qualquer tecla para voltar...").ask()

    elif action == "Criar nova branch":
        new_branch = questionary.text("Nome da nova branch:").ask()
        if new_branch:
            success, msg = run_git(["checkout", "-b", new_branch])
            show_header("Gerenciar Branches", "Resultado")
            console.print(f"[green]Branch '{new_branch}' criada e ativada![/green]" if success else f"[red]Erro: {msg}[/red]")
            questionary.press_any_key_to_continue("Pressione qualquer tecla para voltar...").ask()
            
    elif action == "Deletar branch":
        options = [b for b in branches if b != current_branch and b not in ["main", "master"]]
        if not options:
            console.print("[yellow]Não há branches seguras para deletar (não é possível deletar a branch atual ou main/master).[/yellow]")
            questionary.press_any_key_to_continue("Pressione qualquer tecla para voltar...").ask()
            return
            
        target = questionary.select("Qual branch deseja deletar?", choices=options).ask()
        if target and questionary.confirm(f"Confirma a exclusão de '{target}'?").ask():
            success, msg = run_git(["branch", "-d", target])
            if not success:
                console.print(f"[yellow]Atenção: A branch '{target}' possui commits não mesclados![/yellow]")
                if questionary.confirm("Deseja FORÇAR a exclusão (-D)? Os commits não mesclados serão PERDIDOS permanentemente.").ask():
                    success, msg = run_git(["branch", "-D", target])
                    console.print(f"[green]Branch '{target}' deletada forçadamente![/green]" if success else f"[red]Erro: {msg}[/red]")
            else:
                console.print(f"[green]Branch '{target}' deletada com segurança![/green]")
            questionary.press_any_key_to_continue("Pressione qualquer tecla para voltar...").ask()


def handle_sync():
    """Faz Push e Pull do repositório."""
    show_header("Sincronização", "Envie ou baixe alterações do repositório remoto")
    action = questionary.select(
        "Selecione uma ação:",
        choices=["Push (Enviar alterações)", "Pull (Puxar alterações)", "Voltar"]
    ).ask()
    
    if not action or action == "Voltar":
        return
    
    current_branch, _ = get_branches()
    remote_name = get_default_remote()
    
    if "Push" in action:
        with console.status(f"[bold cyan]Enviando branch {current_branch} para {remote_name}...[/bold cyan]"):
            success, msg = run_git(["push"])
            if not success and "set-upstream" in msg:
                success, msg = run_git(["push", "--set-upstream", remote_name, current_branch])
        
        show_header("Sincronização", "Resultado do Push")
        if success:
            console.print("[bold green]Push realizado com sucesso![/bold green]")
            
            # Integração opcional com GitHub CLI
            if has_gh_cli():
                console.print("\n[dim]GitHub CLI (gh) detectado no sistema.[/dim]")
                if questionary.confirm("Deseja abrir um Pull Request para esta branch agora?").ask():
                    if not check_gh_auth():
                        console.print("[yellow]Você precisa autenticar o GitHub CLI primeiro.[/yellow]")
                        if questionary.confirm("Deseja fazer login no GitHub agora?").ask():
                            subprocess.run([get_gh_executable(), "auth", "login"])
                    
                    if check_gh_auth():
                        succ_log, last_commit = run_git(["log", "-1", "--pretty=format:%s"])
                        default_title = last_commit if succ_log else current_branch
                        
                        pr_title = questionary.text("Título do Pull Request:", default=default_title).ask()
                        if pr_title:
                            pr_body = questionary.text("Descrição (opcional):").ask()
                            
                            with console.status("[bold cyan]Criando Pull Request...[/bold cyan]", spinner="dots"):
                                args = ["pr", "create", "--title", pr_title, "--body", pr_body if pr_body else ""]
                                succ_pr, out_pr = run_gh(args)
                                
                            if succ_pr:
                                console.print("[bold green]Pull Request criado com sucesso![/bold green]")
                                console.print(f"Link: [link={out_pr}]{out_pr}[/link]")
                            else:
                                console.print(f"[bold red]Erro ao criar o Pull Request:[/bold red]\n{out_pr}")
                    else:
                        console.print("[red]Operação cancelada: GitHub CLI não autenticado.[/red]")
        else:
            console.print(f"[bold red]Erro no Push:[/bold red]\n{msg}")
            
    elif "Pull" in action:
        with console.status(f"[bold cyan]Puxando alterações em {current_branch}...[/bold cyan]"):
            success, msg = run_git(["pull"])
        show_header("Sincronização", "Resultado do Pull")
        if success:
            console.print("[bold green]Pull realizado com sucesso![/bold green]")
        else:
            console.print(f"[bold red]Erro no Pull:[/bold red]\n{msg}")
                
    questionary.press_any_key_to_continue("\nPressione qualquer tecla para voltar...").ask()


def handle_history():
    """Mostra o histórico recente de commits formatado dentro do header."""
    success, output = run_git(["log", "-n", "10", "--pretty=format:%h<||>%s<||>%ar<||>%an"])
    
    if not success or not output:
        show_header("Histórico (Log)", "Linha do tempo dos commits")
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
    
    show_header("Histórico (Log)", "Linha do tempo dos commits", custom_display=table)
    questionary.press_any_key_to_continue("\nPressione qualquer tecla para voltar...").ask()


def handle_stash():
    """Gerencia o stash (área de rascunho)."""
    show_header("Stash", "Guarde suas alterações temporariamente")
    action = questionary.select(
        "Selecione uma opção:",
        choices=[
            "Guardar alterações (stash save)",
            "Recuperar últimas alterações (stash pop)",
            "Listar itens guardados (stash list)",
            "Limpar tudo (stash clear)",
            "Voltar"
        ]
    ).ask()

    if not action or action == "Voltar":
        return

    if "Guardar" in action:
        msg = questionary.text("Nome/Mensagem para esse rascunho (opcional):").ask()
        args = ["stash", "push", "-m", msg] if msg else ["stash"]
        success, out = run_git(args)
        show_header("Stash", "Resultado")
        console.print(f"[green]{out}[/green]" if success else f"[red]Erro: {out}[/red]")
        
    elif "Recuperar" in action:
        success, out = run_git(["stash", "pop"])
        show_header("Stash", "Resultado")
        console.print(f"[green]{out}[/green]" if success else f"[red]Erro: {out}[/red]")
        
    elif "Listar" in action:
        success, out = run_git(["stash", "list"])
        show_header("Stash", "Itens Guardados")
        if out:
            console.print(f"[cyan]{out}[/cyan]")
        else:
            console.print("[yellow]O stash está vazio.[/yellow]")
        
    elif "Limpar" in action:
        if questionary.confirm("Tem certeza? Todos os stashes serão apagados permanentemente.").ask():
            success, out = run_git(["stash", "clear"])
            show_header("Stash", "Resultado")
            console.print("[green]Stash limpo com sucesso![/green]" if success else f"[red]Erro: {out}[/red]")

    questionary.press_any_key_to_continue("\nPressione qualquer tecla para voltar...").ask()


def handle_tags():
    """Gerenciador de Tags (Releases)."""
    tags = get_tags()
    
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
            args = ["tag", "-a", tag_name, "-m", tag_msg if tag_msg else f"Release {tag_name}"]
            success, out = run_git(args)
            show_header("Gerenciador de Tags", "Resultado")
            if success:
                console.print(f"[bold green]Tag {tag_name} criada com sucesso no commit atual![/bold green]")
            else:
                console.print(f"[bold red]Erro ao criar Tag:[/bold red]\n{out}")
                
    elif action == "Enviar Tags para o remoto (push --tags)":
        remote_name = get_default_remote()
        with console.status(f"[bold cyan]Enviando tags para {remote_name}...[/bold cyan]", spinner="dots"):
            success, out = run_git(["push", "--tags", remote_name])
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
                success, out = run_git(["tag", "-d", target])
                show_header("Gerenciador de Tags", "Resultado")
                if success:
                    console.print(f"[green]Tag '{target}' deletada localmente.[/green]")
                    remote_name = get_default_remote()
                    with console.status(f"[bold cyan]Apagando do repositório remoto ({remote_name})...[/bold cyan]", spinner="dots"):
                        succ_rem, out_rem = run_git(["push", "--delete", remote_name, target])
                    if succ_rem:
                        console.print(f"[green]Tag '{target}' deletada remotamente.[/green]")
                    else:
                        console.print(f"[yellow]Aviso: Não foi possível deletar remotamente: {out_rem}[/yellow]")
                else:
                    console.print(f"[red]Erro ao deletar localmente: {out}[/red]")
                    
    questionary.press_any_key_to_continue("\nPressione qualquer tecla para voltar...").ask()


def handle_undo():
    """Ferramentas para desfazer ações (Reset, Restore, Revert)."""
    default_undo_table = Table(title="Opções de Reversão", expand=True)
    default_undo_table.add_column("Ação", style="bold cyan")
    default_undo_table.add_column("Descrição", style="white")
    default_undo_table.add_row("Desfazer Último Commit", "Apaga o commit mas preserva os arquivos modificados (Seguro)")
    default_undo_table.add_row("Reverter Commit", "Cria um commit reverso anulando uma alteração específica")
    default_undo_table.add_row("Descartar Alterações", "Descarta todas as alterações não commitadas (Irreversível)")
    
    show_header("Desfazer / Reverter", "Ações de reversão de histórico", custom_display=default_undo_table)
    
    action = questionary.select(
        "O que você deseja desfazer?",
        choices=[
            "Desfazer último commit (mantendo arquivos)",
            "Reverter commit específico (git revert)",
            "Descartar todas as alterações não commitadas",
            "Voltar"
        ]
    ).ask()

    if not action or action == "Voltar":
        return

    if action == "Desfazer último commit (mantendo arquivos)":
        if questionary.confirm("Isso vai apagar o último commit do histórico, mas seus arquivos continuarão modificados. Continuar?").ask():
            success, out = run_git(["reset", "--soft", "HEAD~1"])
            show_header("Desfazer / Reverter", "Resultado")
            console.print("[green]Último commit desfeito! Arquivos mantidos na sua máquina.[/green]" if success else f"[red]Erro: {out}[/red]")
            
    elif action == "Reverter commit específico (git revert)":
        success, log_out = run_git(["log", "-n", "15", "--pretty=format:%h<||>%s<||>%ar"])
        if not success or not log_out:
            console.print("[yellow]Nenhum histórico encontrado para reverter.[/yellow]")
            questionary.press_any_key_to_continue("Pressione qualquer tecla para voltar...").ask()
            return
            
        table = Table(title="Últimos 15 Commits (Revert)", expand=True)
        table.add_column("Hash", style="cyan", no_wrap=True)
        table.add_column("Mensagem", style="white")
        table.add_column("Tempo", style="green")

        commits = []
        for line in log_out.split('\n'):
            parts = line.split('<||>')
            if len(parts) == 3:
                hash_id, msg, time_ago = parts
                commits.append(questionary.Choice(title=f"{hash_id} - {msg[:50]}", value=hash_id))
                table.add_row(hash_id, msg[:40] + ("..." if len(msg)>40 else ""), time_ago)
                
        show_header("Desfazer / Reverter", "Selecione o commit para reverter", custom_display=table)
        
        target_commit = questionary.select(
            "Qual commit você deseja reverter?",
            choices=commits + [questionary.Choice(title="Cancelar", value=None)]
        ).ask()
        
        if not target_commit:
            return
            
        with console.status(f"[bold cyan]Revertendo commit {target_commit}...[/bold cyan]", spinner="dots"):
            success, out = run_git(["revert", "--no-edit", target_commit])
            
        show_header("Desfazer / Reverter", "Resultado do Revert")
        if success:
            console.print(f"[bold green]Commit {target_commit} revertido com sucesso![/bold green]")
        else:
            console.print(f"[bold red]Conflito ao reverter o commit {target_commit}:[/bold red]")
            console.print("[yellow]Você precisará resolver os conflitos manualmente e concluir o commit.[/yellow]")

    elif action == "Descartar todas as alterações não commitadas":
        if questionary.confirm("PERIGO: Isso apagará todas as modificações não commitadas de forma IRREVERSÍVEL. Continuar?").ask():
            success1, out1 = run_git(["reset", "--hard"])
            success2, out2 = run_git(["clean", "-fd"])
            show_header("Desfazer / Reverter", "Resultado")
            if success1 and success2:
                console.print("[green]Árvore de trabalho limpa. Todas as alterações locais foram descartadas.[/green]")
            else:
                console.print(f"[red]Erro ao limpar:\n{out1}\n{out2}[/red]")

    questionary.press_any_key_to_continue("\nPressione qualquer tecla para voltar...").ask()


def handle_pull_requests():
    """Gerenciamento de Pull Requests via GitHub CLI."""
    if not has_gh_cli():
        show_header("Pull Requests", "Integração com GitHub")
        console.print("[bold red]O GitHub CLI (gh) não foi encontrado no seu sistema.[/bold red]")
        console.print("Para gerenciar Pull Requests pelo terminal, instale o gh: https://cli.github.com/")
        questionary.press_any_key_to_continue("\nPressione qualquer tecla para voltar...").ask()
        return

    if not check_gh_auth():
        show_header("Pull Requests", "Autenticação Necessária")
        console.print("[yellow]O GitHub CLI (gh) está instalado, mas você não está logado na sua conta.[/yellow]")
        if questionary.confirm("Deseja fazer o login no GitHub agora?").ask():
            gh_exe = get_gh_executable()
            subprocess.run([gh_exe, "auth", "login"])
            
            if not check_gh_auth():
                console.print("[red]\nAutenticação não concluída.[/red]")
                questionary.press_any_key_to_continue("Pressione qualquer tecla para voltar...").ask()
                return
        else:
            return

    while True:
        show_header("Gerenciar Pull Requests", "Crie, avalie e faça merge de PRs no GitHub")
        
        action = questionary.select(
            "O que deseja fazer?",
            choices=[
                "Criar novo Pull Request",
                "Listar e gerenciar PRs abertos",
                "Voltar"
            ]
        ).ask()
        
        if not action or action == "Voltar":
            break
            
        if action == "Criar novo Pull Request":
            current_branch, _ = get_branches()
            succ_log, last_commit = run_git(["log", "-1", "--pretty=format:%s"])
            default_title = last_commit if succ_log else current_branch
            
            pr_title = questionary.text("Título do Pull Request:", default=default_title).ask()
            if pr_title:
                pr_body = questionary.text("Descrição (opcional):").ask()
                
                with console.status("[bold cyan]Criando Pull Request...[/bold cyan]", spinner="dots"):
                    args = ["pr", "create", "--title", pr_title, "--body", pr_body if pr_body else ""]
                    succ_pr, out_pr = run_gh(args)
                    
                show_header("Gerenciar Pull Requests", "Resultado")
                if succ_pr:
                    console.print("[bold green]Pull Request criado com sucesso![/bold green]")
                    console.print(f"Link: [link={out_pr.strip()}]{out_pr.strip()}[/link]")
                else:
                    console.print(f"[bold red]Erro ao criar o Pull Request:[/bold red]\n{out_pr}")
                questionary.press_any_key_to_continue("\nPressione qualquer tecla para continuar...").ask()
                
        elif action == "Listar e gerenciar PRs abertos":
            with console.status("[bold cyan]Buscando Pull Requests abertos...[/bold cyan]", spinner="dots"):
                succ_list, out_list = run_gh(["pr", "list", "--json", "number,title,author,url", "--limit", "30"])
                
            if not succ_list:
                console.print(f"[bold red]Erro ao buscar PRs:[/bold red]\n{out_list}")
                questionary.press_any_key_to_continue("\nPressione qualquer tecla para continuar...").ask()
                continue
                
            try:
                prs = json.loads(out_list)
            except json.JSONDecodeError:
                prs = []
                
            if not prs:
                show_header("Pull Requests Abertos", "Lista vazia")
                console.print("[yellow]Nenhum Pull Request aberto encontrado.[/yellow]")
                questionary.press_any_key_to_continue("\nPressione qualquer tecla para continuar...").ask()
                continue
                
            table = Table(title="Pull Requests Abertos", expand=True)
            table.add_column("ID", style="cyan", justify="right")
            table.add_column("Título", style="white")
            table.add_column("Autor", style="magenta")
            
            choices = []
            for pr in prs:
                num_str = f"#{pr.get('number', '?')}"
                author_info = pr.get('author')
                author_login = author_info.get('login', 'desconhecido') if isinstance(author_info, dict) else 'desconhecido'
                pr_title = pr.get('title', 'Sem título')
                table.add_row(num_str, pr_title, author_login)
                choices.append(questionary.Choice(title=f"{num_str} - {pr_title} ({author_login})", value=pr))
                
            choices.append(questionary.Choice(title="Voltar", value=None))
            
            show_header("Pull Requests Abertos", "Selecione um PR para gerenciar", custom_display=table)
            
            selected_pr = questionary.select(
                "Qual Pull Request deseja gerenciar?",
                choices=choices
            ).ask()
            
            if not selected_pr:
                continue
                
            pr_action = questionary.select(
                f"Gerenciando PR #{selected_pr['number']} ({selected_pr['title']})",
                choices=[
                    "Fazer merge do PR",
                    "Fechar PR (sem merge)",
                    "Abrir no navegador",
                    "Voltar"
                ]
            ).ask()
            
            if not pr_action or pr_action == "Voltar":
                continue
                
            if pr_action == "Fazer merge do PR":
                merge_type = questionary.select(
                    "Qual método de merge deseja usar?",
                    choices=[
                        questionary.Choice(title="Merge (Create a merge commit)", value="--merge"),
                        questionary.Choice(title="Squash (Squash and merge)", value="--squash"),
                        questionary.Choice(title="Rebase (Rebase and merge)", value="--rebase")
                    ]
                ).ask()
                
                if merge_type and questionary.confirm(f"Confirma o merge do PR #{selected_pr['number']}?").ask():
                    delete_remote = questionary.confirm("Deseja deletar a branch remota após o merge?", default=False).ask()
                    merge_args = ["pr", "merge", str(selected_pr['number']), merge_type]
                    if delete_remote:
                        merge_args.append("--delete-branch")
                    with console.status("[bold cyan]Realizando merge...[/bold cyan]", spinner="dots"):
                        succ_merge, out_merge = run_gh(merge_args)
                        
                    show_header("Pull Requests", "Resultado do Merge")
                    if succ_merge:
                        console.print(f"[bold green]Pull Request #{selected_pr['number']} mergeado com sucesso![/bold green]")
                    else:
                        console.print(f"[bold red]Erro ao realizar merge:[/bold red]\n{out_merge}")
                        
            elif pr_action == "Fechar PR (sem merge)":
                if questionary.confirm(f"Tem certeza que deseja FECHAR o PR #{selected_pr['number']} sem fazer merge?").ask():
                    with console.status("[bold cyan]Fechando PR...[/bold cyan]", spinner="dots"):
                        succ_close, out_close = run_gh(["pr", "close", str(selected_pr['number'])])
                    show_header("Pull Requests", "Resultado")
                    if succ_close:
                        console.print(f"[bold green]Pull Request #{selected_pr['number']} fechado com sucesso![/bold green]")
                    else:
                        console.print(f"[bold red]Erro ao fechar PR:[/bold red]\n{out_close}")
                        
            elif pr_action == "Abrir no navegador":
                webbrowser.open(selected_pr['url'])
                console.print(f"[green]Navegador aberto em: {selected_pr['url']}[/green]")
                
            questionary.press_any_key_to_continue("\nPressione qualquer tecla para continuar...").ask()
