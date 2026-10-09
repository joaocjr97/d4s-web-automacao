"""Locators da consulta de cofre e documentos (seletores Playwright)."""

CAMPO_BUSCA_COFRE = "#q3"
LISTA_COFRES = "#meus_cofres"
CARREGAR_MAIS_COFRES = (
    "xpath=//*[self::a or self::button][contains(normalize-space(.), 'Carregar mais cofres')]"
)
NOME_COFRE = ".nome_cofre"
# Mesmo cofre dos fluxos de envio, usado quando o nome "12" se repete na lista.
COFRE_AUTOMACAO = "#liCofre_1414985 a[href*='/desk/cofres/']"
# Cofre compartilhado de automação.
COFRE_AUTOMACAO_COMPARTILHADO = (
    "xpath=//li[starts-with(@id,'liCofre_')]"
    "[.//span[@class='nome_cofre']"
    "[normalize-space()='Automação compartilhado - conta de automação']]"
    "//a[contains(@href,'/desk/cofres/')]"
)
LINK_COFRE_AUTOMACAO_COMPARTILHADO = (
    'role=link[name="Automação compartilhado - conta de automação"]'
)
MODAL_BACKDROP = ".modal-backdrop"
MODAL_ABERTO = ".modal.in, .modal.show, .modal[style*='display: block']"
BTN_FECHAR_POPUP_COFRE = (
    "#modal-aviso-analizer .close, "
    ".modal.in button.close, .modal.show button.close, "
    ".modal.in [data-dismiss='modal'], .modal.show [data-dismiss='modal'], "
    ".sweet-alert button.confirm, .swal2-container .swal2-confirm"
)
BTN_CONFIRMAR_POPUP_COFRE = (
    "xpath=//div[contains(@class,'modal') or contains(@class,'sweet-alert') "
    "or contains(@class,'swal2-popup') or contains(@class,'popover')]"
    "//*[self::button or self::a]["
    "contains(normalize-space(.), 'Entendi') "
    "or contains(normalize-space(.), 'Continuar') "
    "or contains(normalize-space(.), 'Aceitar') "
    "or contains(normalize-space(.), 'Prosseguir') "
    "or contains(normalize-space(.), 'Fechar') "
    "or contains(normalize-space(.), 'Got it') "
    "or normalize-space(.)='OK' or normalize-space(.)='Ok'"
    "]"
)
TABELA_DOCUMENTOS = "#contratos"
LINHAS_DOCUMENTO = "#contratos tbody tr"
LINHA_VAZIA = "#contratos tbody td.dataTables_empty"
OPCOES_COFRE = "#label-opcao-cofre"
CONTADOR_TOTAL = (
    "xpath=//div[contains(@class,'ibox')]//span["
    "contains(@data-original-title,'Total de documentos') "
    "or contains(@title,'Total de documentos') "
    "or contains(@data-original-title,'Total document') "
    "or contains(@title,'Total document')"
    "]/b"
)
INFO_DATATABLES = "#contratos_info, .dataTables_info"
NOME_PASTA = ".nome_pasta"
# Pasta criada no cofre de automação, quando o nome "pasta" se repete.
PASTA_AUTOMACAO = "#liFolder_1397734 a[href*='/desk/cofres/']"
# Pasta visível no cofre compartilhado (codegen: get_by_role link "Pasta de Automação").
PASTA_DE_AUTOMACAO = (
    "xpath=//li[starts-with(@id,'liFolder_')]"
    "[.//span[@class='nome_pasta'][normalize-space()='Pasta de Automação']]"
    "//a[contains(@href,'/desk/cofres/')]"
)
LINK_PASTA_DE_AUTOMACAO = 'role=link[name="Pasta de Automação"]'
CHEVRON_PASTAS = "xpath=//i[contains(@onclick,'accordion_pastas')]"
BTN_NOVA_PASTA = (
    "xpath=//*[self::a or self::button or self::span]"
    "[contains(normalize-space(.), 'Nova pasta') "
    "or contains(normalize-space(.), 'New folder')]"
)


def link_cofre_por_nome(nome: str) -> str:
    """Link de abertura do cofre (não a estrela de favorito)."""
    if '"' in nome and "'" in nome:
        partes = nome.replace('"', '", \'"\', "')
        valor = f'concat("{partes}")'
        return (
            "xpath=//li[starts-with(@id,'liCofre_')]"
            f"[.//span[@class='nome_cofre'][normalize-space()={valor}]]"
            "//a[contains(@href,'/desk/cofres/')]"
        )
    if "'" in nome:
        return (
            'xpath=//li[starts-with(@id,"liCofre_")]'
            f'[.//span[@class="nome_cofre"][normalize-space()="{nome}"]]'
            '//a[contains(@href,"/desk/cofres/")]'
        )
    return (
        "xpath=//li[starts-with(@id,'liCofre_')]"
        f"[.//span[@class='nome_cofre'][normalize-space()='{nome}']]"
        "//a[contains(@href,'/desk/cofres/')]"
    )


def link_cofre_contendo_nome(nome: str) -> str:
    """Link do cofre cujo nome contém o termo (cofre compartilhado, etc.)."""
    valor = _xpath_equals(nome)
    return (
        "xpath=//li[starts-with(@id,'liCofre_')]"
        f"[.//span[@class='nome_cofre'][contains(normalize-space(), {valor})]]"
        "//a[contains(@href,'/desk/cofres/')]"
    )


def _xpath_equals(nome: str) -> str:
    if '"' in nome and "'" in nome:
        partes = nome.replace('"', '", \'"\', "')
        return f'concat("{partes}")'
    if "'" in nome:
        return f'"{nome}"'
    return f"'{nome}'"


def link_pasta_por_nome(nome: str) -> str:
    """Link de abertura da pasta (não a estrela de favorito)."""
    valor = _xpath_equals(nome)
    return (
        "xpath=//li[starts-with(@id,'liFolder_')]"
        f"[.//span[@class='nome_pasta'][normalize-space()={valor}]]"
        "//a[contains(@href,'/desk/cofres/')]"
    )
