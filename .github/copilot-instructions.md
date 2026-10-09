# Copilot / IA — Automação Web D4Sign

- Use Behave com Gherkin em português (`# language: pt`).
- Stack: Behave + Playwright (Page Objects em `pages/`; steps em `features/steps/`).
- Locators como seletores Playwright (`#id`, `xpath=//...`), sem Selenium `By.*`.
- Credenciais somente em `.env`, nunca no código.
- Reutilize `BasePage` e `LoginPage` para novos fluxos.
- Screenshots automáticos em falha via `features/environment.py`.
- Tags sugeridas: `@smoke`, `@critical`, `@login`, `@envio`, `@ui`.
