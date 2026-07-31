---
name: automacao-web-qa
description: Gera cenários Behave/Gherkin em português e Page Objects Playwright para automação web D4Sign. Use ao criar novos testes web, features, steps ou pages no template-web-tests-python.
---

# Automação Web QA — D4Sign

## Quando usar

- Criar novos cenários BDD para fluxos web da D4Sign
- Adicionar Page Objects ou steps
- Expandir cobertura além do login

## Padrão do projeto

```
features/<dominio>/<nome>.feature
features/steps/<dominio>/<nome>_steps.py
pages/<dominio>/<nome>_page.py
```

## Regras

1. Gherkin em **português** com `# language: pt` no topo do `.feature`
2. Steps reutilizáveis; lógica de UI apenas em **Page Objects**
3. Locators centralizados como seletores Playwright (CSS `#id`, `xpath=//...`)
4. Credenciais e URLs via `Config` / `.env` — nunca hardcoded
5. Herdar de `BasePage` e usar `dismiss_modals_if_present()` antes de cliques críticos
6. Tags: `@smoke`, `@critical`, `@envio`, `@ui`, `@login`
7. Stack: **Behave + Playwright** (sync API); `context.driver` é `BrowserDriver`

## Template de feature

```gherkin
# language: pt

Funcionalidade: <Nome do fluxo>
  Como <persona>
  Quero <ação>
  Para <benefício>

  @<tag>
  Cenário: <Nome do cenário>
    Dado que estou logado na plataforma
    Quando <ação>
    Então <resultado esperado>
```

## Template de step

```python
from behave import given, when, then
from pages.<dominio>.<page>_page import <Page>Page

@given("que estou logado na plataforma")
def usuario_logado(context):
    context.login_page = LoginPage(context.driver)
    context.login_page.fazer_login()
```

## Checklist antes de entregar

- [ ] Feature com cenário legível para negócio
- [ ] Page Object sem asserts (asserts ficam nos steps)
- [ ] Step definitions com nomes em português
- [ ] Tag adequada para execução seletiva (`behave --tags=@envio`)
