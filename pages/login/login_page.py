from pages.base_page import BasePage
from recursos.utils.config import Config


class LoginPage(BasePage):
    IDIOMA_PT = 'xpath=//*[@id="ptLanguage"]'
    EMAIL = "#Email"
    PASSWORD = "#Passwd"
    BTN_LOGAR = "#logar"
    LOGO_D4S = 'xpath=//*[@id="page-wrapper"]/div[1]/nav/div/div/div[1]/a/img'
    MSG_ERRO_LOGIN = "#result.alert-danger"

    EMAIL_INEXISTENTE = "naoexiste.automacao@d4sign.com.br"
    SENHA_INCORRETA = "SenhaIncorreta_QA_123"

    COOKIE_COFRE = 'd4sign_ai_cofre = "1"'
    COOKIE_IDIOMA = 'document.cookie = "contratoazul_language=pt"'

    def abrir_pagina_login(self) -> None:
        try:
            if hasattr(self.driver, "clear_cookies"):
                self.driver.clear_cookies()
            else:
                self.page.context.clear_cookies()
        except Exception:
            pass
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

    # Mensagens reais observadas no CI (UI em inglês / Chrome en-US).
    # Mantém equivalentes em PT para execução local.
    MSG_LOGIN_INVALIDO = (
        "Invalid email or password.",
        "E-mail ou senha inválida.",
    )
    MSG_CAMPO_OBRIGATORIO = (
        "please fill out this field",
        "preencha este campo",
        "please fill in this field",
    )

    def obter_mensagem_erro_login(self, timeout: int = 15) -> str:
        def mensagem_pronta() -> bool:
            try:
                elemento = self.page.locator("#result").first
                if not elemento.is_visible():
                    return False
                texto = (elemento.inner_text() or "").strip().lower()
                if not texto:
                    return False
                return texto not in {"carregando", "loading"}
            except Exception:
                return False

        try:
            self.wait_until(mensagem_pronta, timeout=timeout)
            return (self.page.locator("#result").first.inner_text() or "").strip()
        except Exception:
            return ""

    def mensagem_erro_login_valida(self, mensagem_esperada: str | None = None) -> bool:
        """Aceita a mensagem atual da UI (EN no CI) e equivalentes em PT."""
        erro = self.obter_mensagem_erro_login()
        if not erro:
            return False
        candidatas = list(self.MSG_LOGIN_INVALIDO)
        if mensagem_esperada and mensagem_esperada not in candidatas:
            candidatas.append(mensagem_esperada)
        return any(c in erro for c in candidatas)

    def obter_mensagem_validacao_campo(self, locator: str) -> str:
        element = self.wait_visible(locator)
        return (element.evaluate("el => el.validationMessage") or "").strip()

    def campo_exibe_validacao_obrigatoria(self, locator: str) -> bool:
        mensagem = self.obter_mensagem_validacao_campo(locator).lower()
        return any(trecho in mensagem for trecho in self.MSG_CAMPO_OBRIGATORIO)

    def campo_exibe_validacao_email_invalido(self) -> bool:
        mensagem = self.obter_mensagem_validacao_campo(self.EMAIL).lower()
        return "@" in mensagem or "email" in mensagem or "e-mail" in mensagem

    def usuario_esta_logado(self) -> bool:
        return self.is_present(self.LOGO_D4S, timeout=2)
