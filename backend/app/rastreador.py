from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Any

from app.configuracao import configuracoes

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


def tentar_adicionar_planilha_google(linha: dict[str, Any]) -> dict[str, str]:
    if not configuracoes.id_planilha_google or not configuracoes.json_conta_servico_google:
        return {
            "status": "ignorado",
            "mensagem": "Google Sheets não configurado. Usando CSV local.",
        }

    try:
        import gspread
        from google.oauth2.service_account import Credentials

        escopos = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        credenciais = Credentials.from_service_account_file(
            configuracoes.json_conta_servico_google,
            scopes=escopos,
        )
        cliente = gspread.authorize(credenciais)
        planilha = cliente.open_by_key(configuracoes.id_planilha_google).sheet1

        cabecalhos = planilha.row_values(1)
        if not cabecalhos:
            planilha.append_row(CABECALHOS_RASTREAMENTO)
            cabecalhos = CABECALHOS_RASTREAMENTO

        valores = [str(linha.get(coluna, "")) for coluna in CABECALHOS_RASTREAMENTO]
        planilha.append_row(valores, value_input_option="USER_ENTERED")
        return {"status": "ok", "mensagem": "Linha registrada no Google Sheets."}
    except Exception as erro:
        return {"status": "erro", "mensagem": f"Falha ao escrever no Sheets: {erro}"}
