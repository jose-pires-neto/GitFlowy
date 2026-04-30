import os
import sys
import subprocess
import platform
import shutil

# Garante suporte a emojis no terminal do Windows (cp1252 -> utf-8)
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

def run_cmd(cmd, check=True):
    try:
        # Usa sys.executable para ter certeza de qual python estamos rodando
        result = subprocess.run(cmd, check=check, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def print_step(msg):
    print(f"\n🚀 {msg}")

def print_success(msg):
    print(f"✅ {msg}")

def print_error(msg):
    print(f"❌ {msg}")

def print_warn(msg):
    print(f"⚠️  {msg}")

def main():
    print("="*60)
    print("🌊 Instalador Universal do GitFlowy 🌊")
    print("="*60)

    # 1. Detect OS
    os_name = platform.system()
    print_step(f"Sistema Operacional detectado: {os_name}")

    # 2. Check Git
    if not shutil.which("git"):
        print_error("Git não encontrado! Por favor, instale o Git antes de continuar.")
        sys.exit(1)
    else:
        print_success("Git está instalado.")

    # 3. Check Pip
    if not shutil.which("pip") and not shutil.which("pip3"):
        print_error("O gerenciador de pacotes 'pip' não foi encontrado.")
        sys.exit(1)
    else:
        print_success("Pip está disponível.")

    # 4. Install pipx se não estiver presente
    pipx_cmd = "pipx"
    if not shutil.which("pipx"):
        print_step("O pipx (recomendado para CLI) não foi encontrado. Tentando instalar via pip...")
        succ, out = run_cmd(f"{sys.executable} -m pip install --user pipx")
        if succ:
            print_success("pipx instalado com sucesso!")
            # Garante que as pastas do pipx entrem no PATH
            run_cmd(f"{sys.executable} -m pipx ensurepath", check=False)
            pipx_cmd = f"{sys.executable} -m pipx"
            print_warn("O pipx foi adicionado ao seu PATH. Talvez você precise reiniciar o terminal depois da instalação.")
        else:
            print_warn(f"Não foi possível instalar o pipx automaticamente. Usaremos o pip convencional.\n(Erro: {out.strip()})")
            pipx_cmd = "pip"
    else:
        print_success("pipx já está instalado.")

    # 5. Instalar GitFlowy
    print_step("Instalando o GitFlowy...")
    
    # Se o script está sendo rodado de dentro do clone/pasta do repositório
    if os.path.exists("pyproject.toml") and "gitflowy" in open("pyproject.toml", encoding="utf-8", errors="ignore").read().lower():
        install_source = "."
        print("Instalando a partir dos arquivos locais do repositório.")
    else:
        install_source = "git+https://github.com/jose-pires-neto/GitFlowy.git"
        print("Baixando a versão mais recente diretamente do GitHub...")

    if "pipx" in pipx_cmd:
        install_cmd = f"{pipx_cmd} install --force {install_source}"
    else:
        install_cmd = f"{sys.executable} -m pip install --user --upgrade {install_source}"

    succ, out = run_cmd(install_cmd)
    if succ:
        print_success("GitFlowy instalado com sucesso!")
    else:
        print_error(f"Erro ao instalar o GitFlowy:\n{out}")
        sys.exit(1)

    # 6. Check gh
    print_step("Verificando integração com GitHub CLI (gh)...")
    
    gh_found = shutil.which("gh")
    if not gh_found and os_name == "Windows":
        # Procura em locais comuns caso o PATH ainda não tenha sido recarregado
        common_paths = [
            r"C:\Program Files\GitHub CLI\gh.exe",
            os.path.expandvars(r"%LocalAppData%\Programs\GitHub CLI\gh.exe")
        ]
        winget_dir = os.path.expandvars(r"%LocalAppData%\Microsoft\WinGet\Packages")
        if os.path.exists(winget_dir):
            for d in os.listdir(winget_dir):
                if d.lower().startswith("github.cli"):
                    path = os.path.join(winget_dir, d, "gh.exe")
                    if os.path.exists(path):
                        common_paths.append(path)
                        
        for path in common_paths:
            if os.path.exists(path):
                gh_found = path
                break
                
    if not gh_found:
        print_warn("GitHub CLI (gh) não encontrado.")
        print("   O GitFlowy funciona normalmente sem ele, mas as opções de Pull Request ficarão inativas.")
        if os_name == "Windows":
            print("   Dica de instalação no Windows: winget install --id GitHub.cli")
        elif os_name == "Darwin":
            print("   Dica de instalação no Mac: brew install gh")
        else:
            print("   Dica de instalação no Linux (Ubuntu/Debian): sudo apt install gh")
    else:
        print_success("GitHub CLI (gh) encontrado! Todas as integrações ativadas.")

    print("\n" + "="*60)
    print("🎉 Instalação concluída com sucesso!")
    
    if "pipx" in pipx_cmd and "pipx install" not in out:
        print("⚠️  Se o comando 'gflow' não for reconhecido, feche o terminal e abra um novo para atualizar o PATH.")
        
    print("Para começar, navegue até um projeto Git e digite: gflow")
    print("="*60)

if __name__ == "__main__":
    main()
