from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Any

from app.configuracao import configuracoes
from app.credenciais_google import google_sheets_configurado
from app.formatacao_planilha import montar_valores_planilha
from app.layout_planilha import aplicar_layout_planilha, ultima_linha_com_dados

CABECALHOS_RASTREAMENTO = [
    "data_analise",
    "nome_teste",
    "descricao",
    "parceiro",
    "periodo",
    "variantes",
    "resultado",
    "decisao",
    "arquivo",
]


def _garantir_arquivo_rastreamento(caminho: Path) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    if not caminho.exists():
        with caminho.open("w", newline="", encoding="utf-8-sig") as arquivo:
            escritor = csv.DictWriter(arquivo, fieldnames=CABECALHOS_RASTREAMENTO)
            escritor.writeheader()


def adicionar_linha_rastreamento(
    *,
    nome_teste: str,
    descricao: str,
    parceiro: str,
    periodo: str,
    variantes: str,
    resumo_resultado: str,
    decisao: str,
    nome_arquivo: str,
    caminho_csv: str | None = None,
) -> Path:
    caminho = Path(caminho_csv or configuracoes.caminho_csv_rastreamento)
    _garantir_arquivo_rastreamento(caminho)

    linha = {
        "data_analise": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "nome_teste": nome_teste,
        "descricao": descricao,
        "parceiro": parceiro,
        "periodo": periodo,
        "variantes": variantes,
        "resultado": resumo_resultado,
        "decisao": decisao,
        "arquivo": nome_arquivo,
    }

    with caminho.open("a", newline="", encoding="utf-8-sig") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=CABECALHOS_RASTREAMENTO)
        escritor.writerow(linha)

    return caminho


def ler_linhas_rastreamento(caminho_csv: str | None = None) -> list[dict[str, str]]:
    caminho = Path(caminho_csv or configuracoes.caminho_csv_rastreamento)
    if not caminho.exists():
        return []
    with caminho.open("r", encoding="utf-8-sig") as arquivo:
        return list(csv.DictReader(arquivo))


def _abrir_aba_principal():
    import gspread

    from app.credenciais_google import obter_credenciais_google

    credenciais = obter_credenciais_google()
    cliente = gspread.authorize(credenciais)
    return cliente.open_by_key(configuracoes.id_planilha_google.strip()).sheet1


def reformatar_planilha_google() -> dict[str, str]:
    if not google_sheets_configurado():
        return {
            "status": "ignorado",
            "mensagem": "Google Sheets nao configurado.",
        }

    try:
        planilha = _abrir_aba_principal()
        aplicar_layout_planilha(planilha)
        total = ultima_linha_com_dados(planilha)
        return {
            "status": "ok",
            "mensagem": f"Planilha reformatada ({total} linha(s) com dados).",
        }
    except Exception as erro:
        return {"status": "erro", "mensagem": f"Falha ao reformatar planilha: {erro}"}


def tentar_adicionar_planilha_google(
    linha: dict[str, Any],
    metricas: dict[str, Any] | None = None,
) -> dict[str, str]:
    if not google_sheets_configurado():
        return {
            "status": "ignorado",
            "mensagem": "Google Sheets nao configurado. Usando CSV local.",
        }

    try:
        planilha = _abrir_aba_principal()
        valores = montar_valores_planilha(linha, metricas)
        planilha.append_row(valores, value_input_option="USER_ENTERED", table_range="A1")
        linha_inserida = ultima_linha_com_dados(planilha)
        aplicar_layout_planilha(planilha, ultima_linha=linha_inserida)
        return {"status": "ok", "mensagem": "Linha registrada no Google Sheets."}
    except Exception as erro:
        return {"status": "erro", "mensagem": f"Falha ao escrever no Sheets: {erro}"}
