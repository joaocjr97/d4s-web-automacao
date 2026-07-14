# D4Sign Web Tests — Behave + Selenium

Suíte de automação web da plataforma D4Sign com **Behave (BDD)**, **Page Object** e **Selenium**.

Repositório: [Auditeste-Lab/d4sign-web-tests-behave](https://github.com/Auditeste-Lab/d4sign-web-tests-behave)

## Cobertura

| Área | Feature | Cenários |
|------|---------|----------|
| Login | `features/login/login.feature` | 7 |
| Envios | desk, cofre, assinatura, grupo, template HTML, lote, powerform, pin, canvas, reaproveitamento, substituição, tipos de pin | 17 |
| Erros de envio | limite 20MB, sem signatário, e-mail inválido, senha incorreta | 4 |
| **Total** | 14 features | **28** |

## Estrutura

```
d4sign-web-tests-behave/
├── features/          # Cenários Gherkin (.feature) e steps
├── pages/             # Page Objects e locators
├── recursos/utils/    # Config, driver, evidências
├── data/files/        # PDF e planilha usados nos testes
├── reports/           # Relatórios e screenshots (gitignored)
└── .cursor/skills/    # Skills de IA para QA
```

## Pré-requisitos

- Python 3.10+
- Google Chrome instalado
- pip

## Instalação

```bash
git clone https://github.com/Auditeste-Lab/d4sign-web-tests-behave.git
cd d4sign-web-tests-behave
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/Mac
pip install -r requirements.txt
copy .env.exemplo .env       # Windows
cp .env.exemplo .env         # Linux/Mac
```

Edite o `.env` com credenciais e ambiente de **QA** (`homol`, `ghost`, `staging` ou `hotfix`). Não use `prod` na automação.

## Executar testes

```bash
# Login
behave --tags=@login -f pretty

# Todos os envios (14 cenários)
behave --tags=@envio -f pretty

# Smoke / críticos
behave --tags=@critical -f pretty

# Suíte completa (21 cenários)
behave features/ -f pretty

# Relatório HTML
behave features/ -f pretty -f html -o reports/behave_report.html
```

## Tags

| Tag | Uso |
|-----|-----|
| `@login` | Cenários de autenticação |
| `@envio` | Fluxos de envio e assinatura |
| `@signature` | Mantém sessão entre cenários da mesma feature |
| `@smoke` / `@critical` | Execução rápida no CI |
| `@ui` / `@regression` | Classificação de suíte |

## Variáveis de ambiente (.env)

| Variável | Descrição |
|----------|-----------|
| `ENVIRONMENT` | `prod` (padrão), `ghost`, `homol`, `staging`, `hotfix` |
| `D4S_USERNAME` / `D4S_PASSWORD` | Credenciais de login |
| `TOKEN_API` / `CRYPT_KEY` | Chaves de API |
| `EMAIL_TESTE` | E-mail para cenários de signatário |
| `HEADLESS` | `true` ou `false` |
| `SCREENSHOT_ON_FAIL` | Screenshot automático em falha |
| `RECORD_VIDEO` | Evidências visuais do cenário |

### Ambientes D4Sign

| Ambiente | URL |
|----------|-----|
| **prod** | https://secure.d4sign.com.br/ |
| homol | https://homol.d4sign.com.br/ |
| ghost | https://ghost.d4sign.com.br/ |
| staging | https://stage.d4sign.com.br/ |
| hotfix | https://hotfix.d4sign.com.br/ |

## CI (GitHub Actions)

Secrets: `USERNAME`, `PASSWORD`, `TOKEN_API`, `CRYPT_KEY`, `EMAIL_TESTE`

Variable opcional: `ENVIRONMENT` (padrão `prod` → secure.d4sign.com.br)

O workflow executa `@critical` no push e a suíte completa no disparo manual.

Após a execução, a aba **Summary** do job exibe um relatório Markdown com:
- total de passed/failed/skipped
- tabela por categoria
- passos por cenário
- link para o artefato `behave-reports`

O artefato `behave-reports` inclui HTML, JSON, log, `screenshots/` (falhas) e `videos/` (evidência visual do cenário).

## Relatórios

- Job Summary: aba Summary do GitHub Actions
- HTML: `reports/behave_report.html`
- JSON: `reports/behave.json`
- Screenshots: `reports/screenshots/`
- Vídeos MP4: `reports/videos/` (frames capturados a cada step com `RECORD_VIDEO=true`)
- Evidências: `reports/videos/`
