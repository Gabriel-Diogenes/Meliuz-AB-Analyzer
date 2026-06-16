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


def _normalizar_json_credenciais(valor: str) -> dict:
    texto = valor.strip()
    if (texto.startswith("'") and texto.endswith("'")) or (texto.startswith('"') and texto.endswith('"')):
        texto = texto[1:-1]
    info = json.loads(texto)
    chave_privada = info.get("private_key")
    if isinstance(chave_privada, str) and "\\n" in chave_privada:
        info["private_key"] = chave_privada.replace("\\n", "\n")
    return info


def _resolver_caminho_credenciais(valor: str) -> Path:
    bruto = Path(valor.strip())
    candidatos = [
        bruto,
        DIRETORIO_BACKEND / bruto,
        Path("/etc/secrets") / bruto.name,
        Path("/etc/secrets") / valor.strip(),
    ]
    vistos: set[Path] = set()
    for caminho in candidatos:
        if caminho in vistos:
            continue
        vistos.add(caminho)
        if caminho.exists():
            return caminho
    raise FileNotFoundError(
        "Arquivo de credenciais nao encontrado. "
        f"Valor configurado: {valor!r}. Caminhos testados: {', '.join(str(c) for c in candidatos)}"
    )


def obter_credenciais_google() -> Credentials:
    valor = configuracoes.json_conta_servico_google.strip()
    if not valor:
        raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON nao configurado.")

    if valor.startswith("{"):
        info = _normalizar_json_credenciais(valor)
        return Credentials.from_service_account_info(info, scopes=ESCOPOS_GOOGLE)

    caminho = _resolver_caminho_credenciais(valor)
    return Credentials.from_service_account_file(str(caminho), scopes=ESCOPOS_GOOGLE)


def diagnosticar_google_sheets() -> dict[str, str]:
    if not google_sheets_configurado():
        return {
            "status": "ignorado",
            "mensagem": "GOOGLE_SHEETS_ID ou GOOGLE_SERVICE_ACCOUNT_JSON nao configurados.",
        }

    try:
        import gspread

        credenciais = obter_credenciais_google()
        cliente = gspread.authorize(credenciais)
        planilha = cliente.open_by_key(configuracoes.id_planilha_google.strip())
        aba = planilha.sheet1
        cabecalhos = aba.row_values(1)
        return {
            "status": "ok",
            "mensagem": f"Conexao OK com a planilha '{planilha.title}' ({aba.row_count} linha(s) na aba principal).",
            "email_conta_servico": credenciais.service_account_email,
            "cabecalhos_linha_1": ", ".join(cabecalhos) if cabecalhos else "(vazio)",
        }
    except Exception as erro:
        return {
            "status": "erro",
            "mensagem": f"Falha ao conectar no Google Sheets: {erro}",
        }
