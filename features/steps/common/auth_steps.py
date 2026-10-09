from behave import given

from pages.login.login_page import LoginPage
from recursos.utils.config import Config


@given("que estou logado na plataforma D4Sign")
def usuario_logado(context):
    context.login_page = LoginPage(context.driver, timeout=Config.LOGIN_TIMEOUT)

    # Sessão pode já ter vindo pronta (storage_state cacheado de um login
    # anterior nesta execução) — navega pra desk e confirma antes de decidir
    # se precisa mesmo refazer o login completo via UI.
    context.login_page.open(Config.desk_url())
    if context.login_page.ja_esta_logado():
        print("    OK Sessao reaproveitada do cache (login NAO foi refeito)", flush=True)
        return

    print("    Login completo via UI (cache vazio ou sessao expirada)", flush=True)
    context.login_page.fazer_login()
    try:
        Config.salvar_estado_login(context.driver.get_storage_state())
    except Exception:
        pass
