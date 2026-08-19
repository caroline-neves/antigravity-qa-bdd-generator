---
name: test-scenario-generator
description: >-
  Agente especialista na análise, revisão e geração de cenários de teste de software (BDD/Gherkin).
  Lê os requisitos da issue do Jira em `input/current_issue.md`, varre a suíte existente em `features/`,
  aplica as regras em `.agents/rules/gherkin-aio-rules.md`, classifica os cenários (Reuso, Atualização, Criação),
  gera o relatório de Matriz de Impacto e exporta arquivos `.feature` para o AIO Tests do Jira.
---

# Agente Gerador e Analisador de Cenários de Teste (AIO Tests Jira)

Este skill guia o Antigravity na geração, revisão e manutenção de cenários de teste de software no formato BDD/Gherkin compatíveis com as diretrizes de QA e com o **AIO Tests do Jira**.

---

## 🎯 Objetivo

Garantir alta cobertura de testes, evitar duplicidade de cenários existentes, atualizar testes desatualizados com rastreabilidade ao ID original (`@TestCaseKey` / `OPK-TC-XXX`), respeitar as regras fundamentais de Gherkin em terceira pessoa e exportar arquivos `.feature` prontos para importação no AIO Tests do Jira.

---

## 📜 Regras de Negócio e Diretrizes de QA

O agente **DEVE** seguir rigorosamente todas as diretrizes definidas no arquivo [`.agents/rules/gherkin-aio-rules.md`](file:///Users/marcusalexandre/Documents/antigravity/fearless-hawking/.agents/rules/gherkin-aio-rules.md):

1. **Terceira Pessoa Obrigatória**: `"Dado que o usuário..."`, `"Quando clica..."`. NUNCA primeira pessoa.
2. **Proibição de `E`/`And` após `Dado`/`Given`**: Incorporar o contexto no próprio `Dado` ou reestruturar.
3. **Limite de `E`/`And`**: Máximo 3 por passo. Se necessário, utilizar asterisco (`*`) para listas simples ou separar cenários.
4. **Atomicidade**: 1 cenário = 1 comportamento e 1 resultado claro.
5. **Estilo Declarativo vs Procedural**: Usar declarativo para regras de negócio (O QUE faz) e procedural para layout e exibição de campos/componentes (O QUE exibe).
6. **Evitar Detalhes Técnicos**: Sem seletores DOM, divs, IDs, coordenadas ou cores em hex `#FF0000`.

---

## 🚀 Passo a Passo de Execução do Agente

### Etapa 1: Leitura dos Requisitos da Issue
1. Leia o conteúdo do arquivo [`input/current_issue.md`](file:///Users/marcusalexandre/Documents/antigravity/fearless-hawking/input/current_issue.md) ou da instrução fornecida pelo usuário no chat.
2. Identifique:
   - **Chave da Issue no Jira** (ex: `PROJ-123`).
   - **Título e Módulo da Funcionalidade**.
   - **Regras de Negócio e Critérios de Aceite** (Caminho Feliz, Exceções, Validações, Layout).

### Etapa 2: Varredura e Análise do Banco de Testes Existente
1. Varra a pasta [`features/`](file:///Users/marcusalexandre/Documents/antigravity/fearless-hawking/features/) em busca de arquivos `.feature` existentes.
2. Compare os cenários já existentes com a nova issue.
3. Classifique as mudanças:
   - ♻️ **Cenários a Reutilizar**: Testes existentes que cobrem a funcionalidade sem alterações.
   - ✏️ **Cenários a Atualizar**: Testes existentes afetados que precisam de alterações, preservando a referência original (`OPK-TC-XXX` / `@TestCaseKey`).
   - ✨ **Novos Cenários a Criar**: Cenários inéditos para novos comportamentos ou layout.

### Etapa 3: Apresentação da Proposta com Matriz de Impacto (Human-in-the-Loop)
1. Crie um **Artefato de Revisão** contendo o relatório no seguinte formato padronizado:
   - **Título e Contexto**.
   - **1. Matriz de impacto**: Tabela em markdown com as colunas `Mudança da melhoria | Casos existentes (referência) | Ação`.
   - **2. Cenários a ATUALIZAR (editar o caso existente)**: Formatados com `[ATUALIZAR]`, referência original (ex: `OPK-TC-XXX`), linha `# O que mudou:` e código Gherkin.
   - **3. Cenários NOVOS (criar)**: Formatados com `[NOVO]` e código Gherkin.
2. Configure `RequestFeedback: true` no artefato para validação do QA.

### Etapa 4: Geração dos Arquivos `.feature` e Validação AIO Tests
1. Após a aprovação do QA, salve os arquivos `.feature` formatados na pasta [`output/`](file:///Users/marcusalexandre/Documents/antigravity/fearless-hawking/output/).
2. Garanta a presença do cabeçalho `# language: pt`, das tags Jira (`@JiraKey=...`) e das tags AIO Tests (`@TestCaseKey=...`, `@Priority=...`).
3. Execute o script de validação:
   ```bash
   python3 scripts/aio_validator.py output/
   ```
4. Informe ao usuário a localização dos arquivos prontos para importação no AIO Tests.
