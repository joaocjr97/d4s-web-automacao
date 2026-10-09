"""Gera .env no CI a partir de variáveis de ambiente (sem sed)."""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENV_EXAMPLE = ROOT / ".env.exemplo"
ENV_FILE = ROOT / ".env"


def _env(nome: str, default: str = "") -> str:
    """Lê a variável e remove espaços/quebras de linha nas bordas.

    Um secret do GitHub com espaço, tab ou newline colado na borda (comum ao
    copiar/colar o valor) quebra o arquivo .env: o newline encerra a linha
    "CHAVE=" antes do valor, e o restante vira uma linha solta que o
    python-dotenv ignora — a chave fica vazia mesmo com o secret preenchido.
    """
    return (os.environ.get(nome) or default).strip()


# Ghost fica de fora: a suíte não aponta para https://ghost.d4sign.com.br/.
AMBIENTES_PERMITIDOS = {"prod", "secure", "homol", "staging", "stage", "hotfix"}

OVERRIDES = {
    "ENVIRONMENT": _env("ENVIRONMENT", "prod").lower(),
    "D4S_USERNAME": _env("D4S_USERNAME"),
    "D4S_PASSWORD": _env("D4S_PASSWORD"),
    "TOKEN_API": _env("TOKEN_API"),
    "CRYPT_KEY": _env("CRYPT_KEY"),
    "EMAIL_TESTE": _env("EMAIL_TESTE"),
    "HEADLESS": _env("HEADLESS", "true"),
    "RECORD_VIDEO": _env("RECORD_VIDEO", "true"),
    "SCREENSHOT_ON_FAIL": _env("SCREENSHOT_ON_FAIL", "true"),
    "RECORD_TRACE": _env("RECORD_TRACE", "false"),
    "TIMEOUT": _env("TIMEOUT", "60"),
    "ACTION_TIMEOUT": _env("ACTION_TIMEOUT", "30"),
}


def main() -> int:
    ambiente = OVERRIDES["ENVIRONMENT"]
    if ambiente == "ghost":
        print(
            "Ambiente ghost não é executado nesta suíte. "
            "Use prod, homol, staging ou hotfix.",
            file=sys.stderr,
        )
        return 1
    if ambiente not in AMBIENTES_PERMITIDOS:
        print(
            f"ENVIRONMENT inválido: {ambiente}. "
            "Use prod, homol, staging ou hotfix.",
            file=sys.stderr,
        )
        return 1

    if not ENV_EXAMPLE.exists():
        print(f"Arquivo não encontrado: {ENV_EXAMPLE}", file=sys.stderr)
        return 1

    lines: list[str] = []
    for raw in ENV_EXAMPLE.read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.strip().startswith("#"):
            lines.append(raw)
            continue
        key = raw.split("=", 1)[0].strip()
        if key in OVERRIDES:
            lines.append(f"{key}={OVERRIDES[key]}")
        else:
            lines.append(raw)

    ENV_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")

    missing = [k for k in ("D4S_USERNAME", "D4S_PASSWORD") if not OVERRIDES.get(k)]
    if missing:
        print(f"Secrets ausentes: {', '.join(missing)}", file=sys.stderr)
        return 1

    print(f".env criado em {ENV_FILE}")
    print(f"ENVIRONMENT={next((l.split('=',1)[1] for l in lines if l.startswith('ENVIRONMENT=')), 'prod')}")
    print(f"HEADLESS={OVERRIDES['HEADLESS']}")
    print(f"TIMEOUT={OVERRIDES['TIMEOUT']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
