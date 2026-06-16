from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Any

from app.configuracao import configuracoes
from app.credenciais_google import google_sheets_configurado
from app.formatacao_planilha import CABECALHOS_PLANILHA, montar_valores_planilha

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


def _garantir_cabecalhos_planilha(planilha) -> None:
    cabecalhos_atuais = [cabecalho.strip() for cabecalho in planilha.row_values(1) if cabecalho.strip()]
    if cabecalhos_atuais != CABECALHOS_PLANILHA:
        planilha.update(
            [CABECALHOS_PLANILHA],
            "A1:I1",
            value_input_option="USER_ENTERED",
        )
        planilha.freeze(rows=1)
        planilha.format(
            "A1:I1",
            {
                "textFormat": {"bold": True},
                "backgroundColor": {"red": 1.0, "green": 0.93, "blue": 0.84},
                "horizontalAlignment": "CENTER",
            },
        )


def _formatar_linha_planilha(planilha, numero_linha: int) -> None:
    intervalo = f"A{numero_linha}:I{numero_linha}"
    planilha.format(
        intervalo,
        {
            "wrapStrategy": "WRAP",
            "verticalAlignment": "TOP",
        },
    )


def tentar_adicionar_planilha_google(linha: dict[str, Any]) -> dict[str, str]:
    if not google_sheets_configurado():
        return {
            "status": "ignorado",
            "mensagem": "Google Sheets nao configurado. Usando CSV local.",
        }

    try:
        import gspread

        from app.credenciais_google import obter_credenciais_google

        credenciais = obter_credenciais_google()
        cliente = gspread.authorize(credenciais)
        planilha = cliente.open_by_key(configuracoes.id_planilha_google.strip()).sheet1

        _garantir_cabecalhos_planilha(planilha)

        valores = montar_valores_planilha(linha)
        planilha.append_row(valores, value_input_option="USER_ENTERED")
        _formatar_linha_planilha(planilha, planilha.row_count)
        return {"status": "ok", "mensagem": "Linha registrada no Google Sheets."}
    except Exception as erro:
        return {"status": "erro", "mensagem": f"Falha ao escrever no Sheets: {erro}"}
