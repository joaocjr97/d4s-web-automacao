"""Locators dos fluxos de envio da plataforma D4Sign."""

from selenium.webdriver.common.by import By

# Desk / upload comum
BOTAO_ENVIO = (By.XPATH, '//*[@id="drop-zone"]/a/p[2]')
SELECT_COFRE = (By.NAME, "uuid-cofre")
FILE_UPLOAD = (By.ID, "fileupload")
AGUARDANDO_SIGNATARIOS = (
    By.XPATH,
    '//*[@id="page-wrapper"]//span['
    'contains(translate(., "aguardno", "AGUARDNO"), "AGUARDANDO") and '
    'contains(translate(., "signatriosá", "SIGNATRIOSÁ"), "SIGNAT")'
    ']',
)

# Cofre
COFRE_12 = (By.XPATH, '//*[@id="liCofre_1414985"]/a')
NOVO_ARQUIVO = (By.ID, "label-new-file")
NEW_FILE = (
    By.XPATH,
    '//*[@id="page-wrapper"]/div[2]/div[2]/div[2]/div/div[1]/div[2]/ul/li[1]/a',
)

# Assinatura / envio
INCLUIR_EMAIL = (By.XPATH, "//a[contains(normalize-space(.), 'Incluir meu')]")
INCLUIR_EMAIL_LEGADO = (
    By.XPATH,
    '//*[@id="page-wrapper"]/div[2]/div/div[1]/div/div/div/div[4]/div/div[2]/div[1]/span[1]/a',
)
CAMPO_EMAIL_SIGNATARIO = (By.ID, "email-assinatura")
BTN_ADICIONAR_SIGNATARIO = (
    By.XPATH,
    "//input[@id='email-assinatura']/ancestor::div[contains(@class,'input-group')]"
    "//button[contains(normalize-space(.), 'Adicionar')]",
)
BTN_ADICIONAR_SIGNATARIO_ALT = (
    By.XPATH,
    "//*[@id='email-assinatura']/ancestor::div[contains(@class,'input-group')]"
    "//*[self::button or self::a or self::span][contains(normalize-space(.), 'Adicionar')]",
)
LISTA_ASSINATURA_ROW = (By.CSS_SELECTOR, "#lista-assinatura tbody tr")
BOTAO_ASSINATURA = (By.XPATH, '//*[@id="enviar-para-assinatura"]')
BOTAO_ENVIO_2 = (By.ID, "btnSalvarDocumento")
FASE_ENVIADO = (
    By.XPATH,
    '//*[@id="page-wrapper"]//span['
    'contains(translate(., "ASSINATURAS", "assinaturas"), "ASSINATURAS") '
    'or contains(translate(., "ENVIADO", "enviado"), "ENVIADO")'
    ']',
)
ASSINAR = (By.ID, "adicionar-assinatura")
SENHA_CONTA = (By.ID, "senhaConta")
SALVAR_ASSINATURA = (By.XPATH, '//*[@id="btnSalvarAssinatura"]')
VERIFICA_ASSINATURA = (By.XPATH, '//*[@id="viewblobdiv"]/div[2]/div[1]')
VIEWBLOB = (By.ID, "viewblobdiv")
ASSINATURA_CONCLUIDA = (
    By.XPATH,
    "//*[@id='lista-assinatura']//*[contains(translate(., 'ASSINOU', 'assinou'), 'assinou')]",
)

# Grupo de assinatura (viewblob — não confundir com menu /desk/grupoassinatura)
GRUPO = (
    By.XPATH,
    "//*[@id='page-wrapper']/div[2]//a["
    "contains(translate(normalize-space(.), 'GRUPO', 'grupo'), 'grupo') "
    "and not(contains(@href, 'grupoassinatura'))"
    "]",
)
GRUPO_LEGADO = (
    By.XPATH,
    '//*[@id="page-wrapper"]/div[2]/div/div[1]/div/div/div/div[4]/div/div[2]/div[1]/span[3]/a',
)
FILTRO_GRUPO = (By.ID, "filtro-grupos")
SELECIONAR_GRUPO = (
    By.XPATH,
    "//*[@id='tabela-grupos']//tr[contains(@class,'grupo-row')]"
    "[.//b[contains(translate(., 'GRUPO', 'grupo'), 'grupo')]]"
    "//a[contains(normalize-space(.), 'Adicionar')]",
)
SELECIONAR_GRUPO_LEGADO = (
    By.XPATH,
    '//*[@id="tabela-grupos"]/tbody/tr[29]/td[2]/a',
)

# Template HTML
TEMPLATE_HTML = (
    By.XPATH,
    '//*[@id="page-wrapper"]/div[2]/div[2]/div[2]/div/div[1]/div[2]/ul/li[4]/a',
)
CAMPO_MARCA = (By.ID, "keyt_marca")
CAMPO_LARANJA = (By.ID, "keyt_laranja")
CAMPO_COR = (By.ID, "keyt_cor")
CAMPO_TRUE_FALSE = (By.ID, "keyt_trueFALSE")
CAMPO_RUA = (By.ID, "keyt_rua")
CAMPO_LUGARES = (By.ID, "keyt_lugares")
CAMPO_RESTAURANT = (By.ID, "keyt_restaurant")
SALVAR_TEMPLATE = (By.ID, "btnSaveTemplate")
VERIFICA_ENVIO = CAMPO_EMAIL_SIGNATARIO

# Envio em lote
LOTE = (By.XPATH, '//*[@id="page-wrapper"]/div[2]/div[1]/div[5]/a')
BTN_LOTE = (By.ID, "btnSaveTemplate")
CAMPO_COFRE_LOTE = (By.ID, "uuid-cofre")
NOME_ENVIO = (By.XPATH, '//*[@id="div_up"]/input')
TIPO_DOC = (By.XPATH, '//*[@id="div_up"]/select[4]')
BTN_SALVAR_PF = (By.ID, "btnSavePf")
BTN_OPCAO = (By.ID, "label-opcao-cofre")
SELECIONAR_DOC = (By.XPATH, '//*[@id="contratos"]/tbody/tr[1]/td[6]/div/ul/li[4]/a')
SUCESSO = (By.XPATH, '//*[@id="sucesso"]/h4')
PROCESSAMENTO = (
    By.XPATH,
    '//*[@id="contratos"]/tbody/tr[1]/td[6]/div/ul/li[8]/a',
)
CAMPO_SENHA_LOTE = (By.ID, "senhaConta")
BTN_FIM = (By.ID, "btnSalvarDocumento")
TAG_PROCESSANDO = (
    By.XPATH,
    "//small[contains(text(), 'SUBMITTED FOR PROCESSING')"
    " or contains(translate(., 'PROCESSAMENTO', 'processamento'), 'PROCESSAMENTO')"
    " or contains(translate(., 'PROCESSANDO', 'processando'), 'PROCESSANDO')]",
)
TAG_PROCESSADO = (
    By.XPATH,
    "//small[contains(text(), 'PROCESSED')"
    " or contains(translate(., 'PROCESSADO', 'processado'), 'PROCESSADO')]",
)

# PowerForm
CLM = (By.XPATH, '//*[@id="page-wrapper"]/div[2]/div[1]/div[3]/div/a')
POWERFORM = (By.XPATH, '//*[@id="page-wrapper"]/div[2]/div[1]/div[3]/div/ul/li[5]/a')
CRIAR_POWERFORM = (By.ID, "btnSaveTemplate")
MODAL_POWERFORM = (By.ID, "formPowerForm")
CAMPO_COFRE_PF = (By.ID, "uuid_cofre")
CAMPO_TEMPLATE = (By.ID, "uuid-template")
NOME_DOCUMENTO = (By.ID, "nome_documento")
BOTAO_CONTINUAR = (By.ID, "docButton")
BTN_TOKEN = (By.XPATH, '//*[@id="tokenCount"]/button')
CAMPO_EMAIL_PF = (By.XPATH, "//*[starts-with(@id, 'email_')]")
BTN_EMAIL = (By.ID, "fillerButton")
BTN_SEND = (By.XPATH, '//*[@id="pfv2-result"]/button')
BTN_SALVAR_POWER = (By.ID, "btnSalvarPower")

# Reaproveitamento de documento
OPCOES_DOCUMENTO = (
    By.XPATH,
    "//*[self::button or self::a]"
    "[contains(normalize-space(.), 'Opções do documento')]",
)
MENU_REAPROVEITAR = (
    By.XPATH,
    "//a[contains(normalize-space(.), 'Reaproveitar Documento')]",
)
MODAL_REAPROVEITAMENTO = (
    By.XPATH,
    "//div[contains(@class,'modal') and contains(@class,'in')]"
    "[.//*[contains(normalize-space(.), 'Reaproveitar Documento')]]",
)
SELECT_COFRE_REAPROVEITAMENTO = (
    By.XPATH,
    "//div[contains(@class,'modal') and contains(@class,'in')]"
    "//select[@name='uuid-cofre']",
)
BTN_CONFIRMAR_REAPROVEITAMENTO = (
    By.XPATH,
    "//div[contains(@class,'modal') and contains(@class,'in')]"
    "//button[normalize-space(.)='Confirmar']",
)
MSG_REAPROVEITAMENTO_SUCESSO = (
    By.XPATH,
    "//div[contains(@class,'modal') and contains(@class,'in')]//*["
    "contains(translate(., 'REAPROVEITMN', 'reaproveitmn'), 'reaproveitamento') "
    "and contains(., 'sucesso')]",
)

# Pin / canvas
CARREGANDO_DOCUMENTO = (By.XPATH, '//*[@id="doc-div-principal"]/div/img')
CARREGANDO_ANEXO = (By.XPATH, '//*[@id="progress"]/div')
ADD_ANEXO = (By.ID, "id-adicionar-mais-doc")
DOCS_CARREGADOS = (By.ID, "documentosCarregadosDiv")
CANVAS_1 = (By.ID, "canvas1")
CANVAS_2 = (By.ID, "canvas2")
CANVAS_3 = (By.ID, "canvas3")
CANVAS_4 = (By.ID, "canvas4")
BOTAO_ANEXO = (By.CSS_SELECTOR, "#id-adicionar-mais-doc, #btnNovoDoc")
PIN_1 = (
    By.CSS_SELECTOR,
    "#pin-container-overlay-canvas1 .pin, #pin-container-for-canvas1 div img",
)
PIN_2 = (
    By.CSS_SELECTOR,
    "#pin-container-overlay-canvas2 .pin, #pin-container-for-canvas2 div img",
)
PIN_3 = (
    By.CSS_SELECTOR,
    "#pin-container-overlay-canvas3 .pin, #pin-container-for-canvas3 div img",
)
PIN_4 = (
    By.CSS_SELECTOR,
    "#pin-container-overlay-canvas4 .pin, #pin-container-for-canvas4 div img",
)
BTN_REPLICAR_PIN = (
    By.CSS_SELECTOR,
    "#pin-container-overlay-canvas1 button[data-action='replicar'], "
    "#pin-container-for-canvas1 div div:nth-child(3) button:nth-child(1)",
)
BTN_REMOVER_PIN = (
    By.CSS_SELECTOR,
    "#pin-container-overlay-canvas1 button[data-action='remover-todos'], "
    "#pin-container-for-canvas1 div div:nth-child(3) button:nth-child(2)",
)
CHECKBOX_DOC = (By.ID, "input-doc-div-main")
CHECKBOX_ANEXO = (By.ID, "nomeDocumento")
BTN_MODAL_PINS = (By.ID, "selectAdditionals")
BTN_CONFIRMAR_REMOCAO = (By.XPATH, "//div[@class='modal-body']//button[last()]")
PROGRESS_BAR = (By.XPATH, "//div[contains(@class, 'progress-bar-striped')]")
