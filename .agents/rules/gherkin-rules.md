# Regras de escrita dos cenários BDD/Gherkin (Obra Prima)

> **Fonte única do "como escrever".** Toda regra de escrita fica aqui, e só aqui.
> O fluxo de trabalho (ler a issue, comparar, propor, aprovar, importar) está em
> `.agents/skills/test-scenario-generator/SKILL.md`, que aponta para as seções deste arquivo.
> Base: documentação oficial do Gherkin (https://cucumber.io/docs/gherkin/reference) + padrão de QA da empresa.
> Quando o padrão da empresa diverge do Cucumber, a divergência está marcada como **(padrão da empresa)**.

Atue como especialista em BDD e escrita de Gherkin. Escreva cenários novos, revise cenários existentes e corrija conforme as regras abaixo. Antes de entregar, confira cada cenário contra a **checklist da seção 14** e rode o validador (`python3 scripts/gherkin_validator.py <arquivo>`).

---

## 1. Idioma e palavras-chave

- O texto dos cenários é em **português**, a língua dos usuários e especialistas do domínio (princípio do Cucumber).
- As palavras-chave seguem o destino:

| Destino | Palavras-chave | Cabeçalho |
|---|---|---|
| **Sceno** (principal) | `Funcionalidade`, `Cenário`, `Esquema do Cenário`, `Dado`, `Quando`, `Então`, `E`, `Mas`, `Exemplos` | `# language: pt` na 1ª linha do `.feature` |
| **AIO Tests** (Jira) | `Feature`, `Scenario`, `Scenario Outline`, `Given`, `When`, `Then`, `And`, `But`, `Examples` | nenhum (o AIO só aceita inglês e dá erro com `# language: pt`) |

- O Sceno guarda e exibe tudo em português. Ele também aceita palavras-chave em inglês e converte sozinho.
- Nunca misture inglês e português no mesmo arquivo.
- Neste documento os exemplos estão em português (destino Sceno). Para o AIO, troque só as palavras-chave.

## 2. Estrutura do cenário

| Palavra-chave | Uso | Quantidade |
|---|---|---|
| `Dado` | contexto: onde o usuário está e em que estado o sistema está (seção 3) | **exatamente 1** |
| `Quando` | a ação do usuário que dispara o comportamento (seção 4) | **exatamente 1** (padrão da empresa) |
| `Então` | o resultado observável (seção 5) | **exatamente 1** |
| `E` | complemento do `Quando` ou do `Então` | **no máximo 3 no total** do cenário |
| `Mas` | contradiz uma regra ou um resultado: o que **não** acontece, a exceção | **no máximo 1**, sempre o **último passo**, depois dos `E` |
| `*` | item de lista de elementos da tela (seção 9) | não conta no limite de `E` |

- Ordem obrigatória: `Dado` → `Quando` → `Então`, com `E` e `Mas` depois.
- **Nunca `E` (nem `Mas`) logo depois do `Dado`** (padrão da empresa). Junte o contexto numa única frase de `Dado`.
  - ❌ `Dado que o usuário está em "Clientes"` + `E está logado`
  - ✅ `Dado que o usuário está logado em "Clientes"`
- Um `E` depois do `Quando` só completa a mesma ação (ex.: confirmar o que foi feito no `Quando`) e conta no limite de 3 `E`. Se for outro comportamento, é outro cenário.
- **Tamanho:** o Cucumber recomenda **3 a 5 passos** por cenário. Use essa referência para manter o cenário curto e fácil de ler. Pode passar disso (até `Dado` + `Quando` + `Então` + 3 `E` + 1 `Mas`) quando o `E` a mais deixar o cenário mais claro para quem executa.
- **Um cenário = um comportamento.** Comportamentos diferentes (cadastrar, editar, excluir, visualizar) ficam em cenários separados.
- **Cenário independente:** cada cenário roda sozinho, sem depender de outro ter sido executado antes. O que ele precisa já existir vai no `Dado` ou na pré-condição (seção 11).
- **Nunca dois passos com o mesmo texto** no mesmo cenário (regra do Cucumber, e para quem executa o passo repetido é ambíguo).

## 3. `Dado` (contexto)

### 3.1 Usuário como sujeito, com o local exato (padrão da empresa)
- O `Dado` **sempre** começa com `que o usuário…`, para quem executa saber onde precisa estar.
- Diga o local exato: **módulo**, **submódulo** e, quando houver, **modal**, **seção** ou **aba**. Use o nome exato da tela (consulte `.agents/knowledge/telas-obra-prima.md`, se existir na sua máquina).
- Se o contexto é um estado (registro existente, modal aberta, mensagem exibida), o usuário continua sendo o sujeito e o estado entra na mesma frase, junto com o local.
- Se o local não estiver claro na issue ou no plano de testes, **não invente**: sinalize ao QA.
- ✅ `Dado que o usuário está na aba "Dados" de um contrato com situação "Novo" em "Compras/Contratos"`
- ✅ `Dado que o usuário está na aba "Pagamento" do modal de documento a pagar em "Financeiro/Documentos a pagar"`
- ❌ `Dado que existe um contrato com situação "Novo" em "Compras/Contratos"`
- ❌ `Dado que a modal "Novo contrato" está aberta em "Compras/Contratos"`
- ❌ `Dado que o usuário está no sistema`

### 3.2 Contexto, nunca ação
- Boa prática do Cucumber: "Avoid talking about user interaction in Given's". O `Dado` diz **onde o usuário está e em que estado o sistema está**.
- Use verbos de estado (`está`, `possui`, `tem`) e particípios de estado (`aberto`, `fixada`, `em andamento`).
- Nada de verbo de ação no passado (`trocou`, `abriu`, `fechou`, `recebeu`, `enviou`, `clicou`, `recarregou`, `minimizou`, `voltou`, `teve…`) (padrão da empresa, mais rígido que o Cucumber).
- Se o resultado depende de uma ação, ela vai no `Quando`, e o `Dado` fica com o estado de antes dela.
- ❌ `Dado que o usuário trocou o assunto da conversa para outra obra`
- ✅
```gherkin
Cenário: Primo.AI - Validar resposta com o estoque da nova obra ao trocar o assunto da conversa
  Dado que o usuário está no painel do "Primo.AI" com uma conversa sobre uma obra
  Quando troca o assunto da conversa para outra obra, perguntando sobre o estoque sem citar o nome dela
  Então o assistente responde com o estoque da nova obra
```

## 4. `Quando` (ação)

- **Exatamente 1 `Quando` por cenário** (padrão da empresa). Mais de uma ação principal = dividir em cenários.
- O sujeito é o usuário, explícito (`Quando o usuário clica…`) ou implícito (`Quando clica…`). Nunca o sistema, um registro ou uma tela.
  - ❌ `Quando o sistema carrega os itens do contrato`
- Estilo **procedural/imperativo** (padrão da empresa): o sistema é complexo e tem testes de layout, então o passo diz o que o usuário faz na tela (`clica em "Pesquisar"`, `seleciona "Sim" em "Estoque disponível"`). O Cucumber prefere o estilo declarativo; aqui ele vale só para não descrever detalhe técnico (seção 8.4).

## 5. `Então` (resultado observável)

- O resultado tem que ser **algo que o usuário vê na tela**: mensagem, valor, campo, status, grid, botão habilitado ou desabilitado (Cucumber: "observable output", e não algo escondido dentro do sistema, como um registro no banco de dados).
- O `Então` e os `E` de resultado podem ter o sistema como sujeito (`Então o sistema exibe…`).
- Proibido resultado vago: "funciona corretamente", "sem erros", "normalmente", "segue o fluxo padrão". Diga o que aparece.
  - ❌ `Então o sistema salva sem erros`
  - ✅ `Então o sistema exibe a mensagem "Registro salvo com sucesso"`
- Proibido resultado técnico: ❌ `Então o servidor retorna 403 para a requisição` → ✅ `Então o sistema não exibe a conversa`

## 6. Título do cenário

- Formato: `<Módulo/Submódulo> - <verbo> <o que é validado>`.
- Comece com **"Validar …"** quando o cenário confere uma regra de negócio ou um comportamento.
- Use o **verbo da funcionalidade** quando o cenário executa uma ação do sistema: "Cadastrar …", "Editar …", "Excluir …", "Exportar …", "Executar …".
- Cenário de layout: o título **tem a palavra "Layout"** (ex.: `Estoque/Insumos - Validar layout dos filtros do submódulo`).
- O módulo do título é o nome no sistema (ex.: `Financeiro/Fluxos de caixa`, `Financeiro/Documentos a receber` no plural). Validação que passa por vários módulos usa `Geral/<tema> - …`. Itens do menu do usuário: `Menu do usuário/Empresa/Meu plano - …`.
- No título, **" e " é permitido** (a proibição vale só para os passos).
- Elementos da tela no título também vão entre aspas (seção 8.1).
- Nunca use variável `<…>` no título de um `Esquema do Cenário`. O título é estático; as variáveis ficam nos passos.
- Nunca use etiquetas `[Declarativo]` / `[Procedural]`.
- ✅ `Financeiro/Fluxos de caixa - Validar pesquisa com filtros combinados`
- ✅ `Financeiro/Fluxos de caixa - Exportar fluxo por contas gerenciais analítico ou sintético`
- ❌ `Financeiro/Fluxos de caixa - Filtros combinados` (não diz o que é validado)
- ❌ `Esquema do Cenário: APP/Construtor/Dia a dia - Criação offline de registro <rdo>`

## 7. `Esquema do Cenário` e `Exemplos`

As tabelas do projeto são as tabelas de `Exemplos` do `Esquema do Cenário`.

- Os `Exemplos` só variam **dados** (objeto da ação, área, perfil, faixa). A ação do `Quando` é a mesma em todas as linhas.
  - ❌ `Quando <navegacao>` com linhas "troca de página" / "abre outra conversa" → um cenário por ação.
  - ✅ `Quando pede <pedido> de uma obra…` com linhas "o resumo financeiro", "o saldo de estoque".
- Não use variável no lugar do estado do `Dado` (`Dado que o usuário <acao>…`) quando os Exemplos forem ações.
- **Cabeçalho com nomes claros**, que digam o que varia (`perfil`, `tipo_de_documento`, `local`), nunca `a`, `x`, `1`.
- **Toda `<variável>` dos passos tem uma coluna** com o mesmo nome nos Exemplos, e toda coluna é usada nos passos.
- Toda linha tem o mesmo número de células do cabeçalho.
- **Esquema com uma linha só de Exemplos vira `Cenário`.**
- Deixe claro o **objetivo** do teste e use a frase só como exemplo trocável: `uma pergunta de <tipo_de_assunto>, como "<exemplo>"`.
- Esquema confuso (texto longo nas células): **enxugue a tabela**, sem dividir em vários cenários.
- Não use tabela dentro de um passo (Data Table do Cucumber) nem Doc String (`"""`). Para listar elementos, use `*` (seção 9).

## 8. Escrita dos passos

### 8.1 Aspas duplas nos elementos do sistema
- Todo elemento da interface citado como aparece na tela (módulo, aba, botão, campo, mensagem, status, dropdown…) vai **entre aspas duplas**, no título, nos passos e nos Exemplos.
- ✅ `Dado que o usuário está na aba "Dados" do modal de uma obra no módulo "Obras"`
- ❌ `Dado que o usuário está na aba Dados do modal de uma obra no módulo Obras`
- Use o nome **como está no sistema hoje**. Se o caso antigo (AIO, PDF) tiver outra grafia, vale a do sistema (ex.: "Venc.", "Ignorar contas de cliente", separador "Empresas").

### 8.2 Sem a conjunção "e" nos passos (padrão da empresa)
- Nunca use `" e "` (nem `" and "`) solto no texto de um passo. Use vírgula, "com", "com a" ou reescreva. O "E" é só a palavra-chave.
- Exceção: nome exato da tela entre aspas que já tem "e" (ex.: `"Serviços e insumos"`, `"Adiantamento e faturamento direto"`).
- No título o " e " é permitido.
- ✅ `Então o sistema exibe o título, o número do contrato`
- ❌ `Então o sistema exibe o título e o número do contrato`

### 8.3 Terceira pessoa
- ✅ `Dado que o usuário está na tela de "Clientes"`
- ❌ `Dado que estou na tela de Clientes`

### 8.4 Linguagem do usuário (sem termos técnicos)
- Escreva como o usuário enxerga o sistema, sem termos técnicos: requisição, endpoint, ID, servidor, API, banco de dados, payload, status HTTP, JSON, console, DevTools, Datadog, Postman.
- **Não escreva cenário técnico** (rotina chamada por URL, DevTools, Datadog, Postman, conferência direta no banco). Se a issue pedir esse tipo de validação, **sinalize a quem está criando os cenários** para essa pessoa avaliar se precisa mesmo, e como.

### 8.5 Não engessar dados de teste
- Não fixe massa de dados nos passos (nomes de obras, empresas, valores, datas, logins, e-mails, CPF/CNPJ).
- Descreva a **característica** do dado, para o cenário rodar com qualquer massa que atenda à condição.
- ✅ `Dado que o usuário possui acesso somente a uma obra da empresa`
- ❌ `Dado que o usuário possui acesso somente à obra "Residencial Aurora"`
- ✅ `excluir um registro existente` (e não "excluir a conta a pagar 123").
- Aceito: "Documento X", "Ordem de compra X" nos Exemplos, em que o X representa o número exibido no sistema.

## 9. Cenários de layout

Cenário de layout confere **o que aparece na tela e como**: colunas, campos, botões, filtros, abas, ordem de exibição, valores padrão, cores, tooltips, legendas, cabeçalho de relatório.

- O título tem a palavra **"Layout"** (seção 6).
- Para listar vários elementos, o `Então`/`E` diz o **tipo de elemento** e termina com `:`. Logo abaixo, cada elemento vem numa linha `*`, entre aspas, na ordem da tela.
- Separe um `E` por tipo de elemento (campos, botões, colunas…).
- Os itens `*` não contam no limite de 3 `E`.
```gherkin
Cenário: Estoque/Insumos - Validar layout dos filtros do submódulo
  Dado que o usuário está em "Estoque/Insumos" com o painel de pesquisa lateral aberto
  Quando visualiza a lista de filtros disponíveis
  Então o sistema exibe os campos de filtro na ordem:
    * "Obra/Almoxarifado"
    * "Controla estoque por"
    * "Categoria de insumo"
    * "Insumo"
    * "Código"
    * "Estoque disponível"
    * "Estoque abaixo do mínimo"
  E apresenta o campo "Estoque disponível" selecionado por padrão como "Sim"
  E apresenta o campo "Estoque abaixo do mínimo" selecionado por padrão como "Ambos"
```
- Ao converter um caso antigo, nunca perca validação de layout (seção 10.3).

## 10. Escopo e cobertura

### 10.1 100% do escopo da issue
- Todos os critérios de aceite, regras de negócio, exceções e validações da issue precisam estar cobertos por algum cenário.

### 10.2 Regra de negócio, nunca bug
- Todo cenário valida uma **regra de negócio** ou um **comportamento** que será testado de novo (regressão).
- Nunca crie cenário só para reproduzir um bug específico ou um comportamento pontual. Se o caso de origem (AIO, issue) for só isso, não crie: sinalize ao QA.

### 10.3 Desmembrar sem perder validação
- Caso step by step com várias validações vira **quantos cenários forem necessários** (um comportamento por cenário).
- Nunca perca validação de regra de negócio ou de layout (colunas, campos, mensagens, tooltips, cores, totais, status, ordem).
- Antes de entregar, confira cada passo e cada resultado esperado do caso original: todos precisam estar em algum cenário (ou na pré-condição, se forem só preparação). Só resultados vagos ("sem erros", "fluxo padrão") podem ser descartados, e isso vai sinalizado no relatório.
- Casos duplicados (mesma validação em dois casos) viram um cenário só.

### 10.4 Dúvida de "como reproduzir"
- Dúvida sobre **como simular** uma situação em homologação (gerar consumo, configurar limite baixo, simular virada de mês, simular falha) **não adia o cenário**.
- Escreva o cenário com o comportamento esperado, coloque o estado necessário na pré-condição e **sinalize a quem está criando os testes** para essa pessoa ver com o dev como reproduzir.
- Dúvida que define o **comportamento esperado** (a regra de negócio) é diferente: vai para a lista de dúvidas antes de fechar o cenário.

## 11. Pré-condição

- A pré-condição é o estado que precisa existir antes do teste. No Sceno ela vai no **campo próprio de pré-condição** (não no Gherkin).
- **Não use `Contexto:`/`Background:`.** No Sceno ele não vira pré-condição: os passos são copiados para o início de cada cenário. O que seria contexto compartilhado vai na pré-condição de cada cenário.
- Linhas de descrição abaixo do título também não viram pré-condição (são ignoradas).
- Escreva em **frases naturais** (2 a 3 frases), dizendo o estado que deve existir:
  - ✅ "A empresa do usuário deve ter o plano do Primo.AI ativo. Deve existir uma obra criada na empresa do usuário com nome parecido ao de uma obra de outra empresa."
  - ❌ "Empresa com plano ativo. Uma obra com nome parecido."
- **Acesso:** informe as **permissões** necessárias (nome exato da permissão, coluna "Pesquisar"/"Única" e agrupador, conforme `.agents/knowledge/permissoes-obra-prima.md`, se existir na sua máquina), em vez de citar só o perfil. Cite o agrupador ou a permissão principal, sem listar uma por uma.
- A pré-condição também segue a regra de não engessar dados (seção 8.5).

## 12. Formato do arquivo `.feature`

- **`Funcionalidade:` / `Feature:` vazio**, sem texto depois e sem descrição abaixo (Sceno e AIO não têm descrição; o AIO usaria o texto como "Description").
- Nenhuma linha de descrição abaixo do título do cenário: vá direto para o `Dado`.
- **Nunca tag acima da `Funcionalidade:`** (ex.: `@OPK-12336`).
- Tags acima do cenário só para vincular a um caso existente:
  - **Sceno:** `@CT-XXXX` atualiza o cenário existente na importação, sem duplicar. Cenário novo vai sem tag.
  - **AIO:** `@OPK-TC-XXX`.
- **Indentação de 2 espaços** por nível (cenário 2, passos 4, itens `*` e tabelas 6), sem tab.
- Comentário (`#`) só no início da linha. No Gherkin, um `#` no meio do passo vira parte do texto.
- `# language: pt` na primeira linha quando as palavras-chave estiverem em português (seção 1).
- Não use `Regra:`/`Rule:`. O agrupamento por regra de negócio é feito pela pasta e pelo título.

## 13. Exemplo completo (Sceno)

```gherkin
# language: pt
Funcionalidade:

  Cenário: Obras - Validar recarregamento do grid ao fechar o modal depois de salvar a edição
    Dado que o usuário está no modal de uma obra com alteração salva no módulo "Obras"
    Quando fecha o modal da obra pelo botão do cabeçalho
    Então o grid do módulo "Obras" recarrega com os dados atualizados
    Mas não atualiza o grid enquanto o modal estiver aberto

  @CT-1234
  Esquema do Cenário: Compras/Contratos - Validar bloqueio da edição de contrato por situação
    Dado que o usuário está na aba "Dados" de um contrato com situação "<situacao>" em "Compras/Contratos"
    Quando tenta editar o campo "Objeto"
    Então o sistema mantém o campo "Objeto" bloqueado para edição
    Exemplos:
      | situacao  |
      | Aprovado  |
      | Encerrado |
```

## 14. Checklist antes de entregar

Para cada cenário:
1. [ ] 1 `Dado`, 1 `Quando`, 1 `Então`, no máximo 3 `E` e 1 `Mas` (último passo).
2. [ ] Nenhum `E`/`Mas` logo depois do `Dado`.
3. [ ] `Dado` começa com "que o usuário", diz o local exato e não tem ação.
4. [ ] `Quando` é ação do usuário. `Então` é algo visível na tela, sem resultado vago.
5. [ ] Título no formato `<Módulo> - Validar …`/verbo, com "Layout" se for de layout, sem `<…>`.
6. [ ] Elementos da tela entre aspas, com o nome atual do sistema.
7. [ ] Sem " e " nos passos, sem 1ª pessoa, sem termo técnico, sem dado engessado.
8. [ ] Esquema: variáveis com coluna, colunas com nome claro, mais de uma linha, ação igual em todas.
9. [ ] Cenário independente, sem passo repetido, validando regra de negócio (não bug).
10. [ ] Pré-condição em frases naturais, com permissões, sem dado engessado.
11. [ ] Nenhuma validação do caso original ou da issue ficou de fora.
12. [ ] `python3 scripts/gherkin_validator.py <arquivo>` sem ERRO. Cada ALERTA foi corrigido ou justificado no relatório.
