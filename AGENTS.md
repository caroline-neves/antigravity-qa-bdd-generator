# Instruções para agentes de IA

Este repositório gera e revisa cenários de teste BDD/Gherkin do Obra Prima (destino: Sceno ou AIO Tests).
Vale para qualquer IA (Claude, Antigravity, Cursor, Copilot, Codex, ChatGPT…).

Antes de escrever, revisar ou importar qualquer cenário, leia **por inteiro**:

1. [`.agents/rules/gherkin-rules.md`](.agents/rules/gherkin-rules.md): todas as regras de escrita (fonte única).
2. [`.agents/skills/test-scenario-generator/SKILL.md`](.agents/skills/test-scenario-generator/SKILL.md): o fluxo de trabalho, da issue à importação.

Inegociáveis:
- Nunca crie, altere, exclua ou importe nada no Sceno, no AIO ou no Jira sem o "ok" explícito do QA para aquela ação.
- Antes de entregar, confira a checklist (seção 14 das regras) e rode `python3 scripts/gherkin_validator.py <arquivo>`.
- Bases de consulta em `.agents/knowledge/` (locais, fora do git; podem não existir): ler só quando precisar (telas, permissões, DRE).
