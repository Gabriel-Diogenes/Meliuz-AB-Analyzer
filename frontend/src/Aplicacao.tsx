import { useCallback, useEffect, useMemo, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import {
  AlertTriangle,
  BarChart3,
  CheckCircle2,
  Download,
  ExternalLink,
  FileSpreadsheet,
  Loader2,
  Sparkles,
  Upload,
  Zap,
} from 'lucide-react'
import {
  analisarTeste,
  buscarPromptsPadrao,
  buscarRastreamento,
  urlDownloadRelatorio,
} from './cliente_api'
import type { LinhaRastreamento, ResultadoAnalise } from './tipos'

const ROTULOS_MODELO: Record<string, string> = {
  'gemini-3-flash-preview': 'Gemini 3.0 Flash',
  'gemini-2.5-flash-lite': 'Gemini 2.5 Flash Lite',
}

function formatarMoeda(valor: number): string {
  return valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

export default function Aplicacao() {
  const [modelo, setModelo] = useState('gemini-3-flash-preview')
  const [modelos, setModelos] = useState<string[]>(['gemini-3-flash-preview', 'gemini-2.5-flash-lite'])
  const [geminiConfigurado, setGeminiConfigurado] = useState(false)
  const [promptSistema, setPromptSistema] = useState('')
  const [promptAnalise, setPromptAnalise] = useState('')
  const [nomeTeste, setNomeTeste] = useState('')
  const [descricaoTeste, setDescricaoTeste] = useState('')
  const [arquivo, setArquivo] = useState<File | null>(null)
  const [arrastando, setArrastando] = useState(false)
  const [carregando, setCarregando] = useState(false)
  const [resultado, setResultado] = useState<ResultadoAnalise | null>(null)
  const [erro, setErro] = useState<string | null>(null)
  const [linhasRastreamento, setLinhasRastreamento] = useState<LinhaRastreamento[]>([])
  const [urlPlanilhaGoogle, setUrlPlanilhaGoogle] = useState('')

  useEffect(() => {
    buscarPromptsPadrao()
      .then((padroes) => {
        setPromptSistema(padroes.prompt_sistema)
        setPromptAnalise(padroes.prompt_analise)
        setModelos(padroes.modelos_disponiveis)
        setModelo(padroes.modelo_padrao)
        setGeminiConfigurado(padroes.gemini_configurado)
      })
      .catch((falha) => {
        setErro(falha instanceof Error ? falha.message : 'Nao foi possivel carregar configuracoes da API.')
      })

    buscarRastreamento()
      .then((dados) => {
        setLinhasRastreamento(dados.linhas)
        setUrlPlanilhaGoogle(dados.url_planilha_google)
      })
      .catch(() => undefined)
  }, [])

  const tratarArquivo = useCallback((selecionado: File | null) => {
    if (!selecionado) return
    if (!selecionado.name.toLowerCase().endsWith('.csv')) {
      setErro('Envie um arquivo CSV válido.')
      return
    }
    setArquivo(selecionado)
    setErro(null)
    if (!nomeTeste) {
      const base = selecionado.name.replace(/\.csv$/i, '')
      setNomeTeste(`Teste ${base}`)
    }
  }, [nomeTeste])

  const executarAnalise = async () => {
    if (!arquivo) {
      setErro('Selecione um arquivo CSV.')
      return
    }
    if (!nomeTeste.trim()) {
      setErro('Informe o nome do teste.')
      return
    }
    if (!geminiConfigurado) {
      setErro('GEMINI_API_KEY nao configurada no backend/.env.')
      return
    }

    setCarregando(true)
    setErro(null)

    const dadosFormulario = new FormData()
    dadosFormulario.append('arquivo', arquivo)
    dadosFormulario.append('nome_teste', nomeTeste.trim())
    dadosFormulario.append('descricao_teste', descricaoTeste.trim())
    dadosFormulario.append('modelo', modelo)
    dadosFormulario.append('prompt_sistema', promptSistema)
    dadosFormulario.append('prompt_analise', promptAnalise)

    try {
      const analise = await analisarTeste(dadosFormulario)
      setResultado(analise)
      const rastreamento = await buscarRastreamento()
      setLinhasRastreamento(rastreamento.linhas)
      setUrlPlanilhaGoogle(rastreamento.url_planilha_google)
    } catch (falha) {
      setResultado(null)
      setErro(falha instanceof Error ? falha.message : 'Erro ao analisar o teste')
    } finally {
      setCarregando(false)
    }
  }

  const cartoesMetricas = useMemo(() => {
    if (!resultado) return []
    const { metricas_por_grupo } = resultado.metricas
    const melhorReceita = [...metricas_por_grupo].sort((a, b) => b.receita_liquida - a.receita_liquida)[0]
    const maisCompradores = [...metricas_por_grupo].sort((a, b) => b.compradores - a.compradores)[0]
    return [
      { rotulo: 'Parceiro', valor: resultado.metricas.parceiro },
      { rotulo: 'Período', valor: `${resultado.metricas.periodo.inicio} → ${resultado.metricas.periodo.fim}` },
      { rotulo: 'Melhor receita líquida', valor: `${melhorReceita.grupo} (${formatarMoeda(melhorReceita.receita_liquida)})` },
      { rotulo: 'Mais compradores', valor: `${maisCompradores.grupo} (${maisCompradores.compradores})` },
    ]
  }, [resultado])

  return (
    <div className="min-h-screen bg-[radial-gradient(ellipse_at_top,_rgba(234,88,12,0.12)_0%,_transparent_55%)]">
      <header className="border-b border-white/5 bg-ink-950/70 backdrop-blur-md">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-meliuz-500 to-meliuz-700 shadow-glow">
              <BarChart3 className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="font-display text-xl font-bold text-white">Méliuz Growth A/B Analyzer</h1>
              <p className="text-sm text-ink-500">Análise automatizada de testes de cashback com Google AI Studio</p>
            </div>
          </div>
          <div className="hidden items-center gap-2 rounded-full border border-meliuz-500/30 bg-meliuz-500/10 px-4 py-2 text-sm text-meliuz-300 md:flex">
            <Sparkles className="h-4 w-4" />
            AI-Native Growth
          </div>
        </div>
      </header>

      <main className="mx-auto grid max-w-7xl gap-6 px-6 py-8 lg:grid-cols-[1.1fr_0.9fr]">
        <div className="space-y-6">
          <section className="glass-card p-6">
            <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <Upload className="h-5 w-5 text-meliuz-400" />
                <h2 className="section-title">Dataset do teste A/B</h2>
              </div>
              <div className="flex items-center gap-2">
                {geminiConfigurado ? (
                  <span className="inline-flex items-center gap-1 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 text-xs text-emerald-300">
                    <CheckCircle2 className="h-3.5 w-3.5" />
                    Gemini via backend/.env
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1 rounded-full border border-red-500/30 bg-red-500/10 px-3 py-1 text-xs text-red-300">
                    <AlertTriangle className="h-3.5 w-3.5" />
                    GEMINI_API_KEY ausente no .env
                  </span>
                )}
                <select className="input-field w-52 py-2 text-sm" value={modelo} onChange={(e) => setModelo(e.target.value)}>
                  {modelos.map((item) => (
                    <option key={item} value={item}>{ROTULOS_MODELO[item] ?? item}</option>
                  ))}
                </select>
              </div>
            </div>

            <div
              className={`mb-4 flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed px-6 py-10 transition ${
                arrastando ? 'border-meliuz-400 bg-meliuz-500/10' : 'border-white/10 bg-ink-800/40 hover:border-meliuz-500/40'
              }`}
              onDragOver={(e) => { e.preventDefault(); setArrastando(true) }}
              onDragLeave={() => setArrastando(false)}
              onDrop={(e) => {
                e.preventDefault()
                setArrastando(false)
                tratarArquivo(e.dataTransfer.files?.[0] ?? null)
              }}
              onClick={() => document.getElementById('entrada-csv')?.click()}
            >
              <FileSpreadsheet className="mb-3 h-10 w-10 text-meliuz-400" />
              <p className="font-medium text-white">
                {arquivo ? arquivo.name : 'Arraste o CSV ou clique para selecionar'}
              </p>
              <p className="mt-1 text-sm text-ink-500">Parceiros A, B ou C — mesmo schema</p>
              <input
                id="entrada-csv"
                type="file"
                accept=".csv"
                className="hidden"
                onChange={(e) => tratarArquivo(e.target.files?.[0] ?? null)}
              />
            </div>

            <div className="grid gap-3 md:grid-cols-2">
              <div>
                <label className="mb-1.5 block text-sm font-medium text-ink-300">Nome do teste</label>
                <input
                  className="input-field"
                  placeholder="Ex: Cashback Parceiro A — Q1"
                  value={nomeTeste}
                  onChange={(e) => setNomeTeste(e.target.value)}
                />
              </div>
              <div>
                <label className="mb-1.5 block text-sm font-medium text-ink-300">Descrição</label>
                <input
                  className="input-field"
                  placeholder="Ex: Teste de 5% vs 7% de cashback"
                  value={descricaoTeste}
                  onChange={(e) => setDescricaoTeste(e.target.value)}
                />
              </div>
            </div>
          </section>

          <section className="glass-card p-6">
            <div className="mb-4 flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-meliuz-400" />
              <h2 className="section-title">Prompts enviados ao Google AI Studio</h2>
            </div>
            <p className="mb-4 text-sm text-ink-500">
              Personalize como a IA analisa o teste. Use {'{nome_teste}'}, {'{descricao_teste}'} e {'{contexto_metricas}'} no prompt de análise.
            </p>
            <div className="space-y-4">
              <div>
                <label className="mb-1.5 block text-sm font-medium text-ink-300">Prompt de sistema</label>
                <textarea
                  className="input-field min-h-[140px] font-mono text-xs leading-relaxed"
                  value={promptSistema}
                  onChange={(e) => setPromptSistema(e.target.value)}
                />
              </div>
              <div>
                <label className="mb-1.5 block text-sm font-medium text-ink-300">Prompt de análise</label>
                <textarea
                  className="input-field min-h-[220px] font-mono text-xs leading-relaxed"
                  value={promptAnalise}
                  onChange={(e) => setPromptAnalise(e.target.value)}
                />
              </div>
            </div>
          </section>

          <button type="button" className="btn-primary w-full py-4 text-base" onClick={executarAnalise} disabled={carregando}>
            {carregando ? (
              <>
                <Loader2 className="h-5 w-5 animate-spin" />
                Analisando com Gemini...
              </>
            ) : (
              <>
                <Zap className="h-5 w-5" />
                Executar análise A/B
              </>
            )}
          </button>

          {erro && (
            <div className="flex items-start gap-3 rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-300">
              <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
              {erro}
            </div>
          )}
        </div>

        <div className="space-y-6">
          {resultado ? (
            <>
              <section className="glass-card p-6">
                <h2 className="section-title mb-4">Decisão recomendada</h2>
                <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-4">
                  <p className="text-sm uppercase tracking-wide text-emerald-400">Escalar para 100%</p>
                  <p className="mt-2 text-lg font-semibold text-white">{resultado.decisao}</p>
                </div>
                <div className="mt-4 grid gap-3 sm:grid-cols-2">
                  {cartoesMetricas.map((cartao) => (
                    <div key={cartao.rotulo} className="rounded-xl bg-ink-800/60 p-3">
                      <p className="text-xs uppercase tracking-wide text-ink-500">{cartao.rotulo}</p>
                      <p className="mt-1 text-sm font-medium text-white">{cartao.valor}</p>
                    </div>
                  ))}
                </div>
                <div className="mt-4 flex flex-wrap gap-2">
                  <a className="btn-secondary" href={urlDownloadRelatorio(resultado.arquivos_relatorio.markdown)} download>
                    <Download className="h-4 w-4" /> Markdown
                  </a>
                  <a className="btn-secondary" href={urlDownloadRelatorio(resultado.arquivos_relatorio.html)} target="_blank" rel="noreferrer">
                    <Download className="h-4 w-4" /> HTML
                  </a>
                </div>
                {resultado.avisos.length > 0 && (
                  <div className="mt-4 rounded-xl border border-amber-500/30 bg-amber-500/10 p-3 text-sm text-amber-200">
                    <p className="font-medium">Alertas de dados</p>
                    <ul className="mt-2 list-disc space-y-1 pl-4">
                      {resultado.avisos.map((aviso) => <li key={aviso}>{aviso}</li>)}
                    </ul>
                  </div>
                )}
              </section>

              <section className="glass-card max-h-[640px] overflow-y-auto p-6">
                <h2 className="section-title mb-4">Relatório completo</h2>
                <div className="markdown-report">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{resultado.relatorio_markdown}</ReactMarkdown>
                </div>
              </section>
            </>
          ) : (
            <section className="glass-card flex min-h-[420px] flex-col items-center justify-center p-8 text-center">
              <BarChart3 className="mb-4 h-14 w-14 text-ink-700" />
              <h2 className="font-display text-xl font-semibold text-white">Aguardando análise</h2>
              <p className="mt-2 max-w-sm text-sm text-ink-500">
                Envie o CSV e execute. A chave do Gemini e carregada automaticamente do backend/.env.
              </p>
            </section>
          )}

          <section className="glass-card p-6">
            <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
              <h2 className="section-title">Histórico de testes (planilha)</h2>
              {urlPlanilhaGoogle ? (
                <a
                  href={urlPlanilhaGoogle}
                  target="_blank"
                  rel="noreferrer"
                  className="btn-secondary text-sm"
                >
                  <ExternalLink className="h-4 w-4" />
                  Abrir Google Sheets
                </a>
              ) : null}
            </div>
            {linhasRastreamento.length === 0 ? (
              <p className="text-sm text-ink-500">
                Nenhum teste registrado ainda. Os resultados sao salvos em{' '}
                <code className="text-meliuz-300">backend/output/tracking.csv</code>
                {urlPlanilhaGoogle ? ' e na planilha do Google Sheets.' : '.'}
              </p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead>
                    <tr className="border-b border-white/10 text-ink-500">
                      <th className="px-2 py-2">Data</th>
                      <th className="px-2 py-2">Teste</th>
                      <th className="px-2 py-2">Parceiro</th>
                      <th className="px-2 py-2">Decisão</th>
                    </tr>
                  </thead>
                  <tbody>
                    {linhasRastreamento.slice().reverse().map((linha, indice) => (
                      <tr key={`${linha.nome_teste}-${indice}`} className="border-b border-white/5">
                        <td className="px-2 py-2 whitespace-nowrap">{linha.data_analise}</td>
                        <td className="px-2 py-2">{linha.nome_teste}</td>
                        <td className="px-2 py-2">{linha.parceiro}</td>
                        <td className="px-2 py-2 max-w-[200px] truncate" title={linha.decisao}>{linha.decisao}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </div>
      </main>
    </div>
  )
}
