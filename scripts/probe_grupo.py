"""Localiza opção de grupo na viewblob."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from selenium.webdriver.common.by import By

from pages.envios.envio_page import EnvioPage
from pages.login.login_page import LoginPage
from recursos.utils.config import Config
from recursos.utils.driver_factory import create_driver

Config.load()
driver = create_driver(Config)
LoginPage(driver, timeout=Config.LOGIN_TIMEOUT).fazer_login()
page = EnvioPage(driver, timeout=60)
url = page.enviar_documento_pela_desk()
page._garantir_pagina_documento(url)
page._aguardar_documento_pronto()

for xpath in [
    "//a[contains(translate(normalize-space(.), 'GRUPO', 'grupo'), 'grupo')]",
    "//*[@id='lista-assinatura']//a[contains(., 'Grupo')]",
    "//*[@id='page-wrapper']//div[contains(@class,'div[4]')]//a",
]:
    els = driver.find_elements(By.XPATH, xpath)
    print(xpath[:60], "->", len(els))
    for e in els[:5]:
        print(" ", repr(e.text.strip()[:50]), e.is_displayed())

# links na área de signatários
area = driver.find_elements(
    By.XPATH,
    "//*[@id='page-wrapper']//div[contains(@class,'div[4]') or contains(@id,'assinatura')]//a",
)
for e in area[:20]:
    t = e.text.strip()
    if t:
        print("area:", repr(t), e.is_displayed())

driver.quit()
