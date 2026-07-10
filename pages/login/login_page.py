from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage
from recursos.utils.config import Config


class LoginPage(BasePage):
    IDIOMA_PT = (By.XPATH, '//*[@id="ptLanguage"]')
    EMAIL = (By.ID, "Email")
    PASSWORD = (By.ID, "Passwd")
    BTN_LOGAR = (By.ID, "logar")
    LOGO_D4S = (By.XPATH, '//*[@id="page-wrapper"]/div[1]/nav/div/div/div[1]/a/img')
    MSG_ERRO_LOGIN = (By.CSS_SELECTOR, "#result.alert-danger")

    EMAIL_INEXISTENTE = "naoexiste.automacao@d4sign.com.br"
    SENHA_INCORRETA = "SenhaIncorreta_QA_123"

    COOKIE_COFRE = 'd4sign_ai_cofre = "1"'
    COOKIE_IDIOMA = 'document.cookie = "contratoazul_language=pt"'

    def abrir_pagina_login(self) -> None:
        self.open(Config.login_url())

    def configurar_cookies_iniciais(self) -> None:
        self.execute_script(self.COOKIE_COFRE)
        self.execute_script(self.COOKIE_IDIOMA)

    def preparar_formulario_login(self) -> None:
        self.wait_visible(self.EMAIL)

    def preencher_credenciais(
        self,
        username: str | None = None,
        password: str | None = None,
        preencher_email: bool = True,
        preencher_senha: bool = True,
    ) -> None:
        self.preparar_formulario_login()
        if preencher_email and username is not None:
            self.type_text(self.EMAIL, username)
        if preencher_senha and password is not None:
            self.type_text(self.PASSWORD, password)

    def clicar_entrar(self) -> None:
        self.click(self.BTN_LOGAR, dismiss=False)

    def tentar_login(
        self,
        username: str | None = None,
        password: str | None = None,
        preencher_email: bool = True,
        preencher_senha: bool = True,
    ) -> None:
        self.preencher_credenciais(
            username=username,
            password=password,
            preencher_email=preencher_email,
            preencher_senha=preencher_senha,
        )
        self.clicar_entrar()

    def preencher_credenciais_e_entrar(
        self, username: str | None = None, password: str | None = None
    ) -> None:
        user = username or Config.USERNAME
        pwd = password or Config.PASSWORD
        self.tentar_login(username=user, password=pwd)
        self.dismiss_blocking_modals()
        self.wait_visible(self.LOGO_D4S)

    def fazer_login(self, username: str | None = None, password: str | None = None) -> None:
        self.abrir_pagina_login()
        self.configurar_cookies_iniciais()
        self.preencher_credenciais_e_entrar(username, password)

    def ja_esta_logado(self) -> bool:
        url = (self.driver.current_url or "").lower()
        if "/login" in url:
            return False
        if "viewblob" in url:
            return True
        if self.is_present(self.EMAIL, timeout=1):
            return False
        return self.is_present(self.LOGO_D4S, timeout=3)

    def obter_mensagem_erro_login(self, timeout: int = 10) -> str:
        def mensagem_pronta(driver) -> bool:
            try:
                elemento = driver.find_element(By.ID, "result")
            except Exception:
                return False
            if not elemento.is_displayed():
                return False
            texto = elemento.text.strip()
            return bool(texto) and texto.lower() != "carregando"

        try:
            WebDriverWait(self.driver, timeout).until(mensagem_pronta)
            return self.driver.find_element(By.ID, "result").text.strip()
        except Exception:
            return ""

    def obter_mensagem_validacao_campo(self, locator: tuple[str, str]) -> str:
        element = self.wait_visible(locator)
        return (element.get_attribute("validationMessage") or "").strip()

    def campo_exibe_validacao_obrigatoria(self, locator: tuple[str, str]) -> bool:
        mensagem = self.obter_mensagem_validacao_campo(locator)
        return "preencha este campo" in mensagem.lower()

    def campo_exibe_validacao_email_invalido(self) -> bool:
        mensagem = self.obter_mensagem_validacao_campo(self.EMAIL)
        return "@" in mensagem

    def usuario_esta_logado(self) -> bool:
        return self.is_present(self.LOGO_D4S, timeout=2)
