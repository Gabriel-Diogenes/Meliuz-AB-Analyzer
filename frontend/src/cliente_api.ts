import type { DadosRastreamento, PromptsPadrao, ResultadoAnalise } from './tipos'

const BASE_API = '/api'

async function tratarResposta<T>(resposta: Response): Promise<T> {
  const dados = await resposta.json().catch(() => ({}))
  if (!resposta.ok) {
    throw new Error(dados.detail || dados.mensagem || dados.message || 'Erro na requisição')
  }
  return dados as T
}

function normalizarPromptsPadrao(dados: Record<string, unknown>): PromptsPadrao {
  return {
    prompt_sistema: String(dados.prompt_sistema ?? dados.system_prompt ?? ''),
    prompt_analise: String(dados.prompt_analise ?? dados.analysis_prompt ?? ''),
    modelos_disponiveis: (dados.modelos_disponiveis ?? dados.available_models ?? []) as string[],
    modelo_padrao: String(dados.modelo_padrao ?? dados.default_model ?? 'gemini-3-flash-preview'),
    gemini_configurado: Boolean(dados.gemini_configurado ?? dados.gemini_configured),
  }
}

function normalizarRastreamento(dados: Record<string, unknown>): DadosRastreamento {
  return {
    linhas: (dados.linhas ?? dados.rows ?? []) as DadosRastreamento['linhas'],
    caminho_csv: String(dados.caminho_csv ?? dados.csv_path ?? ''),
    csv_existe: Boolean(dados.csv_existe ?? dados.csv_exists),
    planilha_google_configurada: Boolean(dados.planilha_google_configurada ?? dados.google_sheets_configured),
    url_planilha_google: String(dados.url_planilha_google ?? dados.google_sheets_url ?? ''),
    status_planilha: (dados.status_planilha ?? dados.sheets_status) as DadosRastreamento['status_planilha'],
  }
}

export async function buscarPromptsPadrao(): Promise<PromptsPadrao> {
  const resposta = await fetch(`${BASE_API}/prompts/defaults`)
  const dados = await tratarResposta<Record<string, unknown>>(resposta)
  return normalizarPromptsPadrao(dados)
}

export async function validarConexaoGemini(modelo = ''): Promise<{ status: string; mensagem: string }> {
  const resposta = await fetch(`${BASE_API}/validate-key`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ modelo }),
  })
  return tratarResposta(resposta)
}

export async function analisarTeste(
  dadosFormulario: FormData,
  onProgresso?: (segundosDecorridos: number) => void,
): Promise<ResultadoAnalise> {
  const resposta = await fetch(`${BASE_API}/analyze`, {
    method: 'POST',
    body: dadosFormulario,
  })
  const inicio = await tratarResposta<{ job_id: string; status: string }>(resposta)
  const intervaloMs = 1500

  for (let tentativa = 0; tentativa < 180; tentativa += 1) {
    await new Promise((resolver) => setTimeout(resolver, intervaloMs))
    onProgresso?.((tentativa + 1) * (intervaloMs / 1000))

    const statusResposta = await fetch(`${BASE_API}/analyze/jobs/${inicio.job_id}`)
    const status = await tratarResposta<{
      status: string
      resultado?: ResultadoAnalise
      erro?: string
    }>(statusResposta)

    if (status.status === 'completed' && status.resultado) {
      return status.resultado
    }
    if (status.status === 'failed') {
      throw new Error(status.erro || 'Erro ao analisar o teste')
    }
  }

  throw new Error('Tempo limite da analise excedido. Tente novamente em alguns instantes.')
}

export async function buscarRastreamento(): Promise<DadosRastreamento> {
  const resposta = await fetch(`${BASE_API}/tracking`)
  const dados = await tratarResposta<Record<string, unknown>>(resposta)
  return normalizarRastreamento(dados)
}

export function urlDownloadRelatorio(nomeArquivo: string): string {
  return `${BASE_API}/reports/${nomeArquivo}`
}
