---
name: test-scenario-generator
description: >-
  Analisa, revisa e gera cenários de teste BDD/Gherkin do Obra Prima para o Sceno (principal) ou o AIO Tests.
  Lê a issue do Jira (input/current_issue.md, chat ou PDF), compara com os cenários existentes, classifica
  (reutilizar, atualizar, criar), apresenta o relatório com a matriz de impacto, aguarda o "ok" do QA e só então
  gera os arquivos e importa. As regras de escrita estão em .agents/rules/gherkin-rules.md.
---

# Gerador e revisor de cenários de teste (Sceno / AIO Tests)

Este arquivo descreve **o fluxo de trabalho**. As regras de **como escrever** os cenários estão só em
[`.agents/rules/gherkin-rules.md`](../../rules/gherkin-rules.md). Leia esse arquivo inteiro antes de escrever
ou revisar qualquer cenário. Nenhuma regra de escrita é repetida aqui.

## Regras de trabalho (valem para todo o fluxo)

1. **Aprovação antes de qualquer ação externa.** Nunca crie, atualize, exclua ou importe nada no Sceno, no AIO ou no Jira sem o **"ok" explícito** do QA para aquela ação. Responder a uma dúvida de formato, pasta ou destino **não** é aprovação. Fluxo: proposta → "ok" → ação → resultado.
2. **Não invente.** Local da tela, regra de negócio ou comportamento que não estejam claros na issue, no plano ou no sistema vão para a lista de dúvidas.
3. **Sinalize, não decida sozinho**, nestes casos (seção "Sinalizações" do relatório):
   - a issue pede validação técnica (regras, seção 8.4);
   - há dúvida de como reproduzir uma situação, que a pessoa vai ver com o dev (regras, seção 10.4);
   - o caso de origem é só reprodução de bug (regras, seção 10.2);
   - resultado vago descartado na conversão (regras, seção 10.3);
   - o cenário valida em outro módulo que não o da pasta.
4. **Bases de consulta** (locais de cada QA, fora do git; podem não existir — se faltar, pergunte ao QA; ler só quando precisar): nomes de telas em `.agents/knowledge/telas-obra-prima.md`, permissões e perfis em `.agents/knowledge/permissoes-obra-prima.md`, regras da DRE em `.agents/knowledge/dre-obra-prima.md`.

---

## Etapa 1 — Ler os requisitos

1. Leia a issue onde o QA indicar: arquivo em `input/` (ex.: `input/current_issue.md`), chat ou PDF.
2. Identifique: chave da issue (ex.: `OPK-12851`), título, módulo, regras de negócio, critérios de aceite (caminho feliz, exceções, validações, layout).

## Etapa 2 — Comparar com os cenários existentes

1. Busque os cenários existentes no Sceno (`listar_cenarios` / `ler_cenario`), no PDF ou `.feature` exportado do AIO, ou em [`features/`](../../../features/).
2. Classifique:
   - ♻️ **Reutilizar**: cobre a funcionalidade sem mudança.
   - ✏️ **Atualizar**: precisa mudar. Mantém a chave original (`CT-XXXX` no Sceno, `OPK-TC-XXX` no AIO).
   - ✨ **Criar**: comportamento sem cenário.
3. Casos duplicados entre si viram um cenário só (regras, seção 10.3).

## Etapa 3 — Relatório de revisão (aguardar o "ok")

Salve em `output/<chave>_revisao.md` (ou `output/Revisao_Gherkin_<pasta>.md` na migração). Se a ferramenta tiver uma tela de revisão própria (artefato, plano), pode usar também, mas o arquivo `.md` é o registro.

Formato:
1. **Título e contexto** (issue, módulo, fonte usada).
2. **Matriz de impacto**: tabela `Mudança | Casos existentes (chave) | Ação`.
3. **Cenários a ATUALIZAR**: `[ATUALIZAR] CT-XXXX`, linha `O que mudou:`, o Gherkin com a tag `@CT-XXXX`, a pré-condição.
4. **Cenários NOVOS**: `[NOVO]`, o Gherkin, a pré-condição.
5. **Dúvidas** (só as que definem o comportamento esperado).
6. **Sinalizações** (ver "Regras de trabalho", item 3).
7. Na migração: lista dos casos que têm anexo ou print no AIO (os anexos ficam no Jira e não vêm no PDF).

Antes de apresentar, rode o validador no relatório e corrija o que ele apontar:
```bash
python3 scripts/gherkin_validator.py output/<chave>_revisao.md
```
**Pare e aguarde o "ok" do QA.** O QA pode responder as dúvidas direto no arquivo.

## Etapa 4 — Gerar os arquivos e validar

1. Depois do "ok", salve o `.feature` em `output/<chave>.feature` no formato do destino (regras, seções 1 e 12):
   - **Sceno**: palavras-chave em português, `# language: pt`, `@CT-XXXX` só nos cenários a atualizar.
   - **AIO**: palavras-chave em inglês, sem cabeçalho de idioma, `@OPK-TC-XXX` nos cenários a atualizar.
2. Rode `python3 scripts/gherkin_validator.py output/<chave>.feature`. Nenhum ERRO pode ficar. Cada ALERTA é corrigido ou justificado ao QA.

## Etapa 5 — Importar no Sceno (só com o "ok" para importar)

- **Pasta:** a pasta é o módulo do título, com prefixo `Web/` (ex.: `Web/Financeiro/Fluxos de caixa`). Validação em mais de um módulo vai para `Web/Geral/<tema>`. Se o `Dado` e a validação estão em outro módulo, o cenário vai para a pasta desse módulo (e você sinaliza). Configurações financeiras ficam em `Web/Configurações/Financeiro`. "Meu plano" fica em `Web/Menu do usuário/Empresa/Meu plano`.
- **O Sceno não cria pasta.** Confira com `listar_cenarios` se ela existe. Se não existir, peça ao QA para criar.
- **Portal do cliente** é outro projeto no Sceno, que a ferramenta não acessa. Esses cenários ficam num documento à parte para o QA.
- **Criar:** `criar_cenario` cria um cenário por chamada. Envie a pré-condição no parâmetro `preCondicao` (o Sceno é a fonte; não crie arquivo local de pré-condições).
- **Atualizar:** `atualizar_cenario` com a chave `CT-XXXX`. Na importação de `.feature`, a tag `@CT-XXXX` também atualiza sem duplicar.
- **Listar:** `listar_cenarios` sem filtro corta em 200 itens. Busque por prefixo de chave (ex.: `busca="CT-17"`).
- **Ciclos:** `adicionar_cenarios_ao_ciclo` (chave do ciclo + lista de chaves) cria a Run com uma execução por linha de Exemplos. Confira com `ler_ciclo`. Se você mudar os Exemplos de um esquema que já está num ciclo, o ciclo não cria as execuções novas: avise o QA para usar "Corrigir execuções desse Esquema" no ciclo.
- No fim, informe ao QA as chaves criadas e atualizadas, com a pasta de cada uma.

---

## Fluxo de migração AIO → Sceno (por pasta)

1. O QA envia, por pasta, o PDF exportado do AIO e, às vezes, um `.feature` com versões mais recentes dos casos.
2. Converta cada caso para as regras, desmembrando o step by step sem perder validação, e unifique os duplicados (regras, seção 10.3).
3. Use os nomes de tela atuais do sistema (regras, seção 8.1). Em caso de dúvida de comportamento, o QA pode pedir para conferir no sistema (homologação).
4. Siga as etapas 3 a 5, com o relatório `Revisao_Gherkin_<pasta>.md`.

## Revisão de cenários já existentes no Sceno

1. Leia os cenários da pasta pedida (`listar_cenarios` por prefixo + `ler_cenario`).
2. Confira cada um com a checklist da seção 14 das regras e com o validador.
3. Monte o relatório só com os cenários que precisam de ajuste (antes/depois), marcando o bloco "Antes" com essa palavra (o validador ignora esses blocos).
4. Aguarde o "ok" antes de atualizar no Sceno.
