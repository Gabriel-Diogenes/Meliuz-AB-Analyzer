from __future__ import annotations

import re
from typing import Any

import google.generativeai as genai

from app.prompts_padrao import PROMPT_ANALISE_PADRAO, PROMPT_SISTEMA_PADRAO


def _extrair_decisao(relatorio_markdown: str) -> str:
    padroes = [
        r"##\s*Decisão\s*\n+(.*?)(?:\n##|\Z)",
        r"\*\*Decisão:\*\*\s*(.+)",
        r"Decisão final:\s*(.+)",
    ]
    for padrao in padroes:
        correspondencia = re.search(padrao, relatorio_markdown, flags=re.IGNORECASE | re.DOTALL)
        if correspondencia:
            decisao = correspondencia.group(1).strip()
            return re.sub(r"\s+", " ", decisao)[:500]
    linhas = [linha.strip() for linha in relatorio_markdown.splitlines() if "escalar" in linha.lower()]
    return linhas[-1][:500] if linhas else "Ver relatório completo."


def analisar_com_gemini(
    *,
    chave_api: str,
    nome_modelo: str,
    prompt_sistema: str,
    prompt_analise: str,
    nome_teste: str,
    descricao_teste: str,
    contexto_metricas: str,
) -> dict[str, Any]:
    if not chave_api.strip():
        raise ValueError("GEMINI_API_KEY nao configurada no arquivo backend/.env.")

    genai.configure(api_key=chave_api.strip())
    modelo = genai.GenerativeModel(
        model_name=nome_modelo,
        system_instruction=prompt_sistema or PROMPT_SISTEMA_PADRAO,
    )

    prompt_usuario = (prompt_analise or PROMPT_ANALISE_PADRAO).format(
        nome_teste=nome_teste,
        descricao_teste=descricao_teste,
        contexto_metricas=contexto_metricas,
    )

    resposta = modelo.generate_content(
        prompt_usuario,
        generation_config={
            "temperature": 0.3,
            "max_output_tokens": 8192,
        },
    )

    relatorio = (resposta.text or "").strip()
    if not relatorio:
        raise RuntimeError("O modelo não retornou conteúdo. Verifique a chave e o modelo selecionado.")

    return {
        "relatorio_markdown": relatorio,
        "decisao": _extrair_decisao(relatorio),
        "prompt_enviado": prompt_usuario,
        "modelo": nome_modelo,
    }


def validar_chave_api(chave_api: str, nome_modelo: str) -> dict[str, str]:
    genai.configure(api_key=chave_api.strip())
    modelo = genai.GenerativeModel(model_name=nome_modelo)
    resposta = modelo.generate_content("Responda apenas: OK")
    texto = (resposta.text or "").strip()
    return {"status": "ok", "mensagem": f"Conexão validada. Resposta: {texto[:50]}"}
