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
import features.steps.cofres.cofre_steps as _cofre_steps  # noqa: F401
import features.steps.embed.embed_steps as _embed_steps  # noqa: F401


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


def _feature_evita_cache_login(feature) -> bool:
    """Só @login testa o próprio fluxo de autenticação; precisa sempre
    começar de um contexto limpo (sem cookies cacheados).

    @signature NÃO entra aqui: são features "normais" (pin, envio, etc.)
    que só continuam a sessão entre cenários — devem reaproveitar o login
    cacheado normalmente, senão refazem o formulário de login a cada
    feature nova (driver reiniciado em before_feature).
    """
    return "login" in _coletar_tags_feature(feature)


def _ci_log(message: str) -> None:
    if os.getenv("CI", "").lower() in ("1", "true", "yes"):
        print(message.encode("ascii", errors="replace").decode("ascii"), flush=True)


def _log(message: str) -> None:
    """Print sempre (local e CI); ascii-safe pra não quebrar console cp1252 no Windows."""
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


def _anexar_evidencia_step_ok(context, step) -> None:
    """Screenshot de todo step (passou ou não) quando EVIDENCE_ALWAYS=true.

    Complementa a evidência de falha: aqui é só pra acompanhar visualmente
    o fluxo completo, não tenta capturar URL/HTML (isso já sai no da falha).
    """
    driver = _obter_driver(context)
    if driver is None:
        return

    try:
        screenshot = context.evidence.capture_screenshot(driver, step.name)
    except Exception:
        return

    try:
        import base64

        imagem_b64 = base64.b64encode(screenshot.read_bytes()).decode("ascii")
        _embed_html_report(context, "image/png", imagem_b64, f"Screenshot: {step.name}")
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
    context._evita_cache_login = _feature_evita_cache_login(feature)
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
        # Sessão de login cacheada é injetada em qualquer feature, exceto
        # @login: essa tag testa o próprio fluxo de autenticação e precisa
        # sempre de um contexto limpo (sem cookies). @signature reaproveita
        # o cache normalmente — senão o login completo via UI se repetiria
        # a cada feature nova (driver reiniciado em before_feature).
        usar_cache = not getattr(context, "_evita_cache_login", False)
        storage_state = Config.obter_estado_login() if usar_cache else None
        if not usar_cache:
            _log("    Cache de login ignorado (feature @login)")
        elif storage_state:
            _log("    Cache de login encontrado -> injetando cookies no navegador novo")
        else:
            _log("    Sem cache de login ainda (primeiro login desta execucao)")
        context.pw["driver"] = create_driver(Config, storage_state=storage_state)
        _ci_log("    OK Navegador pronto")

    context.driver = context.pw["driver"]

    if manter_sessao:
        context.pw["signature"] = context.pw["driver"]

    for attr in ("envio_page", "login_page", "cofre_page", "embed_page"):
        if hasattr(context, attr):
            delattr(context, attr)

    # Lista de contagens (cofres/pastas) do cenário de consulta; precisa
    # iniciar limpa aqui, não num step, senão um novo "pesquiso o cofre"
    # no meio do cenário apagaria as contagens já registradas.
    context.contagens = []

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
    if step.status == "failed":
        if Config.SCREENSHOT_ON_FAIL:
            _anexar_evidencias_falha(context, step)
    elif Config.EVIDENCE_ALWAYS:
        _anexar_evidencia_step_ok(context, step)


def after_scenario(context, scenario):
    driver = _obter_driver(context)
    _ci_log(f"  OK Cenario finalizado: {scenario.name} ({scenario.status})")
    if scenario.status == "failed" and driver is not None:
        try:
            _ci_log(f"    URL: {driver.current_url}")
        except Exception:
            pass
        if Config.SCREENSHOT_ON_FAIL:
            try:
                context.evidence.capture_screenshot(driver, scenario.name)
            except Exception:
                pass

    if driver is not None:
        context.evidence.finish_scenario(driver, scenario.status)
        trace = context.evidence.ultimo_trace
        if trace:
            _log(f"    Trace: {trace}")

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
