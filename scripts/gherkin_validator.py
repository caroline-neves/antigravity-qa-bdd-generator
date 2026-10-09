#!/usr/bin/env python3
"""
Validador dos cenários Gherkin (Sceno / AIO Tests)

Confere as regras de `.agents/rules/gherkin-rules.md` que dá para checar
automaticamente. Não substitui a revisão: local exato, cobertura da issue
e boa parte do "dado engessado" continuam sendo conferidos por quem escreve.

Uso:
  python3 scripts/gherkin_validator.py [arquivo_ou_pasta ...]   (padrão: output/)

Lê arquivos `.feature` e os blocos ```gherkin de arquivos `.md` (relatórios de
revisão). Nos `.md`, blocos marcados como "Antes" são ignorados.

Níveis:
  ERRO    quebra a estrutura do Gherkin ou uma regra obrigatória
  ALERTA  provável quebra de regra: revisar
  AVISO   recomendação
Sai com código 1 quando há ERRO ou ALERTA (útil em CI).
"""

import os
import re
import sys

# ─── Palavras-chave (inglês e português, conforme a doc do Cucumber) ─────────

HEADERS = {
    'Feature': 'feature', 'Funcionalidade': 'feature', 'Característica': 'feature', 'Caracteristica': 'feature',
    'Background': 'background', 'Contexto': 'background', 'Cenário de Fundo': 'background',
    'Cenario de Fundo': 'background', 'Fundo': 'background',
    'Rule': 'rule', 'Regra': 'rule',
    'Scenario Outline': 'outline', 'Scenario Template': 'outline', 'Esquema do Cenário': 'outline',
    'Esquema do Cenario': 'outline', 'Delineação do Cenário': 'outline', 'Delineacao do Cenario': 'outline',
    'Scenario': 'scenario', 'Example': 'scenario', 'Cenário': 'scenario', 'Cenario': 'scenario', 'Exemplo': 'scenario',
    'Examples': 'examples', 'Scenarios': 'examples', 'Exemplos': 'examples', 'Cenários': 'examples', 'Cenarios': 'examples',
}
HEADER_LANG = {k: ('en' if k in ('Feature', 'Background', 'Rule', 'Scenario Outline', 'Scenario Template',
                                 'Scenario', 'Example', 'Examples', 'Scenarios') else 'pt') for k in HEADERS}
HEADER_RE = re.compile(r'^(' + '|'.join(sorted(map(re.escape, HEADERS), key=len, reverse=True)) + r'):\s*(.*)$')

STEPS = {
    'Given': 'given', 'When': 'when', 'Then': 'then', 'And': 'and', 'But': 'but',
    'Dado': 'given', 'Dada': 'given', 'Dados': 'given', 'Dadas': 'given', 'Quando': 'when',
    'Então': 'then', 'Entao': 'then', 'E': 'and', 'Mas': 'but',
}
STEP_LANG = {k: ('en' if k in ('Given', 'When', 'Then', 'And', 'But') else 'pt') for k in STEPS}
STEP_RE = re.compile(r'^(' + '|'.join(sorted(map(re.escape, STEPS), key=len, reverse=True)) + r')\s+(.*)$')
STAR_RE = re.compile(r'^\*\s+(.*)$')

# ─── Padrões de conteúdo ────────────────────────────────────────────────────

FIRST_PERSON = re.compile(r'\b(estou|eu|clico|preencho|vejo|faço|seleciono|digito|tenho|meu|minha|I am|I click|I see)\b', re.I)

# When/Quando com outro sujeito que não o usuário
WHEN_OUTRO_SUJEITO = re.compile(r'^(o sistema|a tela|a modal|o modal|a página|o grid|a lista|o contrato|o registro|'
                                r'o documento|a aba|existe|há |é exibid|são exibid|aparece)', re.I)

# Given/Dado sem ação: pretérito perfeito (-ou, -eu, -iu) e alguns irregulares
GIVEN_ACAO_IRREGULARES = {'teve', 'fez', 'pôs', 'deu', 'veio', 'foi', 'disse', 'trouxe'}
GIVEN_NAO_ACAO = {'europeu', 'chapéu', 'troféu', 'museu', 'pigmeu', 'plebeu', 'liceu', 'judeu', 'moscou'}

TERMOS_TECNICOS = re.compile(r'\b(requisiç(ão|ões)|endpoint|api|servidor|banco de dados|payload|status http|http|json|'
                             r'id|console|devtools|datadog|postman|backend|back-end|frontend|front-end)\b', re.I)

RESULTADO_VAGO = re.compile(r'\b(sem erros?|funcion(a|ar|am) (corretamente|normalmente)|fluxo padrão|normalmente)\b', re.I)

DADO_ENGESSADO = [
    (re.compile(r'[\w.+-]+@[\w-]+\.[\w.]+'), 'e-mail'),
    (re.compile(r'\b\d{1,2}/\d{1,2}/\d{2,4}\b'), 'data'),
    (re.compile(r'R\$\s?\d'), 'valor'),
    (re.compile(r'\b\d{3}\.\d{3}\.\d{3}-\d{2}\b'), 'CPF'),
    (re.compile(r'\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b'), 'CNPJ'),
]

TAG_CONHECIDA = re.compile(r'^@(CT-\d+|OPK-TC-\d+)$')
PLACEHOLDER = re.compile(r'<([^<>]+)>')


def sem_aspas(texto):
    """Remove o que está entre aspas (nome exato de tela) e os <placeholders>."""
    return PLACEHOLDER.sub('', re.sub(r'"[^"]*"', '', texto))


def given_action_verbs(texto):
    achados = []
    for palavra in re.findall(r'[a-záéíóúâêôãõç]+', sem_aspas(texto).lower()):
        if palavra in GIVEN_NAO_ACAO:
            continue
        if palavra in GIVEN_ACAO_IRREGULARES or (len(palavra) >= 5 and re.search(r'(ou|eu|iu)$', palavra)):
            achados.append(palavra)
    return achados


# ─── Leitura do arquivo ─────────────────────────────────────────────────────

class Bloco:
    """Trecho Gherkin: um arquivo .feature inteiro ou um bloco ```gherkin de um .md."""
    def __init__(self, path, lines, offset=0, fragmento=False):
        self.path = path
        self.lines = lines          # linhas do trecho
        self.offset = offset        # linha do arquivo onde o trecho começa (para .md)
        self.fragmento = fragmento  # bloco de .md: não exige Feature nem cabeçalho de idioma


def blocos_do_arquivo(path):
    with open(path, encoding='utf-8') as f:
        lines = f.read().splitlines()
    if path.endswith('.feature'):
        return [Bloco(path, lines)]
    blocos, dentro, inicio, atual = [], False, 0, []
    for i, line in enumerate(lines):
        cerca = line.strip()
        if not dentro and re.match(r'^```\s*(gherkin|feature|cucumber)\b', cerca, re.I):
            contexto = ' '.join(lines[max(0, i - 3):i]).lower()
            dentro, inicio, atual = True, i + 1, []
            ignorar = 'antes' in contexto and 'depois' not in contexto
        elif dentro and cerca.startswith('```'):
            if not ignorar:
                blocos.append(Bloco(path, atual, offset=inicio, fragmento=True))
            dentro = False
        elif dentro:
            atual.append(line)
    return blocos


# ─── Validação ──────────────────────────────────────────────────────────────

class Resultado:
    def __init__(self):
        self.itens = []

    def add(self, nivel, linha, msg):
        self.itens.append((nivel, linha, msg))


def validar_cenario(c, r):
    """Regras de um cenário já lido (c = dict com título, passos, exemplos…)."""
    ln, titulo, tipo = c['linha'], c['titulo'], c['tipo']
    passos = c['passos']

    # Título
    if not titulo:
        r.add('ERRO', ln, 'Cenário sem título.')
    else:
        if ' - ' not in titulo:
            r.add('ALERTA', ln, f'Título fora do formato "<Módulo/Submódulo> - <verbo> <o que>": "{titulo}".')
        else:
            primeira = titulo.split(' - ', 1)[1].split()[0] if titulo.split(' - ', 1)[1].split() else ''
            if primeira and not re.search(r'[aei]r$', primeira.lower()):
                r.add('ALERTA', ln, f'Título deve começar com "Validar …" ou com o verbo da funcionalidade depois do " - " '
                                    f'(encontrado "{primeira}"). Ex.: "Validar layout …", "Cadastrar …".')
        if PLACEHOLDER.search(titulo):
            r.add('ALERTA', ln, 'Título com variável <…>. Use variáveis só nos passos.')
        if re.search(r'\[(Declarativo|Procedural)\]', titulo, re.I):
            r.add('ALERTA', ln, 'Remova a etiqueta [Declarativo]/[Procedural] do título.')
        m = TERMOS_TECNICOS.search(sem_aspas(titulo))
        if m:
            r.add('ALERTA', ln, f'Termo técnico no título ("{m.group(0)}"). Use a linguagem do usuário.')
        if titulo.count('"') % 2:
            r.add('ALERTA', ln, 'Aspas desbalanceadas no título.')

    if c['descricao']:
        r.add('ALERTA', c['descricao'], 'Texto de descrição abaixo do cenário. O Sceno/AIO não têm descrição: vá direto para o Dado.')

    # Tags
    tags = c['tags']
    for t, tl in tags:
        if not TAG_CONHECIDA.match(t):
            r.add('AVISO', tl, f'Tag "{t}" fora do padrão (@CT-XXXX no Sceno, @OPK-TC-XXX no AIO).')
    if sum(1 for t, _ in tags if t.startswith('@CT-')) > 1:
        r.add('ALERTA', ln, 'Mais de uma tag @CT-XXXX no mesmo cenário.')

    # Estrutura dos passos
    principais = [p for p in passos if p['kw'] != '*']
    if not principais:
        r.add('ERRO', ln, 'Cenário sem passos.')
        return
    contagem = {k: sum(1 for p in principais if p['kw'] == k) for k in ('given', 'when', 'then', 'and', 'but')}
    if principais[0]['kw'] != 'given':
        r.add('ERRO', principais[0]['linha'], 'O cenário deve começar com Dado/Given.')
    for k, nome in (('given', 'Dado/Given'), ('when', 'Quando/When'), ('then', 'Então/Then')):
        if contagem[k] != 1:
            r.add('ERRO', ln, f'O cenário deve ter exatamente 1 {nome} (tem {contagem[k]}).')
    if contagem['and'] > 3:
        r.add('ERRO', ln, f'{contagem["and"]} E/And no cenário. O máximo é 3.')
    if contagem['but'] > 1:
        r.add('ALERTA', ln, f'{contagem["but"]} Mas/But no cenário. Use no máximo 1.')
    if len(principais) > 5:
        r.add('AVISO', ln, f'{len(principais)} passos. O Cucumber recomenda 3 a 5; mantenha só se o E/And deixar o cenário mais claro.')

    fase = None        # given → when → then
    anterior = None
    textos = {}
    lista = {}
    for i, p in enumerate(passos):
        kw, texto, pl = p['kw'], p['texto'], p['linha']
        if kw == '*':
            if anterior is None or not (anterior['texto'].rstrip().endswith(':') or anterior['kw'] == '*'):
                r.add('ALERTA', pl, 'Lista com "*" deve vir logo depois de um passo terminado em ":" (ex.: E exibe os botões:).')
        else:
            if kw in ('given', 'when', 'then'):
                ordem = {'given': 0, 'when': 1, 'then': 2}
                if fase is not None and ordem[kw] < ordem[fase]:
                    r.add('ERRO', pl, 'Ordem dos passos deve ser Dado → Quando → Então.')
                fase = kw
            if kw in ('and', 'but') and fase == 'given':
                r.add('ALERTA', pl, 'E/Mas logo depois do Dado. Junte o contexto no próprio Dado.')
            if kw == 'but':
                if fase != 'then':
                    r.add('ALERTA', pl, 'Mas/But só vem depois do Então (para contradizer uma regra ou resultado).')
                if any(q['kw'] not in ('*',) for q in passos[i + 1:]):
                    r.add('ALERTA', pl, 'Mas/But deve ser o último passo, depois dos E/And.')
            if texto.rstrip().endswith(':') and (i + 1 >= len(passos) or passos[i + 1]['kw'] != '*'):
                r.add('ALERTA', pl, 'Passo termina em ":" mas não tem lista "*" logo abaixo.')

        # Passo repetido no cenário; itens "*" só se repetem dentro da mesma lista
        if kw != '*':
            lista = {}
            chave = re.sub(r'\s+', ' ', texto.strip().lower())
            if chave in textos:
                r.add('ALERTA', pl, f'Passo repetido no mesmo cenário (igual à linha {textos[chave]}).')
            else:
                textos[chave] = pl
        else:
            chave = re.sub(r'\s+', ' ', texto.strip().lower())
            if chave in lista:
                r.add('ALERTA', pl, f'Item repetido na lista (igual à linha {lista[chave]}).')
            else:
                lista[chave] = pl

        validar_texto_passo(p, fase, r)
        anterior = p

    # Esquema do Cenário / Exemplos
    usados = set()
    for p in passos:
        usados.update(x.strip() for x in PLACEHOLDER.findall(p['texto']))
    exemplos = c['exemplos']
    if tipo == 'scenario':
        if exemplos:
            r.add('ERRO', ln, 'Cenário com Exemplos. Use Esquema do Cenário/Scenario Outline.')
        if usados:
            r.add('ERRO', ln, f'Cenário com variáveis {sorted(usados)}. Use Esquema do Cenário com Exemplos.')
        return
    if not exemplos:
        r.add('ERRO', ln, 'Esquema do Cenário sem Exemplos.')
        return
    colunas = set()
    linhas_dados = 0
    for ex in exemplos:
        if not ex['tabela']:
            r.add('ERRO', ex['linha'], 'Bloco de Exemplos sem tabela.')
            continue
        cab, *dados = ex['tabela']
        colunas.update(cab['cels'])
        for col in cab['cels']:
            if len(col) <= 1 or col.isdigit():
                r.add('AVISO', cab['linha'], f'Coluna "{col}" pouco clara. Use um nome que diga o que varia.')
        for d in dados:
            if len(d['cels']) != len(cab['cels']):
                r.add('ERRO', d['linha'], f'Linha com {len(d["cels"])} células; o cabeçalho tem {len(cab["cels"])}.')
        # Nos relatórios .md, "(mesmas linhas do …)" resume uma tabela já mostrada
        if any(all(re.fullmatch(r'\(.*\)', x) for x in d['cels'] if x) for d in dados):
            linhas_dados += 2
        linhas_dados += len(dados)
        # Dado com <variável> cujos valores são ações
        for p in passos:
            m = re.match(r'que o usuário <([^>]+)>', p['texto'])
            if p['kw'] == 'given' and m and m.group(1) in cab['cels']:
                pos = cab['cels'].index(m.group(1))
                for d in dados:
                    if pos < len(d['cels']) and given_action_verbs(d['cels'][pos]):
                        r.add('ALERTA', d['linha'], f'Dado recebe uma ação dos Exemplos ("{d["cels"][pos]}"). A ação vai no Quando.')
                        break
    if linhas_dados == 0:
        r.add('ERRO', ln, 'Exemplos sem linhas de dados.')
    elif linhas_dados == 1:
        r.add('ALERTA', ln, 'Esquema com uma linha de Exemplos só. Transforme em Cenário.')
    for v in sorted(usados - colunas):
        r.add('ERRO', ln, f'Variável <{v}> sem coluna nos Exemplos.')
    for v in sorted(colunas - usados):
        r.add('AVISO', ln, f'Coluna "{v}" dos Exemplos não é usada nos passos.')
    for p in passos:
        if p['kw'] == 'when' and re.fullmatch(r'\s*(o usuário\s+)?<[^>]+>.*', p['texto']) and \
                not re.match(r'\s*(o usuário\s+)?<[^>]+>\s+\S', p['texto']):
            r.add('ALERTA', p['linha'], 'Quando é só uma variável: os Exemplos variam a ação. Crie um cenário por ação.')


def validar_texto_passo(p, fase, r):
    kw, texto, pl = p['kw'], p['texto'], p['linha']
    livre = sem_aspas(texto)

    if re.search(r'(?<!\S)(e|and)(?!\S)', livre):
        r.add('ALERTA', pl, 'Conjunção "e" no texto do passo. Use vírgula, "com" ou reescreva (o "E" é só a palavra-chave).')
    m = FIRST_PERSON.search(livre)
    if m:
        r.add('ALERTA', pl, f'Primeira pessoa ("{m.group(0)}"). Escreva em 3ª pessoa.')
    m = TERMOS_TECNICOS.search(livre)
    if m:
        r.add('ALERTA', pl, f'Termo técnico ("{m.group(0)}"). Use a linguagem do usuário.')
    for padrao, nome in DADO_ENGESSADO:
        if padrao.search(texto):
            r.add('ALERTA', pl, f'Possível dado engessado ({nome}). Descreva a característica do dado, não o valor.')
            break
    if texto.count('"') % 2:
        r.add('ALERTA', pl, 'Aspas desbalanceadas.')

    if kw == 'given':
        if not re.match(r'que o usuário\b', texto, re.I):
            r.add('ALERTA', pl, 'Dado deve começar com "que o usuário…", com o local exato e o estado na mesma frase.')
        acoes = given_action_verbs(texto)
        if acoes:
            r.add('ALERTA', pl, f'Dado com ação ({", ".join(acoes)}). O Dado é só o estado inicial; a ação vai no Quando.')
    if kw == 'when' and WHEN_OUTRO_SUJEITO.match(texto):
        r.add('ALERTA', pl, 'Quando com outro sujeito. Escreva como ação do usuário ("clica…" ou "o usuário clica…").')
    if fase == 'then' and kw in ('then', 'and', 'but', '*'):
        m = RESULTADO_VAGO.search(livre)
        if m:
            r.add('ALERTA', pl, f'Resultado vago ("{m.group(0)}"). Diga o que o usuário vê na tela.')


def validar_bloco(b, r):
    # Bloco de .md só com passos soltos (trecho antes/depois): não há cenário para validar
    def tem_cenario(l):
        m = HEADER_RE.match(l.strip())
        return m and HEADERS[m.group(1)] in ('scenario', 'outline', 'feature')
    if b.fragmento and not any(tem_cenario(l) for l in b.lines):
        return []
    lang_header = None
    langs = set()
    feature_vista = False
    cenarios = []
    atual = None
    tags_pendentes = []
    zona = None          # 'feature' | 'scenario' | 'steps' | 'examples'
    ultimo_passo = None
    primeira_linha_util = True

    def fechar():
        if atual:
            cenarios.append(atual)

    for i, raw in enumerate(b.lines):
        ln = b.offset + i + 1
        s = raw.strip()
        if not s:
            continue
        if '\t' in raw[:len(raw) - len(raw.lstrip())]:
            r.add('AVISO', ln, 'Indentação com tab. Use 2 espaços por nível.')

        if s.startswith('#'):
            m = re.match(r'#\s*language:\s*(\S+)', s)
            if m:
                if not primeira_linha_util:
                    r.add('ALERTA', ln, '"# language:" deve ser a primeira linha do arquivo.')
                lang_header = m.group(1).lower()
            continue
        primeira_linha_util = False

        if s.startswith('@'):
            if not feature_vista and not b.fragmento:
                r.add('ALERTA', ln, 'Tag acima da Funcionalidade/Feature. Não use tag na Feature.')
            else:
                tags_pendentes += [(t, ln) for t in s.split() if t.startswith('@')]
            continue

        mh = HEADER_RE.match(s)
        if mh:
            kw, texto = mh.group(1), mh.group(2).strip()
            tipo = HEADERS[kw]
            langs.add(HEADER_LANG[kw])
            if tipo == 'feature':
                if feature_vista:
                    r.add('ERRO', ln, 'Mais de uma Funcionalidade/Feature no arquivo.')
                feature_vista = True
                zona = 'feature'
                if texto:
                    r.add('ALERTA', ln, f'Texto depois de "{kw}:" ("{texto}"). Deixe vazio: Sceno/AIO não têm descrição.')
            elif tipo == 'background':
                r.add('ALERTA', ln, f'"{kw}:" não é usado. O que é preparação vai na pré-condição do cenário.')
                zona = 'background'
            elif tipo == 'rule':
                r.add('ALERTA', ln, f'"{kw}:" não é usado. O agrupamento por regra é feito pela pasta e pelo título.')
            elif tipo in ('scenario', 'outline'):
                fechar()
                atual = {'linha': ln, 'titulo': texto, 'tipo': tipo, 'passos': [], 'exemplos': [],
                         'tags': tags_pendentes, 'descricao': None}
                tags_pendentes = []
                zona = 'scenario'
                ultimo_passo = None
            elif tipo == 'examples':
                if not atual:
                    r.add('ERRO', ln, 'Exemplos fora de um cenário.')
                else:
                    atual['exemplos'].append({'linha': ln, 'tabela': []})
                zona = 'examples'
                tags_pendentes = []
            continue

        if s.startswith('|'):
            cels = [c.strip() for c in re.split(r'(?<!\\)\|', s.strip())[1:-1]]
            if zona == 'examples' and atual and atual['exemplos']:
                atual['exemplos'][-1]['tabela'].append({'linha': ln, 'cels': cels})
            elif zona == 'steps':
                r.add('ALERTA', ln, 'Tabela no passo. Tabelas só nos Exemplos; para listar elementos use "*".')
            else:
                r.add('ERRO', ln, 'Tabela fora de Exemplos.')
            continue

        if s.startswith('"""') or s.startswith('```'):
            r.add('ALERTA', ln, 'Doc String (""") não é usada. Escreva o texto no passo ou use lista "*".')
            continue

        ms = STEP_RE.match(s)
        mstar = STAR_RE.match(s)
        if ms or mstar:
            if zona == 'background':
                continue
            if not atual:
                r.add('ERRO', ln, 'Passo fora de um cenário.')
                continue
            if zona == 'examples':
                r.add('ERRO', ln, 'Passo depois dos Exemplos.')
            if ms:
                kw = STEPS[ms.group(1)]
                langs.add(STEP_LANG[ms.group(1)])
                texto = ms.group(2)
            else:
                kw, texto = '*', mstar.group(1)
            ultimo_passo = {'kw': kw, 'texto': texto, 'linha': ln}
            atual['passos'].append(ultimo_passo)
            zona = 'steps'
            continue

        # Linha que não é palavra-chave
        if zona == 'scenario' and atual and not atual['passos']:
            atual['descricao'] = atual['descricao'] or ln
        elif zona == 'feature':
            r.add('ALERTA', ln, 'Texto de descrição abaixo da Feature. Deixe só "Feature:"/"Funcionalidade:".')
        else:
            r.add('ERRO', ln, f'Linha não reconhecida como Gherkin: "{s}".')
    fechar()

    # Idioma
    if len(langs) > 1:
        r.add('ERRO', b.offset + 1, 'Palavras-chave em inglês misturadas com português no mesmo arquivo.')
    elif langs == {'pt'} and lang_header != 'pt' and not b.fragmento:
        r.add('ERRO', b.offset + 1, 'Palavras-chave em português exigem "# language: pt" na primeira linha.')
    elif langs == {'en'} and lang_header and lang_header != 'en':
        r.add('ERRO', b.offset + 1, f'"# language: {lang_header}" com palavras-chave em inglês. Remova o cabeçalho ou traduza.')

    if not b.fragmento and not feature_vista:
        r.add('ERRO', b.offset + 1, 'Falta "Funcionalidade:"/"Feature:" no início do arquivo.')
    if not cenarios:
        r.add('ERRO', b.offset + 1, 'Nenhum cenário encontrado.')

    for c in cenarios:
        validar_cenario(c, r)
    return cenarios


def arquivos_alvo(alvos):
    for alvo in alvos:
        if os.path.isfile(alvo):
            yield alvo
        elif os.path.isdir(alvo):
            for raiz, _, nomes in os.walk(alvo):
                for n in sorted(nomes):
                    if n.endswith(('.feature', '.md')):
                        yield os.path.join(raiz, n)
        else:
            print(f'❌ "{alvo}" não encontrado.')
            sys.exit(2)


def main():
    alvos = sys.argv[1:] or ['output']
    titulos = {}
    total = {'ERRO': 0, 'ALERTA': 0, 'AVISO': 0}
    arquivos = list(arquivos_alvo(alvos))
    if not arquivos:
        print('ℹ️ Nenhum .feature ou .md encontrado.')
        return 0

    print(f'🔍 Validando {len(arquivos)} arquivo(s)...\n')
    for path in arquivos:
        blocos = blocos_do_arquivo(path)
        if not blocos:
            continue
        r = Resultado()
        for b in blocos:
            for c in validar_bloco(b, r):
                if c['titulo'] and path.endswith('.feature'):
                    titulos.setdefault(c['titulo'], []).append(f'{path}:{c["linha"]}')
        print(f'📄 {path}')
        if not r.itens:
            print('   ✅ Sem problemas encontrados.')
        for nivel, linha, msg in sorted(r.itens, key=lambda x: x[1]):
            icone = {'ERRO': '❌', 'ALERTA': '⚠️ ', 'AVISO': 'ℹ️ '}[nivel]
            print(f'   {icone} Linha {linha}: {nivel} - {msg}')
            total[nivel] += 1
        print()

    for t, locais in titulos.items():
        if len(locais) > 1:
            print(f'⚠️  ALERTA - Título repetido em {", ".join(locais)}: "{t}"')
            total['ALERTA'] += 1

    print(f'Resumo: {total["ERRO"]} erro(s), {total["ALERTA"]} alerta(s), {total["AVISO"]} aviso(s).')
    return 1 if total['ERRO'] or total['ALERTA'] else 0


if __name__ == '__main__':
    sys.exit(main())
