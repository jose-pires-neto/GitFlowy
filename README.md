# 🌊 GitFlowy

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)
[![Maintainability](https://img.shields.io/badge/maintainability-A-brightgreen.svg)](https://github.com/jose8/GitFlowy)

O **GitFlowy** é uma ferramenta de linha de comando (CLI) projetada para transformar o fluxo tradicional do Git em uma experiência interativa, visual e livre de erros.

Diga adeus ao `git add .` acidental e à dificuldade de lembrar a sintaxe dos *Conventional Commits*. Com o comando `gflow`, você gerencia seus arquivos e cria mensagens padronizadas em segundos.

---

## 🚀 Por que GitFlowy?

Trabalhar com Git pode ser repetitivo e propenso a erros de digitação ou padronização. O GitFlowy resolve isso oferecendo:

*   **Staging Interativo:** Selecione exatamente quais arquivos deseja commitar usando uma interface visual.
*   **Padronização Automática:** Segue rigorosamente os padrões de [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).
*   **Interface Premium:** Experiência rica no terminal com cores, painéis e feedback visual instantâneo.
*   **Segurança:** Validações integradas para garantir que você está em um repositório Git e possui alterações pendentes.

---

## ✨ Funcionalidades

- [x] **Seleção de Arquivos:** Interface de checklist para `git add`.
- [x] **Menu Semântico:** Escolha entre `feat`, `fix`, `docs`, `style`, `refactor`, etc.
- [x] **Escopo Opcional:** Adicione contexto ao seu commit (ex: `auth`, `ui`).
- [x] **Mensagem Guiada:** Garante que a descrição seja preenchida.
- [x] **Execução Automática:** Faz o `add` e o `commit` em um único fluxo.

---

## 📦 Instalação

### Via pipx (Recomendado)
O `pipx` é a melhor forma de instalar ferramentas CLI de forma isolada e global.

```bash
pipx install git+https://github.com/jose-pires-neto/GitFlowy.git
```

### Via pip
```bash
pip install git+https://github.com/jose-pires-neto/GitFlowy.git
```

### 🗑️ Desinstalação

Se você precisar remover o GitFlowy, utilize o comando correspondente ao método de instalação:

**Se instalou via pipx:**
```bash
pipx uninstall gitflowy
```

**Se instalou via pip:**
```bash
pip uninstall gitflowy
```

> [!NOTE]
> Certifique-se de ter o Python 3.7+ instalado em sua máquina.

---

## 💻 Como Usar

É simples. Em qualquer repositório Git, basta digitar:

```bash
gflow
```

### O Fluxo de Trabalho:
1.  **Stage:** Use a `Barra de Espaço` para selecionar arquivos e `Enter` para confirmar.
2.  **Tipo:** Escolha a categoria da alteração (✨ feature, 🐛 fix, etc).
3.  **Escopo:** (Opcional) Defina a área afetada.
4.  **Mensagem:** Escreva uma descrição curta e clara.
5.  **Confirmação:** Revise a mensagem gerada e confirme.

---

## 🛠️ Tecnologias

O GitFlowy é construído sobre bases sólidas e modernas:

*   [**Rich**](https://github.com/Textualize/rich): Responsável pela beleza e formatação do terminal.
*   [**Questionary**](https://github.com/tmbo/questionary): Proporciona a interatividade fluida dos prompts.

---

## 🤝 Contribuindo

Ideias e melhorias são sempre bem-vindas! Para contribuir:

1.  Faça um **Fork** do projeto.
2.  Crie uma **Branch** para sua feature (`git checkout -b feature/NovaFeature`).
3.  Use o `gflow` para seus commits! 😉
4.  Abra um **Pull Request**.

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---
<p align="center">
  Desenvolvido por um preguiçoso para simplificar a vida dos desenvolvedores.
</p>
