"""Gera .env no CI a partir de variáveis de ambiente (sem sed)."""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENV_EXAMPLE = ROOT / ".env.exemplo"
ENV_FILE = ROOT / ".env"

OVERRIDES = {
    "ENVIRONMENT": os.environ.get("ENVIRONMENT", "prod"),
    "D4S_USERNAME": os.environ.get("D4S_USERNAME", ""),
    "D4S_PASSWORD": os.environ.get("D4S_PASSWORD", ""),
    "TOKEN_API": os.environ.get("TOKEN_API", ""),
    "CRYPT_KEY": os.environ.get("CRYPT_KEY", ""),
    "EMAIL_TESTE": os.environ.get("EMAIL_TESTE", ""),
    "HEADLESS": os.environ.get("HEADLESS", "true"),
    "RECORD_VIDEO": os.environ.get("RECORD_VIDEO", "false"),
    "TIMEOUT": os.environ.get("TIMEOUT", "360"),
}


def main() -> int:
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
