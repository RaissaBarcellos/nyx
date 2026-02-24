# -*- coding: utf-8 -*-
"""
Nyx - Ferramenta de Avaliação de Interpretabilidade de Dados Governamentais Abertos
-----------------------------------------------------------------------------
Este script avalia automaticamente métricas de interpretabilidade em datasets CSV,
gerando scores, tabela sumarizada e gráfico radar usando matplotlib.
"""

import argparse
import pandas as pd
import numpy as np
import re
import os
from rapidfuzz import fuzz
import matplotlib.pyplot as plt

# -----------------------------
# Função para carregar CSV
# -----------------------------
def carregar_csv(caminho_csv):
    try:
        df = pd.read_csv(caminho_csv, encoding="latin1")
    except Exception as e:
        raise ValueError(f"Erro ao carregar CSV: {e}")
    return df

# -----------------------------
# Métricas de interpretabilidade
# -----------------------------
def completude(df):
    return 1 - df.isnull().sum().sum() / (df.shape[0] * df.shape[1])

def concisao(df):
    score = 1.0
    duplicatas = df.duplicated().sum()
    if duplicatas > 0:
        score -= duplicatas / df.shape[0]
    constantes = sum(df.nunique() <= 1)
    if constantes > 0:
        score -= constantes / df.shape[1]
    return max(0, score)

def atualidade(df):
    score = 0.5
    for col in df.columns:
        if re.search(r"data|date|timestamp", col.lower()):
            try:
                datas = pd.to_datetime(df[col], errors="coerce")
                mais_recente = datas.max()
                if mais_recente:
                    delta = (pd.Timestamp.today() - mais_recente).days
                    score = max(0, 1 - delta / 3650)
            except Exception:
                pass
    return score

def consistencia(df):
    score = 1.0
    for col in df.columns:
        tipos = df[col].map(type).nunique()
        if tipos > 1:
            score -= 0.1
    return max(0, score)

def precisao(df):
    missing = df.isnull().sum().sum()
    score = 1 - missing / (df.shape[0] * df.shape[1])
    return max(0, score)

def informatividade(df):
    score_total = 0
    num_cols = df.select_dtypes(include=[np.number]).columns
    for col in num_cols:
        p_data = df[col].value_counts(normalize=True, dropna=True)
        
        if len(p_data) > 1:
            H = -np.sum(p_data * np.log2(p_data))
            H_max = np.log2(len(p_data))
            H_norm = H / H_max if H_max > 0 else 0
        else:
            H_norm = 0  # coluna constante
        
        score_total += H_norm
    
    if len(num_cols) > 0:
        return score_total / len(num_cols)
    return 0.5

# -----------------------------
# Consistência semântica
# -----------------------------
def verificar_colunas_semelhantes(df, limite=70):
    pares = []
    cols = list(df.columns)
    for i in range(len(cols)):
        for j in range(i+1, len(cols)):
            sim = fuzz.ratio(cols[i].lower(), cols[j].lower())
            if sim > limite:
                pares.append((cols[i], cols[j], sim))
    return pares

def validar_coluna_por_nome(df):
    regras = {
        "cpf": r"^\d{11}$",
        "cnpj": r"^\d{14}$",
        "cep": r"^\d{8}$",
        "data": r"^\d{4}-\d{2}-\d{2}$"
    }
    score = 1.0
    for col in df.columns:
        for chave, padrao in regras.items():
            if chave in col.lower():
                try:
                    match_rate = df[col].astype(str).str.match(padrao).mean()
                    score = min(score, match_rate)
                except Exception:
                    score *= 0.9
    return score

def consistencia_semantica(df):
    score = 1.0
    pares = verificar_colunas_semelhantes(df)
    if pares:
        score -= 0.05 * len(pares)
    score *= validar_coluna_por_nome(df)
    return max(0, min(1, score))

# -----------------------------
# Organização/Estrutura
# -----------------------------
def medir_organizacao_estrutura(df, limiar_nulos=0.5, limiar_constantes=0.95, limiar_correlacao=0.9):
    n_linhas, n_colunas = df.shape
    if n_linhas == 0 or n_colunas == 0:
        return 0.0

    # 1. Chave primária
    chaves = [col for col in df.columns if df[col].is_unique and not df[col].isna().any()]
    score_chave = 1.0 if chaves else 0.0

    # 2. Tipos consistentes
    tipos_por_col = df.apply(lambda c: pd.api.types.infer_dtype(c, skipna=True))
    tipos_validos = tipos_por_col.apply(lambda t: t not in ['mixed', 'mixed-integer'])
    score_tipos = tipos_validos.mean()

    # 3. Colunas com muitos valores nulos
    pct_nulos = df.isna().mean()
    score_nulos = 1 - (pct_nulos > limiar_nulos).mean()

    # 4. Colunas quase constantes
    col_constantes = 0
    for col in df.columns:
        freq_max = df[col].value_counts(normalize=True, dropna=True).max()
        if freq_max >= limiar_constantes:
            col_constantes +=1
    score_constantes = 1 - (col_constantes / n_colunas)

    # 5. Correlação alta
    num_cols = df.select_dtypes(include='number')
    if num_cols.shape[1] <= 1:
        score_corr = 1.0
    else:
        corr_matrix = num_cols.corr().abs()
        n = corr_matrix.shape[0]
        count_altas = ((corr_matrix.where(~np.eye(n, dtype=bool))).stack() > limiar_correlacao).sum() // 2
        max_pares = n*(n-1)//2
        pct_altas = count_altas / max_pares if max_pares > 0 else 0
        score_corr = 1 - pct_altas

    # 6. Razão colunas/linhas
    razao = n_colunas / n_linhas if n_linhas > 0 else 1
    score_razao = 1 if razao <= 1 else max(0, 1 - (razao - 1)/5)

    score_final = (
        0.2 * score_chave +
        0.2 * score_tipos +
        0.15 * score_nulos +
        0.15 * score_constantes +
        0.2 * score_corr +
        0.1 * score_razao
    )
    return round(score_final, 3)

# -----------------------------
# Score final combinado
# -----------------------------
def calcular_score_final(df):
    score_org = medir_organizacao_estrutura(df)
    score_prec = precisao(df)
    score_conc = concisao(df)
    score_cons = consistencia(df)
    score_cons_sem = consistencia_semantica(df)
    score_info = informatividade(df)
    score_final = (
        0.181*score_org +
        0.179*score_prec +
        0.170*completude(df) +
        0.162*score_conc +
        0.158*((score_cons + score_cons_sem)/2) +
        0.150*score_info
    )
    score_final = float(np.clip(score_final, 0, 1))
    
    return score_final, {
        "Organization": score_org,
        "Precision": score_prec,
        "Conciseness": score_conc,
        "Completeness": completude(df),
        "Consistency": score_cons,
        "Semantic Consistency": score_cons_sem,
        "Informativeness": score_info
    }


# -----------------------------
# Gráfico radar usando matplotlib
# -----------------------------
def gerar_radar(scores_dict, output_path="radar.png"):
    import matplotlib.pyplot as plt
    import numpy as np

    # Mapear nomes para inglês
    labels_en = {
        "Organização": "Organization",
        "Precisão": "Precision",
        "Concisão": "Conciseness",
        "Completude": "Completeness",
        "Consistência": "Consistency",
        "Consistência Semântica": "Semantic Consistency",
        "Informatividade": "Informativeness"
    }

    categorias = [labels_en.get(k, k) for k in scores_dict.keys()]
    valores = list(scores_dict.values())
    valores += valores[:1]  # fechar o radar

    n_vars = len(categorias)
    angulos = np.linspace(0, 2 * np.pi, n_vars, endpoint=False).tolist()
    angulos += angulos[:1]

    # Criar figura
    fig, ax = plt.subplots(figsize=(7,7), subplot_kw=dict(polar=True))

    # Plot
    ax.plot(angulos, valores, color='dodgerblue', linewidth=2, linestyle='solid', label="Scores")
    ax.fill(angulos, valores, color='dodgerblue', alpha=0.25)

    # Rótulos
    ax.set_xticks(angulos[:-1])
    ax.set_xticklabels(categorias, fontsize=11)
    ax.set_yticks([0.2,0.4,0.6,0.8,1.0])
    ax.set_yticklabels(["0.2","0.4","0.6","0.8","1.0"], fontsize=10)
    ax.set_ylim(0,1)

    # Estética
    ax.grid(color='gray', linestyle='--', linewidth=0.7)
    ax.spines['polar'].set_visible(True)
    ax.set_title("Dataset Interpretability Profile", fontsize=14, fontweight='bold', y=1.08)

    # Salvar
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()

# -----------------------------
# Função principal
# -----------------------------
def main():
    parser = argparse.ArgumentParser(description="Avaliação de datasets governamentais")
    parser.add_argument("--input", required=True, help="CSV de entrada")
    parser.add_argument("--out", default="resultados", help="Diretório de saída")
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)
    df = carregar_csv(args.input)

    score_final, scores_dict = calcular_score_final(df)

    # salvar CSV
    df_scores = pd.DataFrame([scores_dict])
    df_scores["Score Final"] = score_final
    df_scores.to_csv(os.path.join(args.out, "scores.csv"), index=False)

    # gerar radar
    gerar_radar(scores_dict, os.path.join(args.out, "radar.png"))

    print(f"Scores salvos em {args.out}/scores.csv")
    print(f"Radar salvo em {args.out}/radar.png")
    print(f"Score Final: {score_final:.3f}")

if __name__ == "__main__":
    main()
