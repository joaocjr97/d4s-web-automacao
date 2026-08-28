"""Locators dos fluxos de envio da plataforma D4Sign (seletores Playwright)."""

# Desk / upload comum
BOTAO_ENVIO = 'xpath=//*[@id="drop-zone"]/a/p[2]'
# Escopo no form de upload: há outros select[name=uuid-cofre] ocultos na desk.
SELECT_COFRE = "#formUpload select[name='uuid-cofre'], .modal.in select[name='uuid-cofre']"
# Preferir input do modal aberto (há #fileupload ocultos na desk).
FILE_UPLOAD = (
    ".modal.in #fileupload, .modal.in #formUpload #fileupload, "
    "#formUpload #fileupload, #fileupload"
)
FILE_UPLOAD_MODAL = (
    "xpath=//div[contains(@class,'modal') and contains(@class,'in')]"
    "//input[@id='fileupload' or @type='file']"
)
AGUARDANDO_SIGNATARIOS = (
    'xpath=//*[@id="page-wrapper"]//span['
    'contains(translate(., "aguardno", "AGUARDNO"), "AGUARDANDO") and '
    'contains(translate(., "signatriosá", "SIGNATRIOSÁ"), "SIGNAT")'
    ']'
)

# Cofre
# O antigo id fixo (liCofre_1414985, rótulo "12") ficou órfão na conta de
# testes — clicar nele nunca revela "Novo documento". Uso um cofre por nome
# em vez de id: "Berry-Moses" é único na lista e confirmadamente funcional.
COFRE_TESTE = "xpath=//a[normalize-space(.)='Berry-Moses']"
NOVO_ARQUIVO = "#label-new-file"
BTN_NOVO_DOC = "#btnNovoDoc"
# Alterna o modal de envio para o modo de arquivos grandes (acima do limite
# padrão de upload). Precisa ser clicado antes do #fileupload.
LINK_ARQUIVO_GRANDE = "#master_envios_geral > small:nth-child(7) > a"
LINK_ARQUIVO_GRANDE_TEXTO = (
    "xpath=//a[contains(normalize-space(.), 'Limite de 20MB') "
    "or contains(normalize-space(.), '20MB limit') "
    "or contains(normalize-space(.), '20 MB')]"
)
# 1º item do dropdown "Novo documento" (Documento para assinatura).
NEW_FILE = (
    'xpath=//*[@id="btnNovoDoc"]/parent::*//ul[contains(@class,"dropdown-menu")]'
    '//a[contains(@href, "enviarDocumento") or contains(@onclick, "enviarDocumento")]'
)

# Assinatura / envio
INCLUIR_EMAIL = "xpath=//a[contains(normalize-space(.), 'Incluir meu')]"
INCLUIR_EMAIL_LEGADO = (
    'xpath=//*[@id="page-wrapper"]/div[2]/div/div[1]/div/div/div/div[4]/div/div[2]/div[1]/span[1]/a'
)
CAMPO_EMAIL_SIGNATARIO = "#email-assinatura"
BTN_ADICIONAR_SIGNATARIO = (
    "xpath=//input[@id='email-assinatura']/ancestor::div[contains(@class,'input-group')]"
    "//button[contains(normalize-space(.), 'Adicionar')]"
)
BTN_ADICIONAR_SIGNATARIO_ALT = (
    "xpath=//*[@id='email-assinatura']/ancestor::div[contains(@class,'input-group')]"
    "//*[self::button or self::a or self::span][contains(normalize-space(.), 'Adicionar')]"
)
LISTA_ASSINATURA_ROW = "#lista-assinatura tbody tr"
BOTAO_ASSINATURA = 'xpath=//*[@id="enviar-para-assinatura"]'
BOTAO_ENVIO_2 = "#btnSalvarDocumento"
FASE_ENVIADO = (
    'xpath=//*[@id="page-wrapper"]//span['
    'contains(translate(., "ASSINATURAS", "assinaturas"), "ASSINATURAS") '
    'or contains(translate(., "ENVIADO", "enviado"), "ENVIADO")'
    ']'
)
ASSINAR = "#adicionar-assinatura"
SENHA_CONTA = "#senhaConta"
SALVAR_ASSINATURA = 'xpath=//*[@id="btnSalvarAssinatura"]'
VERIFICA_ASSINATURA = 'xpath=//*[@id="viewblobdiv"]/div[2]/div[1]'
VIEWBLOB = "#viewblobdiv"
ASSINATURA_CONCLUIDA = (
    "xpath=//*[@id='lista-assinatura']//*[contains(translate(., 'ASSINOU', 'assinou'), 'assinou')]"
)

# Grupo de assinatura (viewblob — não confundir com menu /desk/grupoassinatura)
# UI pode estar em PT ("Grupo") ou EN ("Group") no CI.
GRUPO = (
    "xpath=//*[@id='page-wrapper']/div[2]//a["
    "(contains(normalize-space(.), 'Grupo') or contains(normalize-space(.), 'Group')) "
    "and not(contains(@href, 'grupoassinatura'))"
    "]"
)
GRUPO_LEGADO = (
    'xpath=//*[@id="page-wrapper"]/div[2]/div/div[1]/div/div/div/div[4]/div/div[2]/div[1]/span[3]/a'
)
FILTRO_GRUPO = "#filtro-grupos"
SELECIONAR_GRUPO = (
    "xpath=//*[@id='tabela-grupos']//tr[contains(@class,'grupo-row')]"
    "[.//b[contains(translate(., 'GRUPO', 'grupo'), 'grupo') "
    "or contains(translate(., 'GROUP', 'group'), 'group')]]"
    "//a[contains(normalize-space(.), 'Adicionar') or contains(normalize-space(.), 'Add')]"
)
SELECIONAR_GRUPO_LEGADO = 'xpath=//*[@id="tabela-grupos"]/tbody/tr[29]/td[2]/a'

# Template HTML
TEMPLATE_HTML = (
    'xpath=//*[@id="page-wrapper"]/div[2]/div[2]/div[2]/div/div[1]/div[2]/ul/li[4]/a'
)
CAMPO_MARCA = "#keyt_marca"
CAMPO_LARANJA = "#keyt_laranja"
CAMPO_COR = "#keyt_cor"
CAMPO_TRUE_FALSE = "#keyt_trueFALSE"
CAMPO_RUA = "#keyt_rua"
CAMPO_LUGARES = "#keyt_lugares"
CAMPO_RESTAURANT = "#keyt_restaurant"
SALVAR_TEMPLATE = "#btnSaveTemplate"
VERIFICA_ENVIO = CAMPO_EMAIL_SIGNATARIO

# Envio em lote
LOTE = 'xpath=//*[@id="page-wrapper"]/div[2]/div[1]/div[5]/a'
BTN_LOTE = "#btnSaveTemplate"
CAMPO_COFRE_LOTE = "#uuid-cofre"
NOME_ENVIO = 'xpath=//*[@id="div_up"]/input'
TIPO_DOC = 'xpath=//*[@id="div_up"]/select[4]'
BTN_SALVAR_PF = "#btnSavePf"
BTN_OPCAO = "#label-opcao-cofre"
SELECIONAR_DOC = (
    'xpath=//*[@id="contratos"]/tbody/tr[1]//ul[contains(@class,"dropdown-menu")]//a['
    'contains(translate(normalize-space(.), "SELECIONAR", "selecionar"), "selecionar") '
    'or contains(translate(normalize-space(.), "SELECT", "select"), "select") '
    'or contains(translate(normalize-space(.), "IMPORTAR", "importar"), "importar") '
    'or contains(translate(normalize-space(.), "UPLOAD", "upload"), "upload")'
    ']'
)
SELECIONAR_DOC_LEGADO = 'xpath=//*[@id="contratos"]/tbody/tr[1]/td[6]/div/ul/li[4]/a'
SUCESSO = 'xpath=//*[@id="sucesso"]/h4'
PROCESSAMENTO = (
    'xpath=//*[@id="contratos"]/tbody/tr[1]//ul[contains(@class,"dropdown-menu")]//a['
    'contains(translate(normalize-space(.), "PROCESSAR", "processar"), "processar") '
    'or contains(translate(normalize-space(.), "PROCESSING", "processing"), "process")'
    ']'
)
PROCESSAMENTO_LEGADO = (
    'xpath=//*[@id="contratos"]/tbody/tr[1]/td[6]/div/ul/li[8]/a'
)
CAMPO_SENHA_LOTE = ".modal.in #senhaConta, #senhaConta"
BTN_FIM = "#btnSalvarDocumento"
TAG_PROCESSANDO = (
    "xpath=//small[contains(text(), 'SUBMITTED FOR PROCESSING')"
    " or contains(translate(., 'PROCESSAMENTO', 'processamento'), 'PROCESSAMENTO')"
    " or contains(translate(., 'PROCESSANDO', 'processando'), 'PROCESSANDO')]"
)
TAG_PROCESSADO = (
    "xpath=//small[contains(text(), 'PROCESSED')"
    " or contains(translate(., 'PROCESSADO', 'processado'), 'PROCESSADO')]"
)

# PowerForm
CLM = 'xpath=//*[@id="page-wrapper"]/div[2]/div[1]/div[3]/div/a'
POWERFORM = 'xpath=//*[@id="page-wrapper"]/div[2]/div[1]/div[3]/div/ul/li[5]/a'
CRIAR_POWERFORM = "#btnSaveTemplate"
MODAL_POWERFORM = "#formPowerForm"
CAMPO_COFRE_PF = "#uuid_cofre"
CAMPO_TEMPLATE = "#uuid-template"
NOME_DOCUMENTO = "#nome_documento"
BOTAO_CONTINUAR = "#docButton"
BOTAO_CONTINUAR_VISIVEL = "#docButton:visible"
BTN_TOKEN = 'xpath=//*[@id="tokenCount"]/button'
CAMPO_EMAIL_PF = "xpath=//*[starts-with(@id, 'email_')]"
BTN_EMAIL = "#fillerButton"
BTN_SEND = 'xpath=//*[@id="pfv2-result"]/button'
BTN_SALVAR_POWER = "#btnSalvarPower"

# Reaproveitamento de documento (PT local / EN no CI)
OPCOES_DOCUMENTO = (
    "xpath=//*[self::button or self::a]["
    "contains(normalize-space(.), 'Opções do documento') "
    "or contains(normalize-space(.), 'Document options')"
    "]"
)
MENU_REAPROVEITAR = (
    "xpath=//a["
    "contains(normalize-space(.), 'Reaproveitar') "
    "or contains(normalize-space(.), 'Reuse Document') "
    "or contains(normalize-space(.), 'Reuse document')"
    "]"
)
MODAL_REAPROVEITAMENTO = (
    "xpath=//div[contains(@class,'modal') and contains(@class,'in')]"
    "[.//*[contains(normalize-space(.), 'Reaproveitar') "
    "or contains(normalize-space(.), 'Reuse Document') "
    "or contains(normalize-space(.), 'Reuse document')]]"
)
SELECT_COFRE_REAPROVEITAMENTO = (
    "xpath=//div[contains(@class,'modal') and contains(@class,'in')]"
    "//select[@name='uuid-cofre']"
)
BTN_CONFIRMAR_REAPROVEITAMENTO = (
    "xpath=//div[contains(@class,'modal') and contains(@class,'in')]"
    "//button[normalize-space(.)='Confirmar' or normalize-space(.)='Confirm']"
)
# Casar por texto aqui é traiçoeiro: o <script> do próprio modal contém a
# frase de sucesso, então qualquer container ancestral casa antes do envio.
MSG_REAPROVEITAMENTO_SUCESSO = (
    "xpath=//div[contains(@class,'modal') and contains(@class,'in')]"
    "//div[@id='resultSuccess']"
)

# Cenários de erro (PT local / EN no CI)
ALERTA_LIMITE_UPLOAD = (
    "xpath=//*[@id='resultUp' and contains(@class,'alert-danger')] "
    "| //div[contains(@class,'modal') and contains(@class,'in')]"
    "//*[contains(@class,'alert-danger')]"
)
MODAL_ABERTO = "xpath=//div[contains(@class,'modal') and contains(@class,'in')]"
MODAL_UPLOAD_COFRE = (
    "xpath=//div[contains(@class,'modal') and contains(@class,'in')]"
    "[.//*[@id='fileupload' or @id='formUpload' or contains(., '20MB') "
    "or contains(., '20 mb') or contains(., 'Choose document') "
    "or contains(., 'Escolher documento')]]"
)
MODAL_SEM_SIGNATARIO = (
    "xpath=("
    "//div[contains(@class,'modal') and contains(@class,'in')]//*["
    "contains(translate(normalize-space(.), "
    "'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÀÃÂÉÊÍÓÔÕÚÇ', "
    "'abcdefghijklmnopqrstuvwxyzáàãâéêíóôõúç'), 'pelo menos um signat') "
    "or contains(translate(normalize-space(.), "
    "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'at least one signat') "
    "or contains(normalize-space(.), 'Add at least one') "
    "or contains(translate(normalize-space(.), "
    "'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÀÃÂÉÊÍÓÔÕÚÇ', "
    "'abcdefghijklmnopqrstuvwxyzáàãâéêíóôõúç'), 'adicione pelo menos') "
    "or contains(translate(normalize-space(.), "
    "'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÀÃÂÉÊÍÓÔÕÚÇ', "
    "'abcdefghijklmnopqrstuvwxyzáàãâéêíóôõúç'), 'nenhum signat')"
    "] | "
    "//*[contains(@class,'sweet-alert') or contains(@class,'swal2-popup') "
    "or contains(@class,'toast') or contains(@class,'alertify')]"
    "//*[contains(translate(normalize-space(.), "
    "'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÀÃÂÉÊÍÓÔÕÚÇ', "
    "'abcdefghijklmnopqrstuvwxyzáàãâéêíóôõúç'), 'pelo menos um signat') "
    "or contains(translate(normalize-space(.), "
    "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'at least one signat')]"
    ")"
)
MSG_SENHA_INVALIDA = (
    "xpath=//div[contains(@class,'modal') and contains(@class,'in')]//*["
    "contains(normalize-space(.), 'Senha inv') "
    "or contains(normalize-space(.), 'Incorrect password') "
    "or contains(normalize-space(.), 'Invalid password') "
    "or contains(normalize-space(.), 'password is invalid')"
    "]"
)

# Substituição de documento
BTN_SUBSTITUIR_DOC = "#substitute_doc"
FILE_SUBSTITUIR = "#filereupload"
MSG_SUBSTITUICAO_SUCESSO = (
    "xpath=//div[contains(@class,'modal') and contains(@class,'in')]//*["
    "(contains(translate(., 'SUBSTIUDO', 'substiudo'), 'substituído') "
    "or contains(translate(., 'SUBSTITUTED', 'substituted'), 'substituted') "
    "or contains(translate(., 'REPLACED', 'replaced'), 'replaced')) "
    "and (contains(translate(., 'SUCESO', 'suceso'), 'sucesso') "
    "or contains(translate(., 'SUCCESS', 'success'), 'success'))"
    "]"
)
NOME_DOC_SUBSTITUTO = "xpath=//*[contains(normalize-space(.), 'doc-substituto')]"

# Pin / canvas
CARREGANDO_DOCUMENTO = 'xpath=//*[@id="doc-div-principal"]/div/img'
CARREGANDO_ANEXO = 'xpath=//*[@id="progress"]/div'
ADD_ANEXO = "#id-adicionar-mais-doc"
DOCS_CARREGADOS = "#documentosCarregadosDiv"
CANVAS_1 = "#canvas1"
CANVAS_2 = "#canvas2"
CANVAS_3 = "#canvas3"
CANVAS_4 = "#canvas4"
BOTAO_ANEXO = "#id-adicionar-mais-doc, #btnNovoDoc"
PIN_1 = "#pin-container-overlay-canvas1 .pin, #pin-container-for-canvas1 div img"
PIN_2 = "#pin-container-overlay-canvas2 .pin, #pin-container-for-canvas2 div img"
PIN_3 = "#pin-container-overlay-canvas3 .pin, #pin-container-for-canvas3 div img"
PIN_4 = "#pin-container-overlay-canvas4 .pin, #pin-container-for-canvas4 div img"
BTN_REPLICAR_PIN = (
    "#pin-container-overlay-canvas1 button[data-action='replicar'], "
    "#pin-container-for-canvas1 div div:nth-child(3) button:nth-child(1)"
)
BTN_REMOVER_PIN = (
    "#pin-container-overlay-canvas1 button[data-action='remover-todos'], "
    "#pin-container-for-canvas1 div div:nth-child(3) button:nth-child(2)"
)
PIN_ELEMENTO = "#pin-container-overlay-canvas1 .pin"
BTN_TIPO_PIN = "#pin-container-overlay-canvas1 button[data-action='toggle-type-select']"
OPCAO_TIPO_PIN = "#pin-container-overlay-canvas1 .custom-select-options li"
CHECKBOX_DOC = "#input-doc-div-main"
CHECKBOX_ANEXO = "#nomeDocumento"
BTN_MODAL_PINS = "#selectAdditionals"
BTN_CONFIRMAR_REMOCAO = "xpath=//div[@class='modal-body']//button[last()]"
PROGRESS_BAR = "xpath=//div[contains(@class, 'progress-bar-striped')]"
