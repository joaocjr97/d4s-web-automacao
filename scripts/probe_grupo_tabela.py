"""Detalha HTML da tabela de grupos."""
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
url = page.enviar_documento_pela_desk()
page._garantir_pagina_documento(url)
page._aguardar_documento_pronto()
page.scroll_into_view(page._locator_grupo())
page.safe_click(page._locator_grupo(), dismiss=False)
page.wait_visible(L.FILTRO_GRUPO)
page.type_text(L.FILTRO_GRUPO, "Grupo")

WebDriverWait(driver, 30).until(
    lambda d: any(
        "grupo" in (r.text or "").lower()
        for r in d.find_elements(By.CSS_SELECTOR, "#tabela-grupos tbody tr")
    )
)
rows = driver.find_elements(By.CSS_SELECTOR, "#tabela-grupos tbody tr")
for i, r in enumerate(rows):
    if "grupo" in (r.text or "").lower():
        print("row", i, repr(r.text))
        print(r.get_attribute("outerHTML")[:500])
        for sel in ["a", "td", "button", "[onclick]"]:
            els = r.find_elements(By.CSS_SELECTOR, sel)
            print(sel, [(e.text.strip(), e.is_displayed()) for e in els[:3]])

driver.quit()
