# Méliuz Growth A/B Analyzer

Solução para análise automatizada de testes A/B de cashback do Méliuz, com interface web, **Google AI Studio (Gemini)** e registro dos resultados em planilha.

> Projeto desenvolvido como **teste prático para vaga de estágio** (Growth AI-Native). O objetivo é que o avaliador consiga rodar tudo em poucos minutos, sem conhecimento prévio do código.

---

## Demo online (recomendado para o avaliador)

A forma mais simples de testar é **abrir o link publicado** — sem instalar Python, Node ou rodar scripts locais.

> **Demo:** _(cole aqui a URL do Render após publicar, ex.: `https://meliuz-ab-analyzer.onrender.com`)_

1. Abra o link acima
2. Aguarde ~30 s na primeira visita (plano gratuito “dorme” após inatividade)
3. Confira o badge verde **"Gemini via backend/.env"**
4. Faça upload de um CSV da pasta `data/` e clique em **Executar análise A/B**

Os datasets de exemplo continuam no repositório em `data/` para download.

### Como publicar gratuitamente no Render (para o candidato)

Hospedagem **100% gratuita** com [Render](https://render.com) — um único link serve interface + API.

#### Passo a passo

1. **Suba o código para um repositório público no GitHub** (sem commitar o `.env`).

2. Crie conta em [render.com](https://render.com) e conecte o GitHub.

3. Clique em **New → Blueprint** e selecione o repositório.  
   O arquivo `render.yaml` na raiz configura tudo automaticamente.

   _Alternativa manual:_ **New → Web Service** → escolha o repo → **Language: Docker** → confirme o `Dockerfile` na raiz.

4. Na tela de variáveis de ambiente, adicione:
   ```
   GEMINI_API_KEY=sua_chave_aqui
   ```
   Obtenha a chave em: https://aistudio.google.com/apikey  
   **Nunca** commite a chave no Git.

5. Clique em **Deploy**. Aguarde o build (~3–5 min na primeira vez).

6. Copie a URL gerada (ex.: `https://meliuz-ab-analyzer.onrender.com`) e:
   - Cole no campo **Demo** deste README
   - Envie o link na entrega do teste

#### Limitações do plano gratuito

| Item | Comportamento |
|------|----------------|
| Primeira visita após inatividade | Pode levar ~30–60 s para “acordar” |
| Análise com Gemini | Pode levar 1–2 min; a interface aguarda automaticamente |
| Relatórios e histórico | Ficam no disco efêmero — somem ao redeploy |
| Google Sheets | Opcional; exige JSON da service account (não necessário para o teste) |

> **Rodar localmente** continua disponível abaixo, caso o avaliador prefira inspecionar o código na máquina.

---

## Guia rápido para o avaliador

### 1. Pré-requisitos

Instale antes de começar:

| Ferramenta | Versão mínima | Como verificar |
|------------|---------------|----------------|
| [Python](https://www.python.org/downloads/) | 3.11+ | `python --version` |
| [Node.js](https://nodejs.org/) | 18+ | `node --version` |

Você também precisa de uma **chave de API do Gemini**, gratuita em:  
https://aistudio.google.com/apikey

### 2. Configurar a chave de API (obrigatório)

```bash
cd backend
copy .env.example .env
```

Abra `backend/.env` e preencha:

```env
GEMINI_API_KEY=sua_chave_aqui
```

> A chave é lida automaticamente pelo backend. **Não é necessário** colar a chave na interface web.

### 3. Iniciar a aplicação (Windows — mais fácil)

Na raiz do projeto, dê **duplo clique** em:

```
Iniciar.bat
```

Na primeira execução, o script instala as dependências. Depois:

- Backend sobe em http://localhost:8000
- Frontend sobe em http://localhost:5173
- O navegador abre automaticamente

Para encerrar: execute `Parar.bat` ou feche as janelas **Meliuz Backend** e **Meliuz Frontend**.

### 4. Rodar uma análise

1. Acesse http://localhost:5173
2. Confira o badge verde **"Gemini via backend/.env"** (se aparecer vermelho, a chave não foi configurada)
3. Arraste um CSV da pasta `data/` ou clique para selecionar
4. Preencha **Nome do teste** e **Descrição** (opcional)
5. Clique em **Executar análise A/B**
6. Veja a **decisão**, o **relatório completo** e o **histórico** na tela
7. Baixe o relatório em Markdown ou HTML

### 5. Datasets do teste

Os três CSVs oficiais já estão em `data/`:

| Arquivo | Parceiro |
|---------|----------|
| `dataset_01_parceiroA.csv` | Parceiro A |
| `dataset_02_parceiroB.csv` | Parceiro B |
| `dataset_03_parceiroC.csv` | Parceiro C |

Rode uma análise para **cada um** dos três arquivos.

### 6. Onde ficam os resultados

| Saída | Caminho |
|-------|---------|
| Relatórios (MD + HTML) | `backend/output/reports/` |
| Histórico local (CSV) | `backend/output/tracking.csv` |
| Google Sheets (se configurado) | link na seção "Histórico de testes" da interface |

---

## O que a solução faz

1. Recebe um CSV de teste A/B (mesmo schema para os três parceiros)
2. Pré-processa dados (valores em R$, datas, alertas de qualidade)
3. Calcula métricas por grupo (GMV, comissão, cashback, receita líquida, ticket médio)
4. Envia métricas + prompts ao **Gemini**
5. Gera relatório Markdown/HTML para gestores
6. Responde: **qual variante escalar para 100% do tráfego**
7. Registra o teste em CSV local e, opcionalmente, no Google Sheets

---

## Estrutura do projeto

```
meliuz-ab-analyzer/
├── Dockerfile / render.yaml  # Deploy gratuito (Render) — um link só
├── Iniciar.bat / Parar.bat   # Atalhos para subir e parar tudo (Windows)
├── Iniciar.ps1               # Alternativa PowerShell
├── backend/
│   ├── app/                  # API FastAPI
│   ├── .env.example          # Modelo de configuração (copie para .env)
│   └── output/               # Relatórios e tracking gerados
├── frontend/                 # Interface React + Vite
├── data/                     # CSVs dos parceiros A, B e C
└── README.md
```

---

## Como rodar manualmente (alternativa)

Útil se preferir terminais separados ou estiver em outro sistema operacional.

### Terminal 1 — Backend

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
# source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env
# Edite .env e cole GEMINI_API_KEY=

uvicorn app.principal:aplicacao --reload --port 8000
```

### Terminal 2 — Frontend

```bash
cd frontend
npm install
npm run dev
```

Abra http://localhost:5173

---

## Configuração completa do `.env`

Arquivo: `backend/.env` (crie a partir de `.env.example`)

| Variável | Obrigatório | Descrição |
|----------|-------------|-----------|
| `GEMINI_API_KEY` | Sim | Chave do [Google AI Studio](https://aistudio.google.com/apikey) |
| `GEMINI_MODEL` | Não | Padrão: `gemini-3-flash-preview` |
| `GOOGLE_SHEETS_ID` | Não | ID da planilha Google Sheets |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Não | Caminho do JSON da service account |
| `TRACKING_CSV_PATH` | Não | Padrão: `output/tracking.csv` |
| `REPORTS_DIR` | Não | Padrão: `output/reports` |

---

## Google Sheets (diferencial opcional)

Para registrar os testes direto no Google Sheets:

### Passo 1 — Criar a planilha

1. Crie uma planilha em [Google Sheets](https://sheets.google.com)
2. Copie o **ID** da URL:  
   `https://docs.google.com/spreadsheets/d/ESTE_ID/edit`

### Passo 2 — Service account no Google Cloud

1. Acesse [Google Cloud Console](https://console.cloud.google.com)
2. Crie um projeto (ou use um existente)
3. Ative as APIs **Google Sheets API** e **Google Drive API**
4. Vá em **IAM e administrador → Contas de serviço → Criar conta de serviço**
5. Baixe a chave JSON (**Chaves → Adicionar chave → JSON**)
6. Abra o JSON e copie o e-mail em `"client_email"` (ex.: `...@....iam.gserviceaccount.com`)

### Passo 3 — Compartilhar a planilha

1. Na planilha, clique em **Compartilhar**
2. Cole o e-mail da service account
3. Permissão: **Editor**

### Passo 4 — Configurar variáveis

#### Local (`backend/.env`)

**Opção A — arquivo JSON** (coloque o arquivo em `backend/`):

```env
GOOGLE_SHEETS_ID=id_da_planilha
GOOGLE_SERVICE_ACCOUNT_JSON=service-account.json
```

**Opção B — JSON inline** (cole o conteúdo inteiro do arquivo):

```env
GOOGLE_SHEETS_ID=id_da_planilha
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"..."}
```

#### Render (produção)

No painel do serviço **meliuz-ab-analyzer → Environment**:

| Variável | Valor |
|----------|-------|
| `GOOGLE_SHEETS_ID` | ID da planilha |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Cole o **JSON inteiro** da service account (uma linha) |

Salve e aguarde o redeploy. Na interface, deve aparecer o botão **"Abrir Google Sheets"** no histórico.

> **Nunca** commite o arquivo JSON no Git. Ele já está no `.gitignore`.

Sem essa configuração, o sistema funciona normalmente e grava só no CSV local.

---

## Problemas comuns

| Problema | Solução |
|--------|---------|
| Badge "GEMINI_API_KEY ausente" | Crie `backend/.env` com a chave e reinicie o backend |
| Prompts vazios na interface | Execute `Parar.bat` → `Iniciar.bat` e recarregue com Ctrl+F5 |
| Porta 8000 ou 5173 em uso | Execute `Parar.bat` antes de iniciar de novo |
| Erro ao instalar Python | Marque "Add Python to PATH" na instalação |
| `Iniciar.bat` não abre | Use `Iniciar.ps1` (botão direito → Executar com PowerShell) |

---

## API

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/health` | GET | Health check |
| `/api/prompts/defaults` | GET | Prompts e modelos disponíveis |
| `/api/validate-key` | POST | Valida chave Gemini (usa `.env`) |
| `/api/analyze` | POST | Inicia analise assincrona (retorna `job_id`) |
| `/api/analyze/jobs/{job_id}` | GET | Consulta status/resultado da analise |
| `/api/tracking` | GET | Lista testes registrados |
| `/api/reports/{arquivo}` | GET | Download de relatório |

---

## Entrega do teste técnico

Checklist sugerido para o candidato:

- [ ] Repositório GitHub **público** com este README
- [ ] **Link da demo online** no README (Render ou similar)
- [ ] `.env` **não** commitado (use `.env.example` como referência)
- [ ] 3 análises rodadas (Parceiros A, B e C)
- [ ] Relatórios em `backend/output/reports/`
- [ ] Histórico em `backend/output/tracking.csv` (e/ou Google Sheets)

---

## Licença

Projeto criado para o teste técnico Méliuz — Growth AI-Native.
