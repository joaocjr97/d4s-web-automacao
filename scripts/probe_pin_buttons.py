"""Probe botões replicar/remover pin."""
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
page.enviar_documento_e_validar_canvas()
page.incluir_signatario_por_email()
time.sleep(2)
page._clicar_canvas_posicao(200, 200)
time.sleep(3)
page._aguardar_pin_canvas1(timeout=30)

pin = driver.find_element(By.CSS_SELECTOR, "#pin-container-overlay-canvas1 .pin")
print(pin.get_attribute("outerHTML")[:2500])

for sel in [
    "button",
    "[class*='replic']",
    "[class*='remove']",
    "[title]",
]:
    els = pin.find_elements(By.CSS_SELECTOR, sel)
    print(sel, [(e.get_attribute("class"), e.get_attribute("title"), e.text) for e in els])

# busca global perto do pin
btns = driver.find_elements(
    By.XPATH,
    "//*[@id='pin-container-overlay-canvas1']//button | "
    "//*[contains(@class,'pin')]//button",
)
print("all pin buttons:", [(b.get_attribute("class"), b.text, b.is_displayed()) for b in btns])

driver.quit()
