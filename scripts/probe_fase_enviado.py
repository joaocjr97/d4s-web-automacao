"""Status após envio com scroll no botão."""
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
page = EnvioPage(driver, timeout=90)
url = page.enviar_documento_pela_desk()
page._garantir_pagina_documento(url)
page.enviar_para_grupo_assinatura()
time.sleep(2)
print("url:", driver.current_url)
for s in driver.find_elements(By.CSS_SELECTOR, "#page-wrapper span"):
    t = (s.text or "").strip()
    if t and s.is_displayed() and ("AGUARD" in t.upper() or "ENVI" in t.upper()):
        print("status:", repr(t))
print("ASSINAR:", page.is_present(L.ASSINAR, 3))

driver.quit()
