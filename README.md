# Méliuz Growth A/B Analyzer

Solução reutilizável para análise automatizada de testes A/B de cashback do Méliuz. A ferramenta recebe um CSV, calcula métricas por variante, envia o contexto ao **Google Gemini** e devolve um relatório com decisão acionável: **qual grupo de cashback escalar para 100% do tráfego**.

Projeto desenvolvido como **teste prático para vaga de estágio — Growth AI-Native**.

---

## Demo online

**Acesse:** https://meliuz-ab-analyzer.onrender.com

Forma mais rápida de testar — sem instalar Python ou Node.

1. Abra o link acima (na primeira visita após inatividade, aguarde ~30 s enquanto o servidor “acorda”)
2. Confira o badge verde **"Gemini via backend/.env"**
3. Faça upload de um CSV da pasta `data/` (ou baixe do repositório)
4. Preencha **Nome do teste** e **Descrição** (opcional)
5. Clique em **Executar análise A/B** — a análise pode levar de **1 a 5 minutos**; a interface mostra o tempo decorrido
6. Veja a **decisão**, o **relatório completo** e o **histórico** na tela
7. Use **Abrir Google Sheets** para ver o registro consolidado de todos os testes

> No plano gratuito do Render, relatórios salvos no servidor podem ser perdidos após redeploy. O histórico persistente fica na planilha Google Sheets.

---

## O que a solução faz

1. **Recebe** um CSV de teste A/B (mesmo schema para os três parceiros)
2. **Pré-processa** os dados — valores em R$, datas, alertas de qualidade (ex.: receita líquida zero, desbalanceamento)
3. **Calcula métricas** por grupo: GMV, comissão, cashback, receita líquida, ticket médio, margem
4. **Analisa com Gemini** usando prompts parametrizáveis (editáveis na interface)
5. **Gera relatório** em Markdown e HTML, apresentável para gestores
6. **Responde** a pergunta central: *"Dado esse teste A/B, qual variante escalar para 100% do tráfego?"*
7. **Registra** cada teste no CSV local e no **Google Sheets** (nome, descrição, resultado, decisão)

---

## Datasets do teste

Os três CSVs oficiais estão em `data/`:

| Arquivo | Parceiro | Grupos |
|---------|----------|--------|
| `dataset_01_parceiroA.csv` | Parceiro A | 3 variantes |
| `dataset_02_parceiroB.csv` | Parceiro B | 3 variantes |
| `dataset_03_parceiroC.csv` | Parceiro C | 2 variantes |

**Schema:** `Data`, `Grupos de usuários`, `Parceiro`, `compradores`, `comissão`, `cashback`, `vendas totais`

A mesma solução processa os três arquivos **sem alteração de código** — basta indicar o CSV na interface.

---

## Como rodar localmente

### Pré-requisitos

| Ferramenta | Versão mínima |
|------------|---------------|
| [Python](https://www.python.org/downloads/) | 3.11+ |
| [Node.js](https://nodejs.org/) | 18+ |

Chave gratuita do Gemini: https://aistudio.google.com/apikey

### 1. Configurar variáveis de ambiente

```bash
cd backend
copy .env.example .env
```

Edite `backend/.env`:

```env
GEMINI_API_KEY=sua_chave_aqui
GEMINI_MODEL=gemini-2.5-flash-lite

# Opcional — Google Sheets
GOOGLE_SHEETS_ID=id_da_planilha
GOOGLE_SERVICE_ACCOUNT_JSON=service-account.json
```

> A chave do Gemini é lida pelo backend. **Não é necessário** colar a chave na interface web.

### 2. Iniciar (Windows)

Na raiz do projeto, dê duplo clique em **`Iniciar.bat`**.

Na primeira execução, o script instala as dependências. Depois:

- Interface: http://localhost:5173
- API: http://localhost:8000

Para encerrar: **`Parar.bat`** ou feche as janelas Backend e Frontend.

### 3. Iniciar manualmente (alternativa)

**Terminal 1 — Backend:**

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux / macOS
pip install -r requirements.txt
uvicorn app.principal:aplicacao --reload --port 8000
```

**Terminal 2 — Frontend:**

```bash
cd frontend
npm install
npm run dev
```

Abra http://localhost:5173

---

## Onde ficam os resultados

| Saída | Local |
|-------|-------|
| Relatórios (MD + HTML) | `backend/output/reports/` |
| Histórico local (CSV) | `backend/output/tracking.csv` |
| Google Sheets | Botão **Abrir Google Sheets** na interface |

---

## Estrutura do projeto

```
Meliuz-AB-Analyzer/
├── Iniciar.bat / Parar.bat     # Atalhos Windows
├── Dockerfile / render.yaml    # Deploy no Render
├── backend/                    # API FastAPI + Gemini + métricas
├── frontend/                   # Interface React + Vite
├── data/                       # CSVs dos parceiros A, B e C
└── README.md
```

---

## Licença

Projeto criado para o teste técnico Méliuz — Growth AI-Native.
