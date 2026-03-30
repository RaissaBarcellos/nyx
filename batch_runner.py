# -*- coding: utf-8 -*-
"""
Batch Runner - Execução em massa do Nyx Ranking
"""

import os
import pandas as pd
from nyx_ranking import carregar_csv, calcular_score_final, gerar_radar


def processar_multiplos_datasets(pasta_entrada, pasta_saida="resultados_batch"):
    os.makedirs(pasta_saida, exist_ok=True)

    resultados = []

    for arquivo in os.listdir(pasta_entrada):
        if arquivo.endswith(".csv"):
            caminho = os.path.join(pasta_entrada, arquivo)

            try:
                df = carregar_csv(caminho)
                score_final, scores_dict = calcular_score_final(df)

                # -----------------------------
                # Salvar radar individual
                # -----------------------------
                nome_base = os.path.splitext(arquivo)[0]
                caminho_radar = os.path.join(pasta_saida, f"radar_{nome_base}.png")
                gerar_radar(scores_dict, caminho_radar)

                # -----------------------------
                # Guardar resultado
                # -----------------------------
                linha = {"dataset": arquivo, "Score Final": score_final}
                linha.update(scores_dict)
                resultados.append(linha)

                print(f"[OK] {arquivo} processado")

            except Exception as e:
                print(f"[ERRO] {arquivo}: {e}")

    if not resultados:
        print("Nenhum dataset válido encontrado.")
        return

    # -----------------------------
    # DataFrame consolidado
    # -----------------------------
    df_resultados = pd.DataFrame(resultados)
    df_resultados.to_csv(os.path.join(pasta_saida, "resultados_consolidados.csv"), index=False)

    # -----------------------------
    # MÉDIA GLOBAL
    # -----------------------------
    medias = df_resultados.drop(columns=["dataset"]).mean().to_dict()

    df_medias = pd.DataFrame([medias])
    df_medias.to_csv(os.path.join(pasta_saida, "medias_gerais.csv"), index=False)

    # -----------------------------
    # Radar médio
    # -----------------------------
    gerar_radar(medias, os.path.join(pasta_saida, "radar_medio.png"))

    print("\n✔ Processamento concluído!")
    print(f"Resultados salvos em: {pasta_saida}")


if __name__ == "__main__":
    processar_multiplos_datasets("datasets")