from behave import given

from pages.login.login_page import LoginPage


@given("que estou logado na plataforma D4Sign")
def usuario_logado(context):
    context.login_page = LoginPage(context.driver)
    if context.login_page.ja_esta_logado():
        return
    context.login_page.fazer_login()
