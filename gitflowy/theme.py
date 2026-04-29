import sys
try:
    from rich.console import Console
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
