import os
import sys

# Evita a criação de pastas __pycache__ ao rodar a suíte.
sys.dont_write_bytecode = True

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from behave.formatter.base import StreamOpener

from recursos.utils.config import Config
from recursos.utils.driver_factory import create_driver
from recursos.utils.evidence import Evidence


def _abrir_stream_em_utf8(self):
    """No Windows o behave grava o report em cp1252, quebrando os acentos.

    O HTML declara utf-8 no <meta>, então forçamos a escrita em UTF-8.
    """
    if not self.stream or self.stream.closed:
        self.ensure_dir_exists(os.path.dirname(self.name))
        self.stream = open(self.name, "w", encoding="utf-8")
        self.should_close_stream = True
    return self.stream


StreamOpener.open = _abrir_stream_em_utf8

# Registra step definitions (subpastas)
import features.steps.login.login_steps as _login_steps  # noqa: F401
import features.steps.common.auth_steps as _auth_steps  # noqa: F401
import features.steps.envios.envio_steps as _envio_steps  # noqa: F401


def _coletar_tags_feature(feature) -> set[str]:
    tags = set(feature.tags or [])
    for scenario in feature.scenarios:
        tags.update(scenario.tags or [])
    return tags


def _feature_reusa_navegador(feature) -> bool:
    return bool(_coletar_tags_feature(feature) & {"login", "signature"})


def _feature_mantem_sessao(feature) -> bool:
    """Fluxos @signature continuam do cenário anterior (como no Robot)."""
    return "signature" in _coletar_tags_feature(feature)


def _limpar_sessao_navegador(context) -> None:
    driver = getattr(context, "driver", None)
    if driver is None:
        return
    try:
        if hasattr(driver, "clear_cookies"):
            driver.clear_cookies()
        else:
            driver.page.context.clear_cookies()
    except Exception:
        pass
    try:
        page = getattr(driver, "page", driver)
        page.evaluate(
            "() => { window.localStorage.clear(); window.sessionStorage.clear(); }"
        )
    except Exception:
        pass


def _ci_log(message: str) -> None:
    if os.getenv("CI", "").lower() in ("1", "true", "yes"):
        print(message.encode("ascii", errors="replace").decode("ascii"), flush=True)


def _embed_html_report(context, mime_type: str, data, caption: str) -> None:
    """Anexa evidência ao step atual no report HTML (se o formatter estiver ativo)."""
    runner = getattr(context, "_runner", None)
    for formatter in getattr(runner, "formatters", []) or []:
        if not hasattr(formatter, "embedding"):
            continue
        try:
            formatter.embedding(mime_type, data, caption)
            if mime_type.startswith("image/"):
                span = formatter.actual["act_step_embed_span"]
                imagens = span.findall("img")
                if imagens:
                    imagens[-1].set(
                        "style", "display: block; max-width: 1024px; margin: 4px 0;"
                    )
        except Exception:
            pass


def _anexar_evidencias_falha(context, step) -> None:
    import base64

    driver = getattr(context, "driver", None)
    if driver is None:
        return

    try:
        screenshot = context.evidence.capture_screenshot(driver, step.name)
        imagem_b64 = base64.b64encode(screenshot.read_bytes()).decode("ascii")
        _embed_html_report(context, "image/png", imagem_b64, "Screenshot da falha")
    except Exception:
        pass

    try:
        url = driver.current_url
        _embed_html_report(context, "text/plain", f"URL: {url}", "URL no momento da falha")
    except Exception:
        pass


def _obter_driver(context):
    pw = getattr(context, "pw", None) or {}
    return pw.get("driver") or getattr(context, "driver", None)


def _fechar_driver(context) -> None:
    driver = _obter_driver(context)
    if driver is None:
        return
    try:
        driver.quit()
    except Exception:
        pass
    if getattr(context, "pw", None) is not None:
        context.pw["driver"] = None
        context.pw["signature"] = None
    context.driver = None


def before_all(context):
    Config.load()
    context.config_obj = Config
    context.evidence = Evidence()


def before_feature(context, feature):
    _ci_log(f">> Feature: {feature.name}")
    context._reusar_navegador = _feature_reusa_navegador(feature)
    context._manter_sessao = _feature_mantem_sessao(feature)
    # Dict mutável no nível da feature: atribuir context.X=... no before_scenario
    # criaria sombra na camada do cenário (Behave stack) e a sessão se perderia,
    # causando 2º sync_playwright() → "Sync API inside the asyncio loop".
    context.pw = {"driver": None, "signature": None}


def before_scenario(context, scenario):
    _ci_log(f"  >> Cenario: {scenario.name}")
    manter_sessao = getattr(context, "_manter_sessao", False)
    driver_salvo = context.pw.get("signature")

    if manter_sessao and driver_salvo is not None:
        context.pw["driver"] = driver_salvo
    elif context.pw.get("driver") is None:
        _ci_log("    ... Abrindo navegador Playwright")
        context.pw["driver"] = create_driver(Config)
        _ci_log("    OK Navegador pronto")

    context.driver = context.pw["driver"]

    if manter_sessao:
        context.pw["signature"] = context.pw["driver"]

    for attr in ("envio_page", "login_page"):
        if hasattr(context, attr):
            delattr(context, attr)

    context.evidence.start_scenario(scenario.name, context.driver)


def after_step(context, step):
    driver = _obter_driver(context)
    if driver is None:
        return
    # Buffer rotativo: só vira MP4 se o cenário falhar; se passar, é descartado.
    if Config.RECORD_VIDEO:
        try:
            context.evidence.capture_frame(driver)
        except Exception:
            pass
    if step.status == "failed" and Config.SCREENSHOT_ON_FAIL:
        _anexar_evidencias_falha(context, step)


def after_scenario(context, scenario):
    driver = _obter_driver(context)
    _ci_log(f"  OK Cenario finalizado: {scenario.name} ({scenario.status})")
    if scenario.status == "failed" and driver is not None:
        try:
            _ci_log(f"    URL: {driver.current_url}")
        except Exception:
            pass
        if Config.SCREENSHOT_ON_FAIL:
            context.evidence.capture_screenshot(driver, scenario.name)

    if driver is not None:
        context.evidence.finish_scenario(driver, scenario.status)

    if getattr(context, "_manter_sessao", False):
        context.pw["signature"] = driver
        return

    if getattr(context, "_reusar_navegador", False):
        return

    _fechar_driver(context)


def after_feature(context, feature):
    if getattr(context, "_reusar_navegador", False):
        _fechar_driver(context)
    elif getattr(context, "pw", None) is not None:
        context.pw["driver"] = None
        context.pw["signature"] = None
    context.driver = None
