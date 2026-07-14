import os
import sys

# Evita a criação de pastas __pycache__ ao rodar a suíte.
sys.dont_write_bytecode = True

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from recursos.utils.config import Config
from recursos.utils.driver_factory import create_driver
from recursos.utils.evidence import Evidence

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
    driver = context.driver
    try:
        driver.delete_all_cookies()
    except Exception:
        pass
    try:
        driver.execute_script(
            "window.localStorage.clear(); window.sessionStorage.clear();"
        )
    except Exception:
        pass


def _ci_log(message: str) -> None:
    if os.getenv("CI", "").lower() in ("1", "true", "yes"):
        print(message.encode("ascii", errors="replace").decode("ascii"), flush=True)


def before_all(context):
    Config.load()
    context.config_obj = Config
    context.evidence = Evidence()


def before_feature(context, feature):
    _ci_log(f">> Feature: {feature.name}")
    context._reusar_navegador = _feature_reusa_navegador(feature)
    context._manter_sessao = _feature_mantem_sessao(feature)
    context._signature_driver = None


def before_scenario(context, scenario):
    _ci_log(f"  >> Cenario: {scenario.name}")
    manter_sessao = getattr(context, "_manter_sessao", False)
    driver_salvo = getattr(context, "_signature_driver", None)

    if manter_sessao and driver_salvo is not None:
        context.driver = driver_salvo
    elif getattr(context, "driver", None) is None:
        _ci_log("    ... Abrindo navegador Chrome")
        context.driver = create_driver(Config)
        _ci_log("    OK Navegador pronto")

    if manter_sessao:
        context._signature_driver = context.driver

    for attr in ("envio_page", "login_page"):
        if hasattr(context, attr):
            delattr(context, attr)

    context.evidence.start_scenario(scenario.name, context.driver)


def after_step(context, step):
    if Config.RECORD_VIDEO:
        try:
            context.evidence.capture_frame(context.driver)
        except Exception:
            pass
    if step.status == "failed" and Config.SCREENSHOT_ON_FAIL:
        context.evidence.capture_screenshot(context.driver, step.name)


def after_scenario(context, scenario):
    _ci_log(f"  OK Cenario finalizado: {scenario.name} ({scenario.status})")
    if scenario.status == "failed":
        try:
            _ci_log(f"    URL: {context.driver.current_url}")
        except Exception:
            pass
    if scenario.status == "failed" and Config.SCREENSHOT_ON_FAIL:
        context.evidence.capture_screenshot(context.driver, scenario.name)

    context.evidence.finish_scenario(context.driver, scenario.status)

    if getattr(context, "_manter_sessao", False):
        context._signature_driver = context.driver
        return

    if getattr(context, "_reusar_navegador", False):
        return

    if getattr(context, "driver", None):
        context.driver.quit()
        context.driver = None


def after_feature(context, feature):
    driver = getattr(context, "_signature_driver", None) or getattr(context, "driver", None)
    if getattr(context, "_reusar_navegador", False) and driver:
        driver.quit()
    context.driver = None
    context._signature_driver = None
