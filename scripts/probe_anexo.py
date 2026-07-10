"""Probe botão anexo após upload cofre."""
import sys
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

for sel in [
    ("btnNovoDoc", (By.ID, "btnNovoDoc")),
    ("BOTAO_ANEXO", L.BOTAO_ANEXO),
    ("ADD_ANEXO", L.ADD_ANEXO),
    ("id-adicionar-mais-doc", (By.ID, "id-adicionar-mais-doc")),
]:
    els = driver.find_elements(*sel[1])
    print(sel[0], "count", len(els))
    for e in els[:2]:
        print(" ", e.is_displayed(), e.is_enabled(), e.text[:40], e.get_attribute("class"))

# busca por texto anexo
links = driver.find_elements(By.XPATH, "//*[contains(translate(., 'ANEXO', 'anexo'), 'anexo')]")
print("texto anexo:", [(l.tag_name, l.text[:50], l.is_displayed()) for l in links[:8]])

driver.quit()
