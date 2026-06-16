from __future__ import annotations

import re
from typing import Any

CABECALHOS_PLANILHA = [
    "Data da analise",
    "Nome do teste",
    "Descricao",
    "Parceiro",
    "Periodo",
    "Variantes",
    "Resultado",
    "Decisao",
    "Arquivo",
]


def _limpar_markdown(texto: str) -> str:
    limpo = str(texto or "")
    limpo = re.sub(r"\*\*(.+?)\*\*", r"\1", limpo)
    limpo = re.sub(r"\*(.+?)\*", r"\1", limpo)
    limpo = re.sub(r"^#+\s*", "", limpo, flags=re.MULTILINE)
    limpo = re.sub(r"^\s*[-*]\s+", "", limpo, flags=re.MULTILINE)
    limpo = limpo.replace("→", " ate ")
    return " ".join(limpo.split())


def _extrair_grupo(texto: str) -> str:
    correspondencia = re.search(
        r"(?:escalar\s+(?:para\s+100%?\s+(?:do\s+tr[aá]fego\s+(?:do\s+)?)?)?)?(Grupo\s+\d+)",
        texto,
        flags=re.IGNORECASE,
    )
    if correspondencia:
        return correspondencia.group(1)
    if "inconclusivo" in texto.lower():
        return "Inconclusivo"
    return ""


def _primeira_frase(texto: str, limite: int = 220) -> str:
    limpo = _limpar_markdown(texto)
    if not limpo:
        return ""
    partes = re.split(r"(?<=[.!?])\s+", limpo)
    resumo = partes[0].strip()
    if len(partes) > 1 and len(resumo) < 80:
        resumo = f"{resumo} {partes[1].strip()}".strip()
    return resumo[:limite]


def formatar_decisao_planilha(decisao: str) -> str:
    limpo = _limpar_markdown(decisao)
    grupo = _extrair_grupo(limpo)
    if grupo:
        resto = re.sub(rf"(?i){re.escape(grupo)}", " ", limpo)
        resto = re.sub(r"(?i)justificativa:?\s*", "", resto)
        resto = re.sub(r"(?i)proximos passos.*", "", resto).strip(" :-.")
        frase = _primeira_frase(resto, 200)
        if frase:
            return f"Escalar {grupo}. {frase}"[:280]
        return f"Escalar {grupo}."
    return _primeira_frase(limpo, 280)


def formatar_resultado_planilha(resultado: str, decisao: str) -> str:
    limpo = _limpar_markdown(resultado)
    if limpo:
        return _primeira_frase(limpo, 280)
    return formatar_decisao_planilha(decisao)


def montar_valores_planilha(linha: dict[str, Any]) -> list[str]:
    decisao = formatar_decisao_planilha(str(linha.get("decisao", "")))
    resultado = formatar_resultado_planilha(str(linha.get("resultado", "")), str(linha.get("decisao", "")))
    return [
        str(linha.get("data_analise", "")),
        str(linha.get("nome_teste", "")),
        str(linha.get("descricao", "")),
        str(linha.get("parceiro", "")),
        _limpar_markdown(str(linha.get("periodo", ""))),
        str(linha.get("variantes", "")),
        resultado,
        decisao,
        str(linha.get("arquivo", "")),
    ]
