from behave import given, then, when

from pages.envios import envio_locators as L
from pages.login.login_page import LoginPage
from pages.envios.envio_page import EnvioPage
from recursos.utils.config import Config


def _envio(context) -> EnvioPage:
    if not hasattr(context, "envio_page"):
        context.envio_page = EnvioPage(context.driver)
    return context.envio_page


def _salvar_url_documento(context, url: str) -> None:
    context.documento_url = url
    context.driver.documento_url = url


@given("que o documento da desk está pronto para assinatura")
def documento_pronto_para_assinatura(context):
    url = (
        getattr(context, "documento_url", None)
        or getattr(context.driver, "documento_url", None)
    )
    if url:
        _envio(context)._garantir_pagina_documento(url)
        return

    LoginPage(context.driver, timeout=Config.LOGIN_TIMEOUT).fazer_login()
    _salvar_url_documento(context, _envio(context).enviar_documento_pela_desk())


@given("que enviei um documento pela desk")
def documento_enviado_desk(context):
    url = (
        getattr(context, "documento_url", None)
        or getattr(context.driver, "documento_url", None)
    )
    if url:
        _envio(context)._garantir_pagina_documento(url)
        return
    _salvar_url_documento(context, _envio(context).enviar_documento_pela_desk())


@given("que o template HTML foi preenchido e salvo")
def template_preenchido(context):
    url = (
        getattr(context, "documento_url", None)
        or getattr(context.driver, "documento_url", None)
    )
    if url and "viewblob" in url:
        _envio(context)._garantir_pagina_documento(url)
        return
    _salvar_url_documento(context, _envio(context).preencher_template_html())


@given("que o documento do template HTML foi enviado para assinatura")
def template_enviado(context):
    page = _envio(context)
    url = (
        getattr(context, "documento_url", None)
        or getattr(context.driver, "documento_url", None)
    )
    if url and "viewblob" in url:
        page._garantir_pagina_documento(url)
        if page.is_present(L.ASSINAR, timeout=10):
            return
    if url and "viewblob" in url and page.is_present(L.VERIFICA_ENVIO, timeout=5):
        _salvar_url_documento(context, page.enviar_template_html())
        return
    _salvar_url_documento(context, page.preencher_template_html())
    _salvar_url_documento(context, page.enviar_template_html())


@given("que enviei documento com anexo no cofre")
def documento_com_anexo(context):
    url = (
        getattr(context, "documento_url", None)
        or getattr(context.driver, "documento_url", None)
    )
    if url and "viewblob" in url:
        _envio(context)._garantir_pagina_documento(url)
        return
    _salvar_url_documento(
        context, _envio(context).enviar_documento_e_validar_canvas()
    )

@when("envio um documento pela desk para assinatura")
def enviar_pela_desk(context):
    _salvar_url_documento(context, _envio(context).enviar_documento_pela_desk())


@then("o documento deve estar aguardando signatários")
def validar_aguardando_signatarios(context):
    _envio(context).validar_aguardando_signatarios()


@when("adiciono signatário e envio o documento para assinatura")
def fluxo_assinatura(context):
    page = _envio(context)
    url_documento = (
        getattr(context, "documento_url", None)
        or getattr(context.driver, "documento_url", None)
    )
    if not url_documento:
        raise AssertionError(
            "URL do documento não encontrada. "
            f"Página atual: {context.driver.current_url}"
        )
    page.incluir_signatario_por_email(url_documento=url_documento)
    page.enviar_para_assinatura()


@when("realizo a assinatura do documento")
def assinar_documento(context):
    _envio(context).assinar_documento()


@then("a assinatura deve ser verificada com sucesso")
def validar_assinatura(context):
    _envio(context).validar_assinatura_concluida()


# --- Cofre ---

@when("envio um documento pelo cofre")
def enviar_pelo_cofre(context):
    _envio(context).enviar_documento_pelo_cofre()


# --- Grupo ---

@when("envio o documento para grupo de assinatura")
def enviar_grupo(context):
    _envio(context).enviar_para_grupo_assinatura()


@then("o documento deve estar na fase enviado")
def validar_fase_enviado(context):
    _envio(context).validar_fase_enviado()


# --- Template HTML ---

@when("preencho e salvo um template HTML no cofre")
def preencher_template(context):
    _salvar_url_documento(context, _envio(context).preencher_template_html())


@then("o template HTML deve estar pronto para envio")
def validar_template_pronto(context):
    assert _envio(context).is_present(L.VERIFICA_ENVIO)


@when("envio o documento do template HTML para assinatura")
def enviar_template(context):
    _salvar_url_documento(context, _envio(context).enviar_template_html())


@when("assino o documento do template HTML")
def assinar_template(context):
    page = _envio(context)
    url = (
        getattr(context, "documento_url", None)
        or getattr(context.driver, "documento_url", None)
    )
    if url:
        page._garantir_pagina_documento(url)
    page.assinar_template_html()


@then("o template HTML deve estar assinado")
def validar_template_assinado(context):
    assert _envio(context).is_present(L.VERIFICA_ASSINATURA)


# --- Lote ---

@when("preparo e envio um lote com planilha Excel")
def enviar_lote(context):
    _envio(context).enviar_lote()


@then("o lote deve ser processado com sucesso")
def validar_lote(context):
    _envio(context).validar_lote_processado()


@when("preparo e envio um PowerForm")
def preparar_powerform(context):
    _envio(context).preparar_powerform()


@then("o PowerForm deve ser enviado com sucesso")
def validar_powerform(context):
    assert not _envio(context).is_present(L.BTN_SALVAR_POWER)


# --- Pin ---

@when("envio documento com anexo e valido os canvas")
def enviar_com_anexo(context):
    _salvar_url_documento(
        context, _envio(context).enviar_documento_e_validar_canvas()
    )


@when("adiciono pin replicado e removo de todas as páginas")
def fluxo_pin(context):
    _envio(context).adicionar_e_validar_pins()


@then("os pins devem estar removidos de todas as páginas")
def validar_pins_removidos(context):
    page = _envio(context)
    for pin in (L.PIN_1, L.PIN_2, L.PIN_3, L.PIN_4):
        assert not page.is_present(pin)


# --- Canvas pins ---

@when("envio documento pelo cofre e adiciono pin no canvas")
def enviar_canvas_pin(context):
    _envio(context).enviar_e_adicionar_pin_no_canvas()


@then("o pin deve estar visível no canvas")
def validar_pin_canvas(context):
    assert _envio(context).is_present(L.PIN_1)
