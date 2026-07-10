# Template Web Tests — D4Sign

Automação web com **Behave (BDD)**, **Page Object** e **Selenium**.

## Estrutura

```
template-web-tests-python/
├── features/          # Cenários Gherkin (.feature) e steps
├── pages/             # Page Objects
├── recursos/utils/    # Config, driver, evidências
├── reports/           # Relatórios e screenshots (gitignored)
├── Docs/              # Documentação
└── .cursor/skills/    # Skills de IA para QA
```

## Pré-requisitos

- Python 3.10+
- Google Chrome instalado
- pip

## Instalação

```bash
cd template-web-tests-python
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
cp .env.exemplo .env         # Linux/Mac
copy .env.exemplo .env       # Windows
```

Edite o `.env` com suas credenciais e ambiente.

## Executar testes

```bash
# Login
behave --tags=@login -f pretty

# Todos os envios (14 cenários)
behave --tags=@envio -f pretty

# Smoke / críticos
behave --tags=@critical -f pretty

# Relatório HTML
behave --tags=@envio -f pretty -f html -o reports/behave_report.html
```

## Variáveis de ambiente (.env)

| Variável | Descrição |
|----------|-----------|
| `ENVIRONMENT` | ghost, homol, staging, hotfix, prod |
| `D4S_USERNAME` / `D4S_PASSWORD` | Credenciais de login (use estes no Windows) |
| `TOKEN_API` / `CRYPT_KEY` | Chaves de API |
| `EMAIL_TESTE` | E-mail para cenários de signatário |
| `HEADLESS` | `true` ou `false` |
| `SCREENSHOT_ON_FAIL` | Screenshot automático em falha |
| `RECORD_VIDEO` | Evidências visuais do cenário |

## Relatórios

- HTML: `reports/behave_report.html`
- Screenshots: `reports/screenshots/`
- Evidências: `reports/videos/`

## Migração do Robot Framework

Use a skill `.cursor/skills/migracao-automacao-qa/` para migrar suites do `robot-D4S`.

Mapeamento:

| Robot | Behave |
|-------|--------|
| `tests/web/*.robot` | `features/**/*.feature` |
| `resources/ui/*.robot` | `pages/**/*.py` |
| `config_sensitive.robot` | `.env` |
