import re
from typing import Any

import pandas as pd

COLUNAS_OBRIGATORIAS = [
    "Data",
    "Grupos de usuários",
    "Parceiro",
    "compradores",
    "comissão",
    "cashback",
    "vendas totais",
]


def converter_real(valor: Any) -> float:
    if pd.isna(valor):
        return 0.0
    if isinstance(valor, (int, float)):
        return float(valor)
    texto = str(valor).strip()
    if not texto:
        return 0.0
    texto = texto.replace("R$", "").replace("\xa0", " ").strip()
    texto = texto.replace(".", "").replace(",", ".")
    texto = re.sub(r"[^\d.\-]", "", texto)
    try:
        return float(texto) if texto else 0.0
    except ValueError:
        return 0.0


def carregar_dataset_ab(bytes_arquivo: bytes, nome_arquivo: str) -> tuple[pd.DataFrame, list[str]]:
    avisos: list[str] = []

    try:
        dataframe = pd.read_csv(pd.io.common.BytesIO(bytes_arquivo))
    except Exception:
        dataframe = pd.read_csv(pd.io.common.BytesIO(bytes_arquivo), sep=";", encoding="utf-8-sig")

    dataframe.columns = [coluna.strip() for coluna in dataframe.columns]
    faltando = [coluna for coluna in COLUNAS_OBRIGATORIAS if coluna not in dataframe.columns]
    if faltando:
        raise ValueError(f"Colunas obrigatórias ausentes: {', '.join(faltando)}")

    dataframe["Data"] = pd.to_datetime(dataframe["Data"], errors="coerce")
    datas_invalidas = dataframe["Data"].isna().sum()
    if datas_invalidas:
        avisos.append(f"{datas_invalidas} linha(s) com data inválida foram descartadas.")
        dataframe = dataframe.dropna(subset=["Data"])

    for coluna in ["comissão", "cashback", "vendas totais"]:
        dataframe[f"{coluna}_num"] = dataframe[coluna].apply(converter_real)

    dataframe["compradores"] = pd.to_numeric(dataframe["compradores"], errors="coerce").fillna(0).astype(int)

    for coluna in ["comissão_num", "cashback_num", "vendas totais_num"]:
        negativos = (dataframe[coluna] < 0).sum()
        if negativos:
            avisos.append(f"{negativos} valor(es) negativo(s) encontrado(s) em {coluna.replace('_num', '')}.")

    dataframe["Grupos de usuários"] = dataframe["Grupos de usuários"].astype(str).str.strip()
    dataframe["Parceiro"] = dataframe["Parceiro"].astype(str).str.strip()

    if dataframe.empty:
        raise ValueError(f"O arquivo '{nome_arquivo}' não contém dados válidos após a limpeza.")

    return dataframe, avisos
