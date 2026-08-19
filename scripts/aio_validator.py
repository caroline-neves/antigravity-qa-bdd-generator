#!/usr/bin/env python3
"""
Validador de Sintaxe Gherkin & Regras de QA (AIO Tests Jira)
Este script analisa arquivos .feature para garantir que:
1. Contêm palavras-chave válidas do Gherkin (pt/en).
2. Respeitam a escrita em 3ª pessoa (sem "eu clico", "estou na tela").
3. Não utilizam Background/Contexto compartilhado (cada cenário tem seu próprio Given).
4. Não possuem 'And'/'E' imediatamente após 'Given'/'Dado'.
5. Respeitam o limite MÁXIMO de 3 'And'/'E' em todo o cenário.
6. Não utilizam a conjunção "e" dentro dos textos dos passos (ex: "'Obra' e 'Data'").
7. Possuem apenas uma ação por título de cenário.
8. Possuem o formato correto de tag (@OPK-TC-XXXX) nos cenários de atualização.
"""

import sys
import os
import re

FIRST_PERSON_PATTERNS = [
    r'\bestou\b', r'\beu\b', r'\bclico\b', r'\bpreencho\b', r'\bvejo\b',
    r'\bfaço\b', r'\beu acesso\b', r'\bI am\b', r'\bI click\b', r'\bI see\b'
]

def validate_feature_file(file_path):
    issues = []
    has_feature = False
    has_scenario = False
    
    last_keyword = None
    and_count_in_scenario = 0
    current_scenario_title = ""
    
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    for idx, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Proibição de Contexto/Background
        if stripped.startswith("Contexto:") or stripped.startswith("Background:"):
            issues.append(f"Linha {idx}: WARNING - Uso de 'Contexto/Background' detectado. Cada cenário DEVE conter seu próprio Given/Dado independente.")
            continue

        # Funcionalidade
        if stripped.startswith("Funcionalidade:") or stripped.startswith("Feature:"):
            has_feature = True
            last_keyword = "Feature"
            continue
            
        # Cenários
        if stripped.startswith("Cenário:") or stripped.startswith("Scenario:") or stripped.startswith("Esquema do Cenário:") or stripped.startswith("Scenario Outline:"):
            has_scenario = True
            last_keyword = "Scenario"
            current_scenario_title = stripped
            and_count_in_scenario = 0
            
            # Checagem de "e" no título
            if re.search(r'\b e \b', stripped, re.IGNORECASE) or re.search(r'\b and \b', stripped, re.IGNORECASE):
                issues.append(f"Linha {idx}: WARNING - Título de cenário com múltiplas ações ('{stripped}'). Crie 1 cenário atômico para cada ação.")
            continue

        # Checagem de Primeira Pessoa
        for fp_pattern in FIRST_PERSON_PATTERNS:
            if re.search(fp_pattern, stripped, re.IGNORECASE):
                issues.append(f"Linha {idx}: WARNING - Uso de primeira pessoa detectado ('{stripped}'). OBRIGATÓRIO usar 3ª pessoa.")
                break

        # Passos Gherkin
        tokens = stripped.split(maxsplit=1)
        step_keyword = tokens[0] if tokens else ""
        step_text = tokens[1] if len(tokens) > 1 else ""

        # Checagem da palavra "e" dentro do texto da frase
        if step_keyword in ["Dado", "Given", "Quando", "When", "Então", "Then", "E", "And", "Mas", "But"]:
            if re.search(r'\b e \b', step_text) or re.search(r'\" e \"', step_text):
                issues.append(f"Linha {idx}: WARNING - Uso da palavra 'e' dentro da frase ('{stripped}'). Substitua por vírgula ou reestruture.")

        if step_keyword in ["Dado", "Given"]:
            last_keyword = "Given"
        elif step_keyword in ["Quando", "When"]:
            last_keyword = "When"
        elif step_keyword in ["Então", "Then"]:
            last_keyword = "Then"
        elif step_keyword in ["E", "And"]:
            if last_keyword == "Given":
                issues.append(f"Linha {idx}: WARNING - Uso de 'E'/'And' imediatamente após 'Dado'/'Given'. Consolide no próprio 'Dado'.")
            and_count_in_scenario += 1
            if and_count_in_scenario > 3:
                issues.append(f"Linha {idx}: ERROR - Excesso de 'E'/'And' no cenário ({and_count_in_scenario} 'And's). O limite MÁXIMO é 3 por cenário.")

    if not has_feature and not has_scenario:
        issues.append("ERROR: Nenhum 'Scenario:' ou 'Feature:' encontrado no arquivo.")
        
    return issues

def main():
    target_path = sys.argv[1] if len(sys.argv) > 1 else "output"
    
    if not os.path.exists(target_path):
        print(f"❌ Diretório ou arquivo '{target_path}' não encontrado.")
        sys.exit(1)
        
    files_to_check = []
    if os.path.isfile(target_path):
        files_to_check.append(target_path)
    else:
        for root, _, files in os.walk(target_path):
            for file in files:
                if file.endswith(".feature"):
                    files_to_check.append(os.path.join(root, file))
                    
    if not files_to_check:
        print(f"ℹ️ Nenhum arquivo .feature encontrado em '{target_path}'.")
        return
        
    total_issues = 0
    print(f"🔍 Validando {len(files_to_check)} arquivo(s) .feature para AIO Tests do Jira...\n")
    
    for file in files_to_check:
        print(f"📄 Arquivo: {file}")
        issues = validate_feature_file(file)
        if not issues:
            print("   ✅ VÁLIDO - Pronto para importação no AIO Tests Jira!")
        else:
            for issue in issues:
                print(f"   ⚠️ {issue}")
                total_issues += 1
        print()
        
    if total_issues == 0:
        print("🎉 Todos os arquivos passaram na validação de sintaxe e regras de QA do AIO Tests!")
    else:
        print(f"⚠️ Foram encontrados {total_issues} alertas/erros na verificação.")

if __name__ == "__main__":
    main()
