# 🚀 Antigravity Test Scenario Generator (AIO Tests Jira)

Este repositório contém um **Agente Inteligente de Engenharia de Qualidade (QA)** especialista em análise, revisão e geração de cenários de teste de software no formato **BDD / Gherkin**, otimizado para importação no **AIO Tests no Jira**..

---

## 🎯 O que este agente faz?

Ao receber uma issue do Jira (história de usuário, critérios de aceite ou tarefas):
1. **Analisa o Banco de Testes Existente**: Varre a suíte existente na pasta [`features/`](file:///Users/marcusalexandre/Documents/antigravity/fearless-hawking/features/) ou recebe os cenários existentes imputados diretamente pelo usuário no chat.
2. **Classifica os Cenários e Gera Matriz de Impacto**:
   - ♻️ **Reaproveitamento**: Identifica cenários existentes que cobrem a funcionalidade sem alterações.
   - ✏️ **Atualização**: Atualiza testes afetados mantendo a tag de vínculo do AIO Tests (`@OPK-TC-XXX`).
   - ✨ **Novos Cenários**: Gera os novos cenários necessários (caminho feliz, exceções, validações e layout).
3. **Aplica Diretrizes Rígidas de QA**:
   - 🗣️ **Terceira pessoa obrigatória** (*"Given que o usuário..."*, *"When clica..."*).
   - 🛑 **Sem Contexto/Background compartilhado**: Cada cenário possui seu próprio `Given` independente.
   - 📏 **Limite de no máximo 3 `And` por cenário**.
   - 🚫 **Ausência do conectivo "e" solto no texto dos passos ou títulos**.
   - 🎯 **1 Ação por Título de Cenário** (comportamentos separados de Editar, Excluir, Visualizar).
   - 🏷️ **Etiquetagem de Foco**: Classificados como `[Declarativo]` (regras de negócio) ou `[Procedural]` (layout).
4. **Exporta para AIO Tests Jira**: Gera arquivos `.feature` organizados na pasta `output/`.

---

## ❓ Dúvidas Frequentes & Comportamento de Geração

### 1. Toda nova solicitação o conteúdo da pasta `output/` é atualizado ou adiciona mais conteúdo?
- **Para a mesma funcionalidade / issue**: Se você rodar uma nova análise para uma issue já analisada (com ajustes de requisitos), o agente **atualiza e substitui** o conteúdo dos arquivos na pasta `output/` com a versão corrigida e validada.
- **Para issues / módulos novos**: O agente cria novos arquivos `.feature` na pasta `output/` mantendo a nomenclatura da issue (ex: `output/modulo_x_atualizar.feature` e `output/modulo_x_novos.feature`), sem apagar os módulos anteriores já gerados.

---

### 2. Onde o agente pode ser executado?

O projeto foi desenhado de forma híbrida:

#### 🟢 Execução Inteligente (Nativa no Antigravity CLI / IDE)
O agente opera com autonomia total dentro do ecossistema **Google Antigravity** (CLI ou IDE):
- A inteligência, regras de negócio e skills são carregadas automaticamente das pastas `.agents/skills/` e `.agents/rules/`.
- No Antigravity, basta pedir no chat em linguagem natural (*"Gerar cenários para a issue em input/current_issue.md"*).

#### 🟡 Execução Portável (Qualquer IDE, Terminal ou Pipeline CI/CD)
Embora a inteligência generativa seja orquestrada pelo Antigravity, o ecossistema do projeto pode ser executado em **qualquer ambiente**:
- **Script Validador (`scripts/aio_validator.py`)**: Funciona em qualquer terminal (Linux, macOS, Windows, VS Code, Cursor, PyCharm) com **Python 3** instalado, sem dependência do Antigravity.
- **Integração com CI/CD**: Pode ser integrado ao **GitHub Actions, GitLab CI ou Jenkins** para validar automaticamente todos os arquivos `.feature` antes do merge ou envio ao Jira.
- **Guia de Regras QA (`.agents/rules/gherkin-aio-rules.md`)**: Serve como documentação viva e guia de estilo oficial de BDD para qualquer desenvolvedor ou ferramenta de IA.

---

### 3. Precisa estar com uma IA integrada para rodar?
- **Para Geração de Cenários, Análise de Impacto e Escrita BDD (Inteligência Generativa)**: **SIM**. É necessário utilizar um assistente ou modelo de IA (como Antigravity, Claude, Cursor, ChatGPT, GitHub Copilot, Windsurf, etc.) interpretando os requisitos da issue e aplicando as regras do repositório.
- **Para Validação Sintática dos Arquivos (`scripts/aio_validator.py`)**: **NÃO**. O validador é um script estático em Python 3 puro e executa em qualquer computador, terminal ou pipeline de CI/CD sem precisar de IA ou conexão com APIs externas.

---

## 🛠️ Como Utilizar (Passo a Passo)

### Passo 1: Inserir os Requisitos da Issue
Cole as informações da sua issue do Jira no arquivo [`input/current_issue.md`](file:///Users/marcusalexandre/Documents/antigravity/fearless-hawking/input/current_issue.md) ou envie diretamente no chat.

---

### Passo 2: Executar o Agente no Antigravity
No chat do **Antigravity**, digite:

> *"Gerar cenários de teste para a issue em input/current_issue.md"*

---

### Passo 3: Revisar a Proposta e Gerar os Arquivos
1. O Antigravity abrirá um artefato visual contendo o relatório de análise e a **Matriz de Impacto**.
2. Após sua aprovação, os arquivos `.feature` formatados serão salvos na pasta [`output/`](file:///Users/marcusalexandre/Documents/antigravity/fearless-hawking/output/).

---

### Passo 4: Validar os Arquivos Sintaticamente (Qualquer Terminal / Pipeline)
Rode o script validador no terminal:

```bash
python3 scripts/aio_validator.py output/
```

---

## 📁 Estrutura do Projeto

```text
.
├── .agents/
│   ├── rules/
│   │   └── gherkin-aio-rules.md     # Regras oficiais de BDD/Gherkin e QA
│   └── skills/
│       └── test-scenario-generator/ # Skill de automação do agente
├── features/                        # Banco de testes existente (.feature)
├── input/                           # Arquivo de entrada da issue do Jira
├── output/                          # Arquivos .feature gerados para o AIO Tests
├── scripts/
│   └── aio_validator.py             # Validador de sintaxe e regras de QA
└── README.md                        # Documentação do projeto
```
