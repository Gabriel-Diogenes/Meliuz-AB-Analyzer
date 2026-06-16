export interface MetricaGrupo {
  grupo: string
  compradores: number
  gmv: number
  comissao: number
  cashback: number
  receita_liquida: number
  ticket_medio: number
  cashback_rate_sobre_gmv: number
  comissao_rate_sobre_gmv: number
  margem_liquida_sobre_gmv: number
  compradores_por_dia: number
  dias_ativos: number
}

export interface MetricasAnalise {
  parceiro: string
  periodo: { inicio: string; fim: string; dias: number }
  grupos: string[]
  metricas_por_grupo: MetricaGrupo[]
  qualidade_dados: string[]
  totais: { linhas: number; compradores: number; gmv: number }
}

export interface ResultadoAnalise {
  sucesso: boolean
  nome_teste: string
  metricas: MetricasAnalise
  avisos: string[]
  relatorio_markdown: string
  decisao: string
  resumo_resultado: string
  modelo_utilizado: string
  arquivos_relatorio: { markdown: string; html: string }
  csv_rastreamento: string
  status_planilha: { status: string; mensagem: string }
}

export interface LinhaRastreamento {
  data_analise: string
  nome_teste: string
  descricao: string
  parceiro: string
  periodo: string
  variantes: string
  resultado: string
  decisao: string
  arquivo: string
}

export interface DadosRastreamento {
  linhas: LinhaRastreamento[]
  caminho_csv: string
  csv_existe?: boolean
  planilha_google_configurada: boolean
  url_planilha_google: string
  status_planilha?: { status: string; mensagem: string; email_conta_servico?: string }
}

export interface PromptsPadrao {
  prompt_sistema: string
  prompt_analise: string
  modelos_disponiveis: string[]
  modelo_padrao: string
  gemini_configurado: boolean
}
