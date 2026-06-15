from __future__ import annotations

import json
from typing import Any

import pandas as pd


def _divisao_segura(numerador: float, denominador: float) -> float | None:
    if denominador == 0:
        return None
    return numerador / denominador


def calcular_metricas(dataframe: pd.DataFrame) -> dict[str, Any]:
    data_inicio = dataframe["Data"].min()
    data_fim = dataframe["Data"].max()
    dias = (data_fim - data_inicio).days + 1
    parceiro = dataframe["Parceiro"].mode().iloc[0]
    grupos = sorted(dataframe["Grupos de usuários"].unique())

    metricas_por_grupo: list[dict[str, Any]] = []
    serie_diaria = dataframe.groupby(["Data", "Grupos de usuários"], as_index=False).agg(
        compradores=("compradores", "sum"),
        comissao=("comissão_num", "sum"),
        cashback=("cashback_num", "sum"),
        gmv=("vendas totais_num", "sum"),
    )

    for grupo in grupos:
        dados_grupo = dataframe[dataframe["Grupos de usuários"] == grupo]
        total_compradores = int(dados_grupo["compradores"].sum())
        total_comissao = float(dados_grupo["comissão_num"].sum())
        total_cashback = float(dados_grupo["cashback_num"].sum())
        total_gmv = float(dados_grupo["vendas totais_num"].sum())
        receita_liquida = total_comissao - total_cashback
        dias_ativos = dados_grupo["Data"].nunique()

        metricas_por_grupo.append(
            {
                "grupo": grupo,
                "compradores": total_compradores,
                "gmv": round(total_gmv, 2),
                "comissao": round(total_comissao, 2),
                "cashback": round(total_cashback, 2),
                "receita_liquida": round(receita_liquida, 2),
                "ticket_medio": round(_divisao_segura(total_gmv, total_compradores) or 0, 2),
                "cashback_rate_sobre_gmv": round((_divisao_segura(total_cashback, total_gmv) or 0) * 100, 2),
                "comissao_rate_sobre_gmv": round((_divisao_segura(total_comissao, total_gmv) or 0) * 100, 2),
                "margem_liquida_sobre_gmv": round((_divisao_segura(receita_liquida, total_gmv) or 0) * 100, 2),
                "compradores_por_dia": round(_divisao_segura(total_compradores, dias_ativos) or 0, 2),
                "dias_ativos": int(dias_ativos),
            }
        )

    qualidade_dados: list[str] = []
    totais_compradores = [grupo["compradores"] for grupo in metricas_por_grupo]
    if max(totais_compradores) > 0:
        desbalanceamento = max(totais_compradores) / max(min(totais_compradores), 1)
        if desbalanceamento > 1.5:
            qualidade_dados.append(
                f"Desbalanceamento entre grupos: razão max/min de compradores = {desbalanceamento:.2f}x."
            )

    grupos_gmv_zero = [grupo["grupo"] for grupo in metricas_por_grupo if grupo["gmv"] == 0]
    if grupos_gmv_zero:
        qualidade_dados.append(f"Grupo(s) com GMV zero: {', '.join(grupos_gmv_zero)}.")

    if dias < 7:
        qualidade_dados.append(f"Período curto ({dias} dia(s)); resultados podem ser inconclusivos.")

    return {
        "parceiro": parceiro,
        "periodo": {
            "inicio": data_inicio.strftime("%Y-%m-%d"),
            "fim": data_fim.strftime("%Y-%m-%d"),
            "dias": int(dias),
        },
        "grupos": grupos,
        "metricas_por_grupo": metricas_por_grupo,
        "qualidade_dados": qualidade_dados,
        "serie_diaria": serie_diaria.assign(Data=serie_diaria["Data"].dt.strftime("%Y-%m-%d")).to_dict(orient="records"),
        "totais": {
            "linhas": int(len(dataframe)),
            "compradores": int(dataframe["compradores"].sum()),
            "gmv": round(float(dataframe["vendas totais_num"].sum()), 2),
        },
    }


def metricas_para_contexto_prompt(metricas: dict[str, Any], avisos: list[str]) -> str:
    conteudo = {
        "avisos_preprocessamento": avisos,
        "metricas": metricas,
    }
    return json.dumps(conteudo, ensure_ascii=False, indent=2)
