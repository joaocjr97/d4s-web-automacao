"""Anexo com espera completa."""
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.envios import envio_locators as L
from pages.envios.envio_page import EnvioPage
from pages.login.login_page import LoginPage
from recursos.utils.config import Config
from recursos.utils.driver_factory import create_driver

Config.load()
driver = create_driver(Config)
LoginPage(driver, timeout=Config.LOGIN_TIMEOUT).fazer_login()
page = EnvioPage(driver, timeout=90)
page.enviar_documento_pelo_cofre()
page._aguardar_canvas_documento()

anexo = (By.ID, "id-adicionar-mais-doc")
page.scroll_into_view(anexo)
page.js_click(anexo)
time.sleep(2)
page.upload_file(L.FILE_UPLOAD, Config.doc_testes_pdf())
page.wait_for_document_loaded(L.CARREGANDO_ANEXO, L.CANVAS_3)
try:
    WebDriverWait(driver, 90).until(EC.presence_of_element_located(L.CANVAS_4))
    print("canvas4 OK")
except Exception as e:
    print("canvas4 fail", e)
print("canvas3", page.is_present(L.CANVAS_3))
print("docs", page.is_present(L.DOCS_CARREGADOS))

driver.quit()
