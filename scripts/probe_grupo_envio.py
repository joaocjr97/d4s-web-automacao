"""Debug fluxo envio após adicionar grupo."""
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
page = EnvioPage(driver, timeout=90)
url = page.enviar_documento_pela_desk()
page._garantir_pagina_documento(url)
page._aguardar_documento_pronto()
page.safe_click(page._locator_grupo(), dismiss=False)
page.wait_visible(L.FILTRO_GRUPO)
page.type_text(L.FILTRO_GRUPO, "Grupo")
sel = page._locator_selecionar_grupo()
page.wait_visible(sel)
page.safe_click(sel, dismiss=False)
page.pause(3)

lista = driver.find_element(By.ID, "lista-assinatura").text[:200]
print("lista após Adicionar:", repr(lista))
print("ASSINAR btn:", page.is_present(L.ASSINAR, 2))
print("BOTAO_ASSINATURA:", page.is_present(L.BOTAO_ASSINATURA, 2))
btn = driver.find_elements(*L.BOTAO_ASSINATURA)
if btn:
    print("  enabled:", btn[0].is_enabled(), "displayed:", btn[0].is_displayed())

page.reload()
page.pause(3)
lista2 = driver.find_element(By.ID, "lista-assinatura").text[:200]
print("lista após reload:", repr(lista2))
btn2 = driver.find_elements(*L.BOTAO_ASSINATURA)
if btn2:
    print("BOTAO_ASSINATURA pós-reload enabled:", btn2[0].is_enabled())

driver.quit()
