"""Gera Job Summary do GitHub Actions a partir do JSON do Behave."""

from __future__ import annotations

import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "reports"
JSON_REPORT = REPORTS / "behave.json"


def _duracao(status) -> float:
    try:
        return float((status or {}).get("duration") or 0)
    except (TypeError, ValueError):
        return 0.0


def _fmt_duracao(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.2f} s"
    minutos = int(seconds // 60)
    resto = seconds % 60
    return f"{minutos}m {resto:.1f}s"


def _status_label(status: str) -> str:
    status = (status or "").lower()
    if status == "passed":
        return "✅ passed"
    if status == "failed":
        return "❌ failed"
    if status in {"skipped", "untested"}:
        return "⏭ skipped"
    return f"⚪ {status or 'unknown'}"


def _categoria(feature_name: str, filename: str) -> str:
    tags_map = {
        "login": "Autenticação",
        "assinatura": "Assinatura",
        "pin": "Pins / Canvas",
        "canvas": "Pins / Canvas",
        "cofre": "Envio",
        "desk": "Envio",
        "grupo": "Envio",
        "template": "Template",
        "lote": "Lote",
        "powerform": "PowerForm",
    }
    texto = f"{feature_name} {filename}".lower()
    for chave, nome in tags_map.items():
        if chave in texto:
            return nome
    return "Outros"


CONSOLE_LOG = REPORTS / "behave_console.log"


def _parse_status_from_console() -> list[dict]:
    """Fallback quando o JSON não foi gerado corretamente."""
    if not CONSOLE_LOG.exists():
        return []

    texto = CONSOLE_LOG.read_text(encoding="utf-8", errors="replace")
    cenarios: list[dict] = []
    feature_atual = "Feature"

    for linha in texto.splitlines():
        feature_match = re.search(r">> Feature:\s*(.+)$", linha)
        if feature_match:
            feature_atual = feature_match.group(1).strip()
            continue

        cenario_match = re.search(
            r"OK Cenario finalizado:\s*(.+?)\s*\(Status\.(\w+)\)",
            linha,
        )
        if not cenario_match:
            continue

        nome = cenario_match.group(1).strip()
        status = cenario_match.group(2).strip().lower()
        cenarios.append(
            {
                "feature": feature_atual,
                "categoria": _categoria(feature_atual, ""),
                "nome": nome,
                "status": status,
                "duracao": 0.0,
                "tags": [],
                "steps": [],
                "erro": "",
                "arquivo": "",
            }
        )
    return cenarios


def carregar_cenarios() -> list[dict]:
    if JSON_REPORT.exists() and JSON_REPORT.stat().st_size > 0:
        raw = JSON_REPORT.read_text(encoding="utf-8").strip()
        if raw:
            try:
                data = json.loads(raw)
            except json.JSONDecodeError as exc:
                print(f"JSON inválido ({exc}); usando fallback do console.", file=sys.stderr)
                data = None
            if data is not None:
                cenarios: list[dict] = []
                for feature in data:
                    feature_name = feature.get("name") or "Feature"
                    filename = feature.get("location", "").split(":")[0]
                    categoria = _categoria(feature_name, filename)

                    for element in feature.get("elements", []):
                        if element.get("type") not in {"scenario", "scenario_outline"}:
                            continue

                        status = (element.get("status") or "unknown").lower()
                        steps = []
                        duration = 0.0
                        erro = ""

                        for step in element.get("steps", []) or []:
                            step_status = (step.get("result") or {}).get(
                                "status", "unknown"
                            )
                            step_duration = _duracao(step.get("result"))
                            duration += step_duration
                            keyword = step.get("keyword", "").strip()
                            name = step.get("name", "").strip()
                            steps.append(
                                {
                                    "status": step_status,
                                    "texto": f"{keyword} {name}".strip(),
                                    "duracao": step_duration,
                                }
                            )
                            if step_status == "failed" and not erro:
                                erro = (
                                    (step.get("result") or {}).get("error_message") or ""
                                ).strip()

                        tags = [
                            t.get("name", t) if isinstance(t, dict) else str(t)
                            for t in element.get("tags", [])
                        ]
                        cenarios.append(
                            {
                                "feature": feature_name,
                                "categoria": categoria,
                                "nome": element.get("name") or "Cenário",
                                "status": status,
                                "duracao": duration,
                                "tags": tags,
                                "steps": steps,
                                "erro": erro,
                                "arquivo": filename,
                            }
                        )
                if cenarios:
                    return cenarios

    fallback = _parse_status_from_console()
    if fallback:
        return fallback

    raise FileNotFoundError(
        "Não foi possível ler reports/behave.json nem reports/behave_console.log"
    )


def gerar_markdown(cenarios: list[dict]) -> str:
    passed = sum(1 for c in cenarios if c["status"] == "passed")
    failed = sum(1 for c in cenarios if c["status"] == "failed")
    skipped = sum(1 for c in cenarios if c["status"] in {"skipped", "untested"})
    steps_passed = sum(
        1 for c in cenarios for s in c["steps"] if s["status"] == "passed"
    )
    steps_failed = sum(
        1 for c in cenarios for s in c["steps"] if s["status"] == "failed"
    )
    steps_skipped = sum(
        1
        for c in cenarios
        for s in c["steps"]
        if s["status"] in {"skipped", "untested"}
    )

    badge = (
        f"`tests | {passed} passed`"
        if failed == 0
        else f"`tests | {failed} failed`"
    )

    lines = [
        "## Testes E2E (Behave) summary",
        "",
        f"**{passed} passed, {failed} failed and {skipped} skipped**",
        "",
        badge,
        "",
        "<details>",
        "<summary>Expand for details</summary>",
        "",
        "### 🧪 Resultado dos testes E2E (Behave)",
        "",
    ]

    por_categoria: dict[str, list[dict]] = defaultdict(list)
    for cenario in cenarios:
        por_categoria[cenario["categoria"]].append(cenario)

    for categoria, itens in sorted(por_categoria.items()):
        lines.extend(
            [
                f"#### 📁 {categoria}",
                "",
                "| Status | Cenário | Duração |",
                "|--------|---------|---------|",
            ]
        )
        for item in itens:
            nome = item["nome"].replace("|", "\\|")
            feature = item["feature"].replace("|", "\\|")
            lines.append(
                f"| {_status_label(item['status'])} | `[{feature}]` {nome} | {_fmt_duracao(item['duracao'])} |"
            )
        lines.append("")

    lines.extend(
        [
            "<details>",
            "<summary>Passos por cenário</summary>",
            "",
        ]
    )

    for item in cenarios:
        titulo = f"{item['feature']} — {item['nome']}"
        lines.extend([f"##### {titulo}", ""])
        if not item["steps"]:
            lines.append("_Sem passos registrados._")
            lines.append("")
            continue

        lines.extend(
            [
                "| Status | Passo | Duração |",
                "|--------|-------|---------|",
            ]
        )
        for step in item["steps"]:
            texto = step["texto"].replace("|", "\\|")
            lines.append(
                f"| {_status_label(step['status'])} | {texto} | {_fmt_duracao(step['duracao'])} |"
            )
        if item["erro"]:
            erro_curto = item["erro"].splitlines()[0][:300]
            lines.extend(["", f"> ❌ `{erro_curto}`"])
        lines.append("")

    lines.extend(
        [
            "</details>",
            "",
            "### Totais",
            "",
            "| | Cenários | Passos |",
            "|-|----------|--------|",
            f"| ✅ Passou | {passed} | {steps_passed} |",
            f"| ❌ Falhou | {failed} | {steps_failed} |",
            f"| ⏭ Ignorado | {skipped} | {steps_skipped} |",
            "",
            "📎 Baixe o artefato `behave-reports` para relatório HTML, screenshots e logs.",
            "",
            "</details>",
            "",
            "*Job summary generated at run-time.*",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    try:
        cenarios = carregar_cenarios()
    except Exception as exc:
        print(f"Falha ao gerar Job Summary: {exc}", file=sys.stderr)
        summary = (
            "## Testes E2E (Behave) summary\n\n"
            f"❌ Não foi possível gerar o resumo: `{exc}`\n\n"
            "📎 Baixe o artefato `behave-reports` para análise manual.\n"
        )
        destino = os.environ.get("GITHUB_STEP_SUMMARY")
        if destino:
            Path(destino).write_text(summary, encoding="utf-8")
        return 1

    markdown = gerar_markdown(cenarios)
    destino = os.environ.get("GITHUB_STEP_SUMMARY")
    if destino:
        Path(destino).write_text(markdown, encoding="utf-8")
        print(f"Job Summary gerado em {destino}")
    else:
        try:
            print(markdown)
        except UnicodeEncodeError:
            Path(REPORTS / "job_summary.md").write_text(markdown, encoding="utf-8")
            print(f"Job Summary salvo em {REPORTS / 'job_summary.md'}")

    failed = sum(1 for c in cenarios if c["status"] == "failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
