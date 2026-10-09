"""Locators do editor Tryit (W3Schools) e do iframe de embed D4Sign."""

# W3Schools Tryit
TEXTAREA_CODE = "#textareaCode"
EDITOR_CODEMIRROR = ".CodeMirror"
BTN_RUN = "#runbtn, button[onclick*='submitTryit']"
IFRAME_RESULTADO = "#iframeResult"
IFRAME_D4SIGN = "#d4signIframe"

COOKIE_ACEITAR = (
    "#accept-choices, "
    "#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll, "
    "#onetrust-accept-btn-handler, "
    "button:has-text('Accept all'), "
    "button:has-text('Accept All'), "
    "button:has-text('Aceitar')"
)

# Viewblob dentro do iframe D4Sign
VIEWBLOB = "#viewblobdiv"
CANVAS = "canvas[id^='canvas']"
CANVAS_1 = "#canvas1"
CANVAS_2 = "#canvas2"
CANVAS_3 = "#canvas3"
CANVAS_4 = "#canvas4"
# Playwright não mistura engines (css + xpath) num único seletor separado por
# vírgula: cada parte precisa virar um Locator próprio e ser combinada com
# .or_() (ver EmbedPage._aguardar_carregamento).
CARREGANDO_DOCUMENTO_CSS = "#doc-div-principal img, #progress .progress-bar"
CARREGANDO_DOCUMENTO_XPATH = "xpath=//*[contains(@class,'progress-bar')]"
