from behave import given, then, when

from pages.embed.embed_page import EmbedPage
from recursos.utils.config import Config


def _embed(context) -> EmbedPage:
    if not hasattr(context, "embed_page"):
        context.embed_page = EmbedPage(context.driver)
    return context.embed_page


@given("que abro o editor Tryit do W3Schools")
def abrir_tryit(context):
    _embed(context).abrir_tryit()


@when("monto o embed do documento D4Sign para visualização")
def montar_embed(context):
    page = _embed(context)
    page.montar_e_executar_embed()
    context.ids_canvas_embed = page.ids_canvas_encontrados()


@then("a viewblob deve ser exibida no iframe do embed")
def validar_viewblob_embed(context):
    page = _embed(context)
    assert page.viewblob_esta_visivel(), (
        "A viewblob do embed D4Sign não apareceu no iframe do Tryit. "
        f"URL atual: {context.driver.current_url}"
    )


@then("o documento deve ter {quantidade:d} anexos visíveis pelos canvas")
def validar_anexos_canvas(context, quantidade):
    page = _embed(context)
    encontrados = page.contar_anexos_por_canvas()
    ids = page.ids_canvas_encontrados()
    context.quantidade_anexos_embed = encontrados
    context.ids_canvas_embed = ids
    esperado = quantidade or Config.EMBED_ANEXOS_ESPERADOS
    print(f"Canvas no embed: {ids} | anexos (canvas além do principal): {encontrados}")
    assert encontrados == esperado, (
        "Quantidade de anexos no embed diferente do esperado. "
        f"Esperado: {esperado}. Encontrado: {encontrados}. "
        f"Canvas: {ids}."
    )
