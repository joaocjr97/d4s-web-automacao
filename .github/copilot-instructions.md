# Copilot / IA — Automação Web D4Sign

- Use Behave com Gherkin em português (`# language: pt`).
- Page Objects em `pages/`; steps em `features/steps/`.
- Credenciais somente em `.env`, nunca no código.
- Reutilize `BasePage` e `LoginPage` para novos fluxos.
- Screenshots automáticos em falha via `features/environment.py`.
- Tags sugeridas: `@smoke`, `@critical`, `@login`, `@envio`, `@ui`.
