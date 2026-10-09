# Gerador de cenários de teste BDD/Gherkin (Obra Prima)

Projeto para gerar, revisar e migrar cenários de teste em Gherkin com qualquer assistente de IA, sempre com o mesmo padrão de qualidade. O destino principal é o **Sceno**; o **AIO Tests** (Jira) continua suportado.

## Como funciona

1. Você passa a issue do Jira (num arquivo em `input/`, no chat ou em PDF).
2. A IA compara com os cenários existentes e monta um relatório de revisão em `output/`: matriz de impacto, cenários a atualizar, cenários novos, dúvidas e sinalizações.
3. Você revisa e dá o **"ok"**. Nada é criado no Sceno, no AIO ou no Jira antes disso.
4. A IA gera o `.feature`, roda o validador e, com um novo "ok", importa no Sceno.

## Onde está cada coisa

| Arquivo | Para quê |
|---|---|
| [`AGENTS.md`](AGENTS.md) | Porta de entrada para qualquer IA (o `CLAUDE.md` aponta para ele) |
| [`.agents/rules/gherkin-rules.md`](.agents/rules/gherkin-rules.md) | **Todas as regras de escrita** (fonte única) |
| [`.agents/skills/test-scenario-generator/SKILL.md`](.agents/skills/test-scenario-generator/SKILL.md) | O fluxo de trabalho, da issue à importação |
| `.agents/knowledge/` | Bases de consulta locais (telas, permissões, DRE). Fora do git: cada QA mantém a sua |
| [`scripts/gherkin_validator.py`](scripts/gherkin_validator.py) | Validador das regras que dá para checar automaticamente |
| `features/` | Exemplo de cenários no padrão |
| `input/` | Issue em análise (local, fora do git) |
| `output/` | Relatórios de revisão e `.feature` gerados (local, fora do git) |

Para mudar uma regra, edite **só** o `gherkin-rules.md` (e, se for checável, o validador).

## Como usar

Em qualquer IA com acesso ao repositório, peça em linguagem natural, por exemplo:

> Gerar cenários de teste para a issue OPK-XXXXX (colada no chat ou salva em input/)

Se a IA não ler o `AGENTS.md` sozinha, peça antes: *"Leia o AGENTS.md e siga as instruções."*

## Validador

Roda em qualquer terminal com Python 3, sem IA nem dependências:

```bash
python3 scripts/gherkin_validator.py output/              # pasta inteira
python3 scripts/gherkin_validator.py output/OPK-123.feature
python3 scripts/gherkin_validator.py output/OPK-123_revisao.md   # blocos ```gherkin do relatório
```

- **ERRO**: estrutura quebrada ou regra obrigatória (ex.: 2 `Quando`, variável sem coluna).
- **ALERTA**: provável quebra de regra, a revisar (ex.: " e " no passo, `Dado` com ação, termo técnico).
- **AVISO**: recomendação (ex.: mais de 5 passos).

Sai com código 1 quando há ERRO ou ALERTA, então pode rodar em CI (GitHub Actions, GitLab CI, Jenkins).
O validador não substitui a revisão: local exato, cobertura da issue e parte do "dado engessado" dependem de quem escreve.
