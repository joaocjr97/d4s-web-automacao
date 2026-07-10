# D4Sign Web Tests — Behave + Selenium

Suíte de automação web da plataforma D4Sign com **Behave (BDD)**, **Page Object** e **Selenium**.

Repositório: [Auditeste-Lab/d4sign-web-tests-behave](https://github.com/Auditeste-Lab/d4sign-web-tests-behave)

## Cobertura

| Área | Feature | Cenários |
|------|---------|----------|
| Login | `features/login/login.feature` | 7 |
| Envios | desk, cofre, assinatura, grupo, template HTML, lote, powerform, pin, canvas | 14 |
| **Total** | 10 features | **21** |

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

Edite o `.env` com credenciais e ambiente antes de executar.

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
| `ENVIRONMENT` | `ghost`, `homol`, `staging`, `hotfix`, `prod` |
| `D4S_USERNAME` / `D4S_PASSWORD` | Credenciais de login |
| `TOKEN_API` / `CRYPT_KEY` | Chaves de API |
| `EMAIL_TESTE` | E-mail para cenários de signatário |
| `HEADLESS` | `true` ou `false` |
| `SCREENSHOT_ON_FAIL` | Screenshot automático em falha |
| `RECORD_VIDEO` | Evidências visuais do cenário |

### Ambientes D4Sign

| Ambiente | URL |
|----------|-----|
| prod | https://secure.d4sign.com.br/ |
| staging | https://stage.d4sign.com.br/ |
| homol | https://homol.d4sign.com.br/ |
| ghost | https://ghost.d4sign.com.br/ |
| hotfix | https://hotfix.d4sign.com.br/ |

## Relatórios

- HTML: `reports/behave_report.html`
- Screenshots: `reports/screenshots/`
- Evidências: `reports/videos/`

## CI

O workflow em `.github/workflows/ci.yml` executa os testes com tag `@smoke` em cada push/PR na branch `main`.

Secrets necessários no GitHub: `USERNAME`, `PASSWORD`, `TOKEN_API`, `CRYPT_KEY`, `EMAIL_TESTE`.
