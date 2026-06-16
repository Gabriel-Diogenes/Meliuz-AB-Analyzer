from __future__ import annotations

import json
from pathlib import Path

from google.oauth2.service_account import Credentials

from app.configuracao import DIRETORIO_BACKEND, configuracoes

ESCOPOS_GOOGLE = (
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
)


def google_sheets_configurado() -> bool:
    return bool(configuracoes.id_planilha_google.strip() and configuracoes.json_conta_servico_google.strip())


def obter_credenciais_google() -> Credentials:
    valor = configuracoes.json_conta_servico_google.strip()
    if not valor:
        raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON nao configurado.")

    if valor.startswith("{"):
        info = json.loads(valor)
        return Credentials.from_service_account_info(info, scopes=ESCOPOS_GOOGLE)

    caminho = Path(valor)
    if not caminho.is_absolute():
        caminho = DIRETORIO_BACKEND / caminho
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo de credenciais nao encontrado: {caminho}")
    return Credentials.from_service_account_file(str(caminho), scopes=ESCOPOS_GOOGLE)
