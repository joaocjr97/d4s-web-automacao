from behave import then, when

from pages.cofres.cofre_page import CofrePage


def _cofre(context) -> CofrePage:
    if not hasattr(context, "cofre_page"):
        context.cofre_page = CofrePage(context.driver)
    return context.cofre_page


def _contagens(context) -> list:
    if not hasattr(context, "contagens"):
        context.contagens = []
    return context.contagens


def _registrar_contagem(context, tipo: str, nome: str, quantidade: int) -> None:
    _contagens(context).append(
        {"tipo": tipo, "nome": nome, "quantidade": quantidade}
    )


@when('pesquiso o cofre "{nome}"')
def pesquisar_cofre(context, nome):
    page = _cofre(context)
    page.pesquisar_cofre(nome)
    context.nome_cofre = nome


@when('abro o cofre "{nome}"')
def abrir_cofre(context, nome):
    page = _cofre(context)
    page.abrir_cofre_pesquisado(nome)
    context.nome_cofre = nome
    quantidade = page.contar_documentos()
    context.quantidade_documentos = quantidade
    _registrar_contagem(context, "cofre", nome, quantidade)


@when('pesquiso e abro o cofre "{nome}"')
def pesquisar_e_abrir_cofre(context, nome):
    pesquisar_cofre(context, nome)
    abrir_cofre(context, nome)


@then("o cofre deve estar aberto")
def validar_cofre_aberto(context):
    assert _cofre(context).cofre_esta_aberto(), (
        "O cofre não foi aberto. "
        f"URL atual: {context.driver.current_url}"
    )


@then("a quantidade de documentos deve ser maior que 0")
def validar_quantidade_documentos(context):
    quantidade = getattr(context, "quantidade_documentos", None)
    if quantidade is None:
        quantidade = _cofre(context).contar_documentos()
        context.quantidade_documentos = quantidade
    assert quantidade > 0, (
        "O cofre foi aberto, mas nenhum documento foi encontrado. "
        f"Quantidade: {quantidade}."
    )
    print(f"Documentos no cofre {getattr(context, 'nome_cofre', '')!r}: {quantidade}")


@when('pesquiso a pasta "{nome}"')
def pesquisar_pasta(context, nome):
    page = _cofre(context)
    page.pesquisar_pasta(nome)
    context.nome_pasta = nome


@when('abro a pasta "{nome}"')
def abrir_pasta(context, nome):
    page = _cofre(context)
    page.abrir_pasta(nome)
    context.nome_pasta = nome
    quantidade = page.contar_documentos()
    context.quantidade_documentos_pasta = quantidade
    _registrar_contagem(context, "pasta", nome, quantidade)


@when('pesquiso e abro a pasta "{nome}"')
def pesquisar_e_abrir_pasta(context, nome):
    pesquisar_pasta(context, nome)
    abrir_pasta(context, nome)


@when('abro a pasta "{nome}" sem pesquisar')
def abrir_pasta_sem_pesquisar(context, nome):
    page = _cofre(context)
    page.abrir_pasta_sem_pesquisa(nome)
    context.nome_pasta = nome
    quantidade = page.contar_documentos()
    context.quantidade_documentos_pasta = quantidade
    _registrar_contagem(context, "pasta", nome, quantidade)


@then("a pasta deve estar aberta")
def validar_pasta_aberta(context):
    nome = getattr(context, "nome_pasta", None)
    assert _cofre(context).pasta_esta_aberta(nome), (
        "A pasta não foi aberta. "
        f"Pasta: {nome!r} | URL atual: {context.driver.current_url}"
    )


@then("a quantidade de documentos da pasta deve ser contabilizada")
def validar_quantidade_documentos_pasta(context):
    quantidade = getattr(context, "quantidade_documentos_pasta", None)
    if quantidade is None:
        quantidade = _cofre(context).contar_documentos()
        context.quantidade_documentos_pasta = quantidade
    assert quantidade >= 0, (
        "Não foi possível contar os documentos da pasta. "
        f"Quantidade: {quantidade}."
    )
    print(f"Documentos na pasta {getattr(context, 'nome_pasta', '')!r}: {quantidade}")


@then("a quantidade de documentos da pasta deve ser maior que 0")
def validar_quantidade_documentos_pasta_positiva(context):
    quantidade = getattr(context, "quantidade_documentos_pasta", None)
    if quantidade is None:
        quantidade = _cofre(context).contar_documentos()
        context.quantidade_documentos_pasta = quantidade
    assert quantidade > 0, (
        "A pasta foi aberta, mas nenhum documento foi encontrado. "
        f"Pasta: {getattr(context, 'nome_pasta', '')!r} | Quantidade: {quantidade}."
    )
    print(f"Documentos na pasta {getattr(context, 'nome_pasta', '')!r}: {quantidade}")


@then("a quantidade de documentos deve ser apresentada por nome")
def apresentar_ultima_contagem_por_nome(context):
    itens = getattr(context, "contagens", [])
    assert itens, "Nenhuma contagem foi registrada neste cenário."
    item = itens[-1]
    nome = item["nome"]
    quantidade = item["quantidade"]
    tipo = item["tipo"]
    assert quantidade > 0, (
        f"O {tipo} {nome!r} foi aberto, mas nenhum documento foi encontrado. "
        f"Quantidade: {quantidade}."
    )
    print(f"- {nome}: {quantidade}")
