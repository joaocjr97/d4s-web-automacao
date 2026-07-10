---
name: migracao-automacao-qa
description: Migra testes Robot Framework (robot-D4S) para Behave/Selenium no template-web-tests-python. Use ao converter .robot para .feature, keywords para Page Objects, ou config_sensitive para .env.
---

# Migração Robot → Behave

## Mapeamento

| Robot Framework | Novo framework |
|-----------------|----------------|
| `tests/web/**/*.robot` | `features/**/*.feature` |
| `*** Test Cases ***` | `Cenário:` no Gherkin |
| `resources/ui/ui_keywords.robot` | `pages/` + steps compartilhados |
| `resources/common/variables.robot` | Locators nas Page Objects |
| `config_sensitive.robot` | `.env` |
| `config_environment.robot` | `recursos/utils/config.py` |
| `Suite Setup` / `Test Setup` | `features/environment.py` hooks |
| `results/` | `reports/` |

## Passo a passo

1. **Ler** o `.robot` legado (Settings, Variables, Test Cases, Keywords)
2. **Extrair** locators para uma Page Object em `pages/<dominio>/`
3. **Converter** cada Test Case em um `Cenário:` Gherkin
4. **Implementar** steps em `features/steps/<dominio>/`
5. **Reutilizar** login via `LoginPage.fazer_login()` no `Given`
6. **Tratar modais** com `BasePage.dismiss_modals_if_present()`
7. **Validar** com `behave --tags=@<tag>`

## Conversão de keywords

```robot
# Robot
Click Element    ${btnSalvar}
Wait Until Element Is Visible    ${logoD4S}    ${TIMEOUT}
```

```python
# Page Object
self.click(self.BTN_SALVAR)
self.wait_visible(self.LOGO_D4S)
```

## Cenários de envios a migrar (robot-D4S)

1. envio-assinatura: Envio, Assinatura
2. envio-cofre: Envio
3. envio-desk: Envio
4. envio-powerform: Preparação do PowerForm
5. envio-template-html: Preenchimento, Envio do Documento, Assinatura do Template
6. pin: Envio anexo/canvas, Adicionar pin
7. envio-grupo-assinatura: Upload de Documento, Envio para Grupo
8. envio-canvas-pins: Envio
9. envio-lote: Envio em Lote

## Erros conhecidos na migração

- **modal-backdrop** e **#modal-aviso-analizer** bloqueiam cliques → fechar no `BasePage`
- XPath longos em `page-wrapper` → revisar seletores na UI atual
- IDs dinâmicos (ex. PowerForm email) → usar partial match ou data attributes

## Comando pós-migração

```bash
behave features/<dominio>/ -f pretty -f html -o reports/behave_report.html
```
