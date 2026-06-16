from __future__ import annotations

from datetime import datetime
from typing import Any

from app.analisador_csv import carregar_dataset_ab
from app.configuracao import configuracoes
from app.gerador_relatorio import montar_resumo_resultado, salvar_relatorio
from app.metricas import calcular_metricas, metricas_para_contexto_prompt
from app.prompts_padrao import PROMPT_ANALISE_PADRAO, PROMPT_SISTEMA_PADRAO
from app.rastreador import adicionar_linha_rastreamento, tentar_adicionar_planilha_google
from app.servico_gemini import analisar_com_gemini


def executar_analise_completa(
    *,
    conteudo_csv: bytes,
    nome_arquivo: str,
    chave_gemini: str,
    modelo: str,
    nome_teste: str,
    descricao_teste: str,
    prompt_sistema: str,
    prompt_analise: str,
) -> dict[str, Any]:
    if not conteudo_csv:
        raise ValueError("Arquivo CSV vazio.")

    dataframe, avisos = carregar_dataset_ab(conteudo_csv, nome_arquivo or "dataset.csv")
    metricas = calcular_metricas(dataframe)
    contexto_metricas = metricas_para_contexto_prompt(metricas, avisos)

    resultado_ia = analisar_com_gemini(
        chave_api=chave_gemini,
        nome_modelo=modelo,
        prompt_sistema=prompt_sistema or PROMPT_SISTEMA_PADRAO,
        prompt_analise=prompt_analise or PROMPT_ANALISE_PADRAO,
        nome_teste=nome_teste,
        descricao_teste=descricao_teste,
        contexto_metricas=contexto_metricas,
    )

    caminho_md, caminho_html = salvar_relatorio(
        diretorio_relatorios=configuracoes.diretorio_relatorios,
        nome_teste=nome_teste,
        relatorio_markdown=resultado_ia["relatorio_markdown"],
    )

    resumo_resultado = montar_resumo_resultado(resultado_ia["relatorio_markdown"], resultado_ia["decisao"])
    periodo = f"{metricas['periodo']['inicio']} → {metricas['periodo']['fim']}"
    variantes = ", ".join(metricas["grupos"])

    caminho_rastreamento = adicionar_linha_rastreamento(
        nome_teste=nome_teste,
        descricao=descricao_teste,
        parceiro=metricas["parceiro"],
        periodo=periodo,
        variantes=variantes,
        resumo_resultado=resumo_resultado,
        decisao=resultado_ia["decisao"],
        nome_arquivo=nome_arquivo or "dataset.csv",
    )

    resultado_planilha = tentar_adicionar_planilha_google(
        {
            "data_analise": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "nome_teste": nome_teste,
            "descricao": descricao_teste,
            "parceiro": metricas["parceiro"],
            "periodo": periodo,
            "variantes": variantes,
            "resultado": resumo_resultado,
            "decisao": resultado_ia["decisao"],
            "arquivo": nome_arquivo or "dataset.csv",
        },
        metricas=metricas,
    )

    return {
        "sucesso": True,
        "nome_teste": nome_teste,
        "metricas": metricas,
        "avisos": avisos,
        "relatorio_markdown": resultado_ia["relatorio_markdown"],
        "decisao": resultado_ia["decisao"],
        "resumo_resultado": resumo_resultado,
        "modelo_utilizado": resultado_ia["modelo"],
        "arquivos_relatorio": {
            "markdown": caminho_md.name,
            "html": caminho_html.name,
        },
        "csv_rastreamento": str(caminho_rastreamento.resolve()),
        "status_planilha": resultado_planilha,
    }
