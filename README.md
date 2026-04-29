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

*   **Tudo em Um:** Commits, Branches e Sincronização em um único menu interativo.
*   **Padronização Automática:** Segue rigorosamente os padrões de [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/), com opção de adicionar tudo (git add .) ou escolher arquivos específicos.
*   **Gestão de Branches:** Crie, troque e delete branches sem precisar lembrar das flags do Git.
*   **Segurança:** Validações integradas para garantir que você está em um repositório Git e possui alterações pendentes.
*   **Tratamento Automático:** O comando de Push já lida automaticamente com branches novas que precisam de `set-upstream`.
*   **Visualmente Agradável:** Interface rica no terminal com cores, painéis e feedback visual instantâneo.

---

## ✨ Funcionalidades

- [x] **Painel Interativo 3x3**: Menu principal super responsivo em grade, com navegação por setas do teclado.
- [x] **Dashboard de Bordo**: Painel dinâmico que não polui seu histórico do terminal, mostrando status, logs e ferramentas em uma tela estática.
- [x] **Smart Staging**: Opção de Adicionar TUDO ou selecionar arquivos em formato checklist interativo.
- [x] **Commits Semânticos**: Menu guiado (tipo, escopo, mensagem).
- [x] **Branch Manager**: Interface visual para trocar, criar e deletar branches locais.
- [x] **Tag Manager**: Liste, crie (vincule releases) e delete tags locais e remotas com facilidade.
- [x] **Sincronização Fácil (com GitHub CLI)**: Push e Pull simplificados. Se você tiver a CLI do GitHub (`gh`) instalada, o GitFlowy se oferece para abrir um Pull Request logo após o Push!
- [x] **Tabela de Histórico**: Visualize os últimos commits formatados elegantemente no painel de bordo.
- [x] **Botão de Pânico Avançado**: Escolha entre um `git reset` (preserva arquivos), um `git revert` selecionado em uma lista visual de commits, ou descarte tudo caso o projeto pegue fogo.
- [x] **Guarda-Volumes (Stash)**: Guarde ou recupere alterações inacabadas para transitar entre branches.

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

Um belíssimo Dashboard 3x3 será aberto. Use as **setas do teclado** para deslizar pelas opções e o **Enter** para selecionar a ação desejada:

1. **📝 Fazer Commit**
2. **📊 Status Completo**
3. **🔄 Sync (Push/Pull/PR)**
4. **🌿 Branches**
5. **📜 Histórico (Log)**
6. **🏷️ Tags (Releases)**
7. **📦 Stash (Guarda)**
8. **↩️ Reverter**
9. **🚪 Sair**

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
