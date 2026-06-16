from __future__ import annotations

from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.analisador_csv import carregar_dataset_ab
from app.configuracao import MODELO_GEMINI_PADRAO, MODELOS_GEMINI_PERMITIDOS, configuracoes
from app.gerador_relatorio import montar_resumo_resultado, salvar_relatorio
from app.metricas import calcular_metricas, metricas_para_contexto_prompt
from app.prompts_padrao import PROMPT_ANALISE_PADRAO, PROMPT_SISTEMA_PADRAO
from app.rastreador import adicionar_linha_rastreamento, ler_linhas_rastreamento, tentar_adicionar_planilha_google
from app.servico_gemini import analisar_com_gemini, validar_chave_api

aplicacao = FastAPI(
    title="Méliuz Growth A/B Analyzer",
    description="Análise automatizada de testes A/B de cashback com Google AI Studio",
    version="1.0.0",
)

aplicacao.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RequisicaoValidacaoChave(BaseModel):
    modelo: str = ""


class RespostaPromptsPadrao(BaseModel):
    prompt_sistema: str
    prompt_analise: str
    modelos_disponiveis: list[str]
    modelo_padrao: str
    gemini_configurado: bool


def _obter_chave_gemini_obrigatoria() -> str:
    chave = configuracoes.chave_gemini.strip()
    if not chave:
        raise HTTPException(
            status_code=503,
            detail="GEMINI_API_KEY nao configurada no arquivo backend/.env.",
        )
    return chave


def _modelo_padrao() -> str:
    modelo_env = configuracoes.modelo_gemini.strip()
    if modelo_env in MODELOS_GEMINI_PERMITIDOS:
        return modelo_env
    return MODELO_GEMINI_PADRAO


def _resolver_modelo(modelo: str | None = None) -> str:
    solicitado = (modelo or "").strip() or _modelo_padrao()
    if solicitado not in MODELOS_GEMINI_PERMITIDOS:
        permitidos = ", ".join(MODELOS_GEMINI_PERMITIDOS)
        raise HTTPException(
            status_code=400,
            detail=f"Modelo nao permitido: {solicitado}. Use um destes: {permitidos}.",
        )
    return solicitado


@aplicacao.get("/api/health")
def verificar_saude() -> dict[str, str]:
    return {"status": "ok"}


@aplicacao.get("/api/prompts/defaults", response_model=RespostaPromptsPadrao)
def obter_prompts_padrao() -> RespostaPromptsPadrao:
    return RespostaPromptsPadrao(
        prompt_sistema=PROMPT_SISTEMA_PADRAO,
        prompt_analise=PROMPT_ANALISE_PADRAO,
        modelos_disponiveis=list(MODELOS_GEMINI_PERMITIDOS),
        modelo_padrao=_modelo_padrao(),
        gemini_configurado=bool(configuracoes.chave_gemini.strip()),
    )


@aplicacao.post("/api/validate-key")
def validar_chave(requisicao: RequisicaoValidacaoChave) -> dict[str, str]:
    try:
        return validar_chave_api(_obter_chave_gemini_obrigatoria(), _resolver_modelo(requisicao.modelo))
    except HTTPException:
        raise
    except Exception as erro:
        raise HTTPException(status_code=400, detail=str(erro)) from erro


@aplicacao.get("/api/tracking")
def obter_rastreamento() -> dict:
    linhas = ler_linhas_rastreamento()
    caminho = Path(configuracoes.caminho_csv_rastreamento)
    id_planilha = configuracoes.id_planilha_google.strip()
    return {
        "linhas": linhas,
        "caminho_csv": str(caminho.resolve()),
        "csv_existe": caminho.exists(),
        "planilha_google_configurada": bool(id_planilha),
        "url_planilha_google": (
            f"https://docs.google.com/spreadsheets/d/{id_planilha}/edit?usp=sharing" if id_planilha else ""
        ),
    }


@aplicacao.get("/api/reports/{nome_arquivo}")
def baixar_relatorio(nome_arquivo: str):
    diretorio = Path(configuracoes.diretorio_relatorios).resolve()
    caminho_arquivo = (diretorio / nome_arquivo).resolve()
    if not str(caminho_arquivo).startswith(str(diretorio)) or not caminho_arquivo.exists():
        raise HTTPException(status_code=404, detail="Relatório não encontrado.")
    return FileResponse(caminho_arquivo)


@aplicacao.post("/api/analyze")
async def analisar_teste_ab(
    arquivo: UploadFile = File(...),
    nome_teste: str = Form(...),
    descricao_teste: str = Form(""),
    modelo: str = Form(""),
    prompt_sistema: str = Form(""),
    prompt_analise: str = Form(""),
):
    chave_resolvida = _obter_chave_gemini_obrigatoria()
    modelo_resolvido = _resolver_modelo(modelo)

    conteudo = await arquivo.read()
    if not conteudo:
        raise HTTPException(status_code=400, detail="Arquivo CSV vazio.")

    try:
        dataframe, avisos = carregar_dataset_ab(conteudo, arquivo.filename or "dataset.csv")
        metricas = calcular_metricas(dataframe)
        contexto_metricas = metricas_para_contexto_prompt(metricas, avisos)

        resultado_ia = analisar_com_gemini(
            chave_api=chave_resolvida,
            nome_modelo=modelo_resolvido,
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
            nome_arquivo=arquivo.filename or "dataset.csv",
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
                "arquivo": arquivo.filename or "dataset.csv",
            }
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
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro)) from erro
    except Exception as erro:
        raise HTTPException(status_code=500, detail=f"Erro na análise: {erro}") from erro


DIRETORIO_STATIC = Path(__file__).resolve().parent.parent / "static"


def _montar_frontend_estatico() -> None:
    if not DIRETORIO_STATIC.exists():
        return

    pasta_assets = DIRETORIO_STATIC / "assets"
    if pasta_assets.exists():
        aplicacao.mount("/assets", StaticFiles(directory=pasta_assets), name="assets")

    @aplicacao.get("/{caminho:path}", include_in_schema=False)
    async def servir_spa(caminho: str):
        if caminho.startswith("api"):
            raise HTTPException(status_code=404, detail="Not found")
        alvo = DIRETORIO_STATIC / caminho
        if alvo.is_file():
            return FileResponse(alvo)
        return FileResponse(DIRETORIO_STATIC / "index.html")


_montar_frontend_estatico()
