# D4Sign Web Tests — Behave + Playwright

[![CI](https://github.com/Auditeste-Lab/d4sign-web-tests-playwright/actions/workflows/ci.yml/badge.svg)](https://github.com/Auditeste-Lab/d4sign-web-tests-playwright/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Behave](https://img.shields.io/badge/BDD-Behave-0B5FFF)](https://behave.readthedocs.io/)
[![Playwright](https://img.shields.io/badge/browser-Playwright-2EAD33?logo=playwright&logoColor=white)](https://playwright.dev/python/)
[![License](https://img.shields.io/badge/uso-interno%20QA-lightgrey)](#licença--uso)

Suíte de automação web da plataforma **D4Sign** com **Behave (BDD/Gherkin em português)**, **Page Object Model** e **Playwright (sync API)**.

Repositório: [Auditeste-Lab/d4sign-web-tests-playwright](https://github.com/Auditeste-Lab/d4sign-web-tests-playwright)

---

## Sumário

- [Stack](#stack)
- [Cobertura](#cobertura)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Configuração (.env)](#configuração-env)
- [Como executar](#como-executar)
- [Tags](#tags)
- [Arquitetura e convenções](#arquitetura-e-convenções)
- [Evidências e relatórios](#evidências-e-relatórios)
- [CI (GitHub Actions)](#ci-github-actions)
- [Tempo de execução](#tempo-de-execução)
- [Troubleshooting](#troubleshooting)

---

## Stack

| Camada | Tecnologia |
|--------|------------|
| BDD | Behave 1.2.6 + Gherkin (`# language: pt`) |
| Browser | Playwright (Chromium / Chrome) |
| Padrão | Page Object (`pages/`) + steps finos (`features/steps/`) |
| Config | `python-dotenv` + `recursos/utils/config.py` |
| Relatórios | HTML (`behave-html-formatter`), Trace Viewer (Playwright), JSON, screenshots, vídeos MP4 |
| CI | GitHub Actions (Python 3.12 + `playwright install chromium`) |

> **Não usa Selenium.** O driver é uma sessão Playwright (`BrowserDriver`) exposta como `context.driver`.

---

## Cobertura

| Área | Feature | Cenários | Tags principais |
|------|---------|----------|-----------------|
| Login | `features/login/login.feature` | 7 | `@login` `@smoke` `@critical` |
| Assinatura (desk) | `envio_assinatura.feature` | 2 | `@envio` `@signature` `@critical` |
| Canvas / pins | `envio_canvas_pins.feature` | 1 | `@envio` `@signature` |
| Cofre | `envio_cofre.feature` | 1 | `@envio` `@signature` `@critical` |
| Desk | `envio_desk.feature` | 1 | `@envio` `@signature` `@critical` |
| Erros de envio | `envio_erros.feature` | 3 | `@envio` `@signature` `@erro` |
| Grupo de assinatura | `envio_grupo_assinatura.feature` | 2 | `@envio` `@signature` |
| Lote | `envio_lote.feature` | 1 | `@envio` `@batch` |
| PowerForm | `envio_powerform.feature` | 1 | `@envio` |
| Reaproveitamento | `envio_reaproveitamento.feature` | 1 | `@envio` `@signature` |
| Substituição | `envio_substituicao.feature` | 1 | `@envio` `@signature` |
| Template HTML | `envio_template_html.feature` | 3 | `@envio` `@template` `@signature` |
| Pin (anexo/canvas) | `pin.feature` | 2 | `@envio` `@pin` `@signature` `@critical` |
| Tipos de pin | `pin_tipos.feature` | 1 | `@envio` `@pin` `@signature` |
| Consulta de cofre | `cofres/consulta_cofre.feature` | 1 | `@cofre` `@cofre-normal` `@smoke` |
| Cofre compartilhado | `cofres/consulta_cofre_compartilhado.feature` | 1 | `@cofre` `@cofre-compartilhado` `@smoke` |
| Embed (viewblob) | `embed/assinatura_embed.feature` | 1 | `@embed` `@critical` |
| **Total** | **17 features** | **30** | |

---

## Estrutura do projeto

```
template-web-tests-python/
├── features/
│   ├── environment.py          # Hooks Behave (lifecycle Playwright, evidências, cache de login)
│   ├── login/
│   │   └── login.feature
│   ├── envios/
│   │   └── *.feature           # Envio, assinatura, pin, lote, template
│   ├── cofres/
│   │   ├── consulta_cofre.feature
│   │   └── consulta_cofre_compartilhado.feature
│   ├── embed/
│   │   └── assinatura_embed.feature   
│   └── steps/
│       ├── common/auth_steps.py       # login reaproveitado entre features
│       ├── login/login_steps.py
│       ├── envios/envio_steps.py
│       ├── cofres/cofre_steps.py
│       └── embed/embed_steps.py
├── pages/
│   ├── base_page.py            # Waits, clicks, upload, modais (Playwright)
│   ├── login/login_page.py
│   ├── envios/
│   │   ├── envio_page.py
│   │   └── envio_locators.py   # Seletores Playwright (CSS / xpath=)
│   ├── cofres/
│   │   ├── cofre_page.py       # Pesquisa, abertura e contagem no cofre
│   │   └── cofre_locators.py
│   └── embed/
│       ├── embed_page.py       # Monta o embed e conta canvas da viewblob
│       └── embed_locators.py
├── recursos/utils/
│   ├── config.py               # .env → Config (URLs, embed, timeouts)
│   ├── driver_factory.py       # sync_playwright → BrowserDriver
│   ├── evidence.py             # Screenshots, frames → MP4, trace .zip
│   ├── create_env_ci.py        # Gera .env no CI a partir de secrets
│   └── generate_job_summary.py # Summary do GitHub Actions
├── data/files/                 # PDF / XLSX usados nos uploads
├── reports/                    # HTML, JSON, screenshots, vídeos, traces (gitignored)
├── .github/workflows/ci.yml    # Pipeline "Automação Web"
├── behave.ini
├── requirements.txt
├── .env.exemplo
└── README.md
```

---

## Pré-requisitos

- **Python 3.10+** (CI usa 3.12; local com 3.14 também funciona com Playwright recente)
- **pip**
- Conta de teste na D4Sign (ambiente de QA preferencialmente)
- Chromium via Playwright (`python -m playwright install chromium`)

---

## Instalação

```bash
git clone https://github.com/Auditeste-Lab/d4sign-web-tests-playwright.git
cd d4sign-web-tests-playwright

python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
python -m playwright install chromium

# Windows
copy .env.exemplo .env

# Linux / macOS
cp .env.exemplo .env
```

Edite o `.env` com credenciais reais. Prefira ambientes de QA (`homol`, `staging`, `hotfix`). Evite `prod` na automação local, salvo necessidade explícita.

---

## Configuração (.env)

Copie de `.env.exemplo`. Variáveis principais:

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `ENVIRONMENT` | `prod` | `prod`, `homol`, `staging`, `hotfix` |
| `D4S_USERNAME` | — | E-mail de login (`D4S_` evita conflito com `USERNAME` do Windows) |
| `D4S_PASSWORD` | — | Senha |
| `TOKEN_API` | — | Token de API (opcional) |
| `CRYPT_KEY` | — | Crypt key (opcional) |
| `EMAIL_TESTE` | — | E-mail auxiliar para signatários |
| `EMBED_DOCUMENT_UUID_<AMBIENTE>` | — | UUID do documento exibido no teste de embed (sufixo `_PROD`/`_HOMOL`/`_STAGING`) |
| `BROWSER` | `chrome` | `chrome` / `chromium` (Firefox/WebKit experimentais) |
| `HEADLESS` | `false` | `true` no CI; `false` para ver o browser |
| `TIMEOUT` | `60` | Timeout padrão de waits (segundos) |
| `LOGIN_TIMEOUT` | `20` | Timeout específico do login |
| `SCREENSHOT_ON_FAIL` | `true` | PNG em falha + embed no HTML |
| `RECORD_VIDEO` | `true` | Vídeo MP4 **somente se o cenário falhar** (ou sempre, com `EVIDENCE_ALWAYS=true`) |
| `RECORD_TRACE` | `true` | Trace Playwright (`.zip`) **somente se o cenário falhar** (ou sempre, com `EVIDENCE_ALWAYS=true`) |
| `EVIDENCE_ALWAYS` | `false` | `true` = screenshot de todo step + vídeo/trace completos em todo cenário, mesmo passando. Uso local; deixe `false` no CI |

### Ambientes D4Sign

| `ENVIRONMENT` | URL base |
|---------------|----------|
| `prod` | https://secure.d4sign.com.br/ |
| `homol` | https://homol.d4sign.com.br/ |
| `staging` | https://stage.d4sign.com.br/ |
| `hotfix` | https://hotfix.d4sign.com.br/ |

URLs derivadas: `/login.html` (login), `/desk` (desk) e `/embed/viewblob` (embed). O cenário de embed abre o editor Tryit do W3Schools e aponta o iframe para o documento de `EMBED_DOCUMENT_UUID_<AMBIENTE>`. O teste só visualiza a viewblob e conta os canvas; não assina.

---

## Como executar

### Comandos úteis

```bash
# Suíte completa (30 cenários)
behave features/ -f pretty

# Por tag
behave --tags=@login -f pretty
behave --tags=@envio -f pretty
behave --tags=@critical -f pretty
behave --tags=@erro -f pretty
behave --tags=@pin -f pretty
behave --tags=@batch -f pretty
behave --tags=@cofre -f pretty
behave --tags=@embed -f pretty

# Feature específica
behave features/envios/envio_desk.feature -f pretty
behave features/login/login.feature -f pretty
behave features/cofres/consulta_cofre.feature -f pretty
behave features/embed/assinatura_embed.feature -f pretty

# Dry-run (lista cenários sem abrir browser)
behave features/ --dry-run --format progress

# Relatório HTML + pretty
mkdir reports
behave features/ -f pretty -f html -o reports/behave_report.html
```

### Headless local

No `.env`:

```env
HEADLESS=true
```

Em headed (`HEADLESS=false`), o Chromium sobe **maximizado** e sem viewport emulado (usa o tamanho real da janela).

---

## Tags

| Tag | Efeito |
|-----|--------|
| `@login` | Autenticação; **reusa o mesmo browser** entre cenários da feature e **não** injeta cookies de um login anterior |
| `@envio` | Fluxos de envio / assinatura / pin |
| `@signature` | **Mantém sessão e documento** entre cenários da mesma feature (como Suite Setup no Robot) |
| `@critical` / `@smoke` | Subconjunto de validação rápida |
| `@erro` | Cenários negativos de envio |
| `@pin` | Pins / canvas |
| `@template` | Template HTML |
| `@batch` | Envio em lote (`envio_lote.feature`) |
| `@cofre` | Consulta de cofre, pasta e subpasta. `@cofre-normal` e `@cofre-compartilhado` separam os dois fluxos; `@pasta` e `@subpasta` marcam os mesmos cenários |
| `@embed` | Visualização da viewblob no Tryit, sem assinar |
| `@ui` / `@regression` | Classificação de suíte |

### Sessão do navegador

- Features com `@login` ou `@signature` **não fecham** o browser entre cenários.
- A sessão Playwright fica em `context.pw["driver"]` (nível feature), para não ser apagada pelo stack do Behave.
- O login pela tela acontece uma vez por execução. Os cookies ficam em memória (`Config`) e a feature seguinte abre já autenticada. Só `@login` começa sem essa sessão, porque testa o formulário.
- Rodar uma feature sozinha (por exemplo `@batch`) sempre faz o login completo: não há cookies de uma execução anterior.
- Fechar o browser manualmente no meio da feature pode gerar `TargetClosedError` e, ao reabrir, `Sync API inside the asyncio loop` (não chame `sync_playwright().start()` duas vezes no mesmo thread sem `quit()`).

---

## Arquitetura e convenções

### Camadas

1. **Feature (Gherkin)** — linguagem de negócio, sem detalhes de UI  
2. **Steps** — orquestram pages; asserts nos `Then`  
3. **Page Objects** — locators + ações de UI  
4. **BasePage** — waits, click seguro, upload, dismiss de modais  
5. **BrowserDriver** — wrapper Playwright (`page`, `current_url`, `save_screenshot`, `quit`)

### Regras

- Gherkin sempre com `# language: pt`
- Locators como strings Playwright: `#id`, `.css`, `xpath=//...`
- Credenciais **somente** via `.env` / `Config`
- Antes de cliques críticos: `dismiss_modals_if_present()` / `dismiss_blocking_modals()`
- Upload: `set_input_files` (não `send_keys` de Selenium)
- Novo fluxo: `features/<domínio>/`, `features/steps/<domínio>/`, `pages/<domínio>/` (como `cofres/` e `embed/`)

### Skills Cursor

Em `.cursor/skills/`:

- `automacao-web-qa` — criar features / pages / steps  
- `migracao-automacao-qa` — migrar Robot Framework → Behave/Playwright  

---

## Evidências e relatórios

| Artefato | Onde | Quando |
|----------|------|--------|
| Screenshot de falha | `reports/screenshots/` | Step/cenário failed + `SCREENSHOT_ON_FAIL=true` |
| Vídeo MP4 | `reports/videos/` | Só em falha (`RECORD_VIDEO=true`) |
| Trace Playwright (`.zip`) | `reports/traces/` | Só em falha (`RECORD_TRACE=true`) |
| Report HTML | `reports/behave_report.html` | Com `-f html -o ...` |
| Report JSON | `reports/behave.json` | CI / formato json |
| Log console | `reports/behave_console.log` | CI |

No HTML, falhas podem embutir screenshot e URL do momento do erro.

Por padrão, screenshot/vídeo/trace só são gerados **na falha**. Pra ter evidência de **todos** os cenários (passando ou não) — útil pra debugar localmente e acompanhar o fluxo completo — ative no `.env`:

```env
EVIDENCE_ALWAYS=true
```

Com isso: screenshot de cada step (anexado no HTML) e vídeo MP4 + trace completos de todo cenário, não só dos que falharem. Deixe `false` (padrão) no CI pra não inflar o artefato.

### Trace Viewer (recomendado para debugar)

O [Playwright Trace Viewer](https://playwright.dev/python/docs/trace-viewer) já vem embutido no `playwright` (nenhuma instalação extra — sem Java, sem Node). Pra cada cenário que falha (ou todos, com `EVIDENCE_ALWAYS=true`), é salvo um `.zip` em `reports/traces/` com:

- Timeline de cada ação (click, fill, goto, assert) com duração
- Snapshot do **DOM antes/depois** de cada ação — dá pra ver exatamente "o que mudou"
- O elemento-alvo destacado visualmente em cada passo
- Console do navegador e chamadas de rede
- Quando um locator falha, mostra o que ele esperava encontrar e o que existia na página

O caminho do `.zip` é impresso no console ao final do cenário (`Trace: reports/traces/...zip`). Pra abrir:

```bash
# Opção 1: viewer local (abre no navegador, sem instalar nada)
python -m playwright show-trace reports/traces/<arquivo>.zip

# Opção 2: arraste o .zip para https://trace.playwright.dev (sem instalar nada, roda 100% no navegador)
```

---

## CI (GitHub Actions)

Workflow: `.github/workflows/ci.yml` (nome da pipeline: **Automação Web**)

**Triggers:** push/PR em `main`/`master`, e `workflow_dispatch` (ambiente + tags opcionais).

**Passos principais:**

1. Python 3.12  
2. `pip install -r requirements.txt`  
3. `python -m playwright install --with-deps chromium` + Xvfb  
4. Gera `.env` via `create_env_ci.py` (secrets). `HEADLESS=false`: o Chrome abre numa tela virtual (`xvfb-run`), porque o login não completa no Chromium headless do runner  
5. Dry-run + execução Behave (progress + HTML + JSON)  
6. Job Summary + upload do artefato `behave-reports` (pasta `reports/` inteira)

**Secrets:** `USERNAME`, `PASSWORD`, `TOKEN_API`, `CRYPT_KEY`, `EMAIL_TESTE`. No workflow, `USERNAME` e `PASSWORD` entram no `.env` como `D4S_USERNAME` e `D4S_PASSWORD`.  
**Variable:** `ENVIRONMENT` (opcional; usada em push/PR; padrão `prod`)

No disparo manual (**Run workflow**), além do branch, há dois campos:

| Campo | Efeito |
|-------|--------|
| **Ambiente** | `prod`, `homol`, `staging` ou `hotfix`. Define a URL base da execução. Ghost não aparece e é recusado se a variable `ENVIRONMENT` vier com esse valor. |
| **Tags** | Filtra cenários (`@critical`, `@erro`, `@cofre`, `@embed`, …). Vazio = suíte completa. |

Push e pull request não mostram esses campos: o ambiente vem da variable `ENVIRONMENT` do repositório, ou `prod` se ela não existir. As mesmas credenciais (secrets) valem para todos os ambientes; o que muda é a URL.

`RECORD_TRACE=true` no CI, com `EVIDENCE_ALWAYS=false`. O trace é coletado em todo cenário e o `.zip` só é gravado em `reports/traces/` quando o cenário falha. Esse arquivo vai no artefato `behave-reports`, na execução da pipeline (seção Artifacts). Cenário que passa descarta o trace ao encerrar.

---

## Tempo de execução

| Escopo | Ordem de grandeza |
|--------|-------------------|
| `@login` (7 cenários) | ~1–2 min |
| `@critical` | ~5–15 min |
| Suíte completa (30) | **~30–40 min** (headed/headless e rede) |
| `envio_lote` sozinho | pode passar de 10 min (polling de processamento) |

O timeout padrão de espera de negócio é `TIMEOUT=60`. Ações de UI sem prazo próprio usam `ACTION_TIMEOUT=30`. Fluxos mais longos (upload, assinatura, lote) passam um prazo próprio no Page Object.

---

## Troubleshooting

### `Sync API inside the asyncio loop`

Causa comum: segundo `sync_playwright().start()` no mesmo thread sem fechar a sessão anterior (Behave apagava `context.driver` entre cenários).  
Mitigação já no projeto: sessão em `context.pw` + `quit()` só no fim da feature quando aplicável.

### `strict mode violation` / vários elementos

Playwright exige locator único em modo strict. O `BasePage` usa `.first` (equivalente ao `find_element` do Selenium). Prefira seletores mais específicos (ex.: `#formUpload select[name='uuid-cofre']`).

### `Target page, context or browser has been closed`

Browser foi fechado no meio da feature `@signature` / `@login`. Não misture `quit()` manual com reuso de sessão.

### Select de cofre “hidden”

Na desk existem selects `uuid-cofre` ocultos. O fluxo de upload usa o select **dentro de** `#formUpload` / `.modal.in`.

### Resolução / UI “esmagada”

Com `HEADLESS=false`, a janela sobe maximizada e `viewport=None` (sem emulação). Com `HEADLESS=true`, viewport fixo **1920×1080**.

### Instalação no Python 3.14

Use `playwright>=1.55` (requirements já flexível) para pegar wheels de `greenlet` compatíveis. Depois:

```bash
python -m playwright install chromium
```

---

## Dados de teste

Arquivos em `data/files/`:

| Arquivo | Uso |
|---------|-----|
| `doc-testes.pdf` | Upload padrão (desk / cofre / anexo) |
| `doc-substituto.pdf` | Substituição de documento |
| `planilha.xlsx` | Envio em lote |

---

## Licença / uso

Projeto interno de automação QA (Auditeste / D4Sign). Credenciais e tokens não devem ser commitados — use `.env` (gitignored) e secrets do GitHub Actions.
