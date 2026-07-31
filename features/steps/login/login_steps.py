from behave import given, then, when

from pages.login.login_page import LoginPage
from recursos.utils.config import Config


def _criar_login_page(context) -> LoginPage:
    return LoginPage(context.driver, timeout=Config.LOGIN_TIMEOUT)


@given("que acesso a página de login da D4Sign")
def acessar_pagina_login(context):
    context.login_page = _criar_login_page(context)
    context.login_page.abrir_pagina_login()
    context.login_page.configurar_cookies_iniciais()


@when("realizo login com credenciais válidas")
def realizar_login(context):
    context.login_page.preencher_credenciais_e_entrar()


@when("realizo login com senha incorreta")
def login_senha_incorreta(context):
    context.login_page.tentar_login(
        username=Config.USERNAME,
        password=LoginPage.SENHA_INCORRETA,
    )


@when("realizo login com usuário inexistente")
def login_usuario_inexistente(context):
    context.login_page.tentar_login(
        username=LoginPage.EMAIL_INEXISTENTE,
        password=LoginPage.SENHA_INCORRETA,
    )


@when('realizo login com e-mail "{email}" e senha "{senha}"')
def login_com_email_e_senha(context, email, senha):
    context.login_page.tentar_login(username=email, password=senha)


@when('realizo login apenas com senha "{senha}"')
def login_apenas_senha(context, senha):
    context.login_page.tentar_login(
        password=senha,
        preencher_email=False,
        preencher_senha=True,
    )


@when("realizo login apenas com e-mail válido")
def login_apenas_email(context):
    context.login_page.tentar_login(
        username=Config.USERNAME,
        preencher_email=True,
        preencher_senha=False,
    )


@when("clico em entrar sem preencher os campos")
def clicar_entrar_sem_credenciais(context):
    context.login_page.preparar_formulario_login()
    context.login_page.clicar_entrar()


@then("devo ver o painel principal da plataforma")
def validar_painel_principal(context):
    assert context.login_page.usuario_esta_logado(), (
        "Logo da D4Sign não foi exibido após o login."
    )


@then('devo ver a mensagem de erro "{mensagem}"')
def validar_mensagem_erro(context, mensagem):
    # Valida pela mensagem real da UI (EN no CI; PT local).
    erro = context.login_page.obter_mensagem_erro_login()
    assert context.login_page.mensagem_erro_login_valida(mensagem), (
        f"Mensagem de erro esperada (PT/EN): {mensagem!r} "
        f"ou 'Invalid email or password.'. Obtida: {erro!r}."
    )


@then("não devo estar autenticado na plataforma")
def validar_nao_autenticado(context):
    assert not context.login_page.usuario_esta_logado(), (
        "Usuário foi autenticado indevidamente."
    )


@then("o campo e-mail deve exibir validação de formato inválido")
def validar_email_formato_invalido(context):
    assert context.login_page.campo_exibe_validacao_email_invalido(), (
        "Validação nativa de e-mail inválido não foi exibida."
    )


@then("o campo e-mail deve exibir validação de preenchimento obrigatório")
def validar_email_obrigatorio(context):
    assert context.login_page.campo_exibe_validacao_obrigatoria(
        context.login_page.EMAIL
    ), "Validação de e-mail obrigatório não foi exibida."


@then("o campo senha deve exibir validação de preenchimento obrigatório")
def validar_senha_obrigatoria(context):
    assert context.login_page.campo_exibe_validacao_obrigatoria(
        context.login_page.PASSWORD
    ), "Validação de senha obrigatória não foi exibida."
