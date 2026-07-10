"""Testa upload de anexo via novo seletor."""
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from selenium.webdriver.common.by import By

from pages.envios import envio_locators as L
from pages.envios.envio_page import EnvioPage
from pages.login.login_page import LoginPage
from recursos.utils.config import Config
from recursos.utils.driver_factory import create_driver

Config.load()
driver = create_driver(Config)
LoginPage(driver, timeout=Config.LOGIN_TIMEOUT).fazer_login()
page = EnvioPage(driver, timeout=60)
page.enviar_documento_pelo_cofre()
page._aguardar_canvas_documento()

anexo = (By.ID, "id-adicionar-mais-doc")
page.scroll_into_view(anexo)
page.js_click(anexo)
time.sleep(2)
print("fileupload present:", page.is_present(L.FILE_UPLOAD, 3))
page.upload_file(L.FILE_UPLOAD, Config.doc_testes_pdf())
time.sleep(5)
for c in ["canvas3", "canvas4", "documentosCarregadosDiv"]:
    print(c, len(driver.find_elements(By.ID, c)))

driver.quit()
