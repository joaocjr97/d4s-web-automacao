from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage
from pages.envios import envio_locators as L
from recursos.utils.config import Config

# Índice do cofre usado nos testes legados (option[157] => index 156)
COFRE_DESK_INDEX = 156
COFRE_LOTE_INDEX = 1
COFRE_PF_INDEX = 1


class EnvioPage(BasePage):
    """Page Object com fluxos de envio da plataforma D4Sign."""

    def _aguardar_documento_pronto(self, timeout: int = 60) -> None:
        self.dismiss_blocking_modals()
        WebDriverWait(self.driver, timeout).until(
            EC.any_of(
                EC.presence_of_element_located(L.CAMPO_EMAIL_SIGNATARIO),
                EC.presence_of_element_located(L.INCLUIR_EMAIL),
                EC.presence_of_element_located(L.INCLUIR_EMAIL_LEGADO),
                EC.presence_of_element_located(L.LISTA_ASSINATURA_ROW),
                EC.presence_of_element_located(L.BOTAO_ASSINATURA),
            )
        )

    def _signatario_ja_na_lista(self) -> bool:
        for row in self.driver.find_elements(*L.LISTA_ASSINATURA_ROW):
            if (row.text or "").strip():
                return True
        return False

    def _aguardar_signatario_na_lista(self, timeout: int = 60) -> None:
        WebDriverWait(self.driver, timeout).until(
            lambda driver: self._signatario_ja_na_lista()
        )

    def _clicar_incluir_email_signatario(self) -> None:
        for locator in (L.INCLUIR_EMAIL, L.INCLUIR_EMAIL_LEGADO):
            if self.is_present(locator, timeout=5):
                self.scroll_into_view(locator)
                try:
                    self.wait_clickable(locator, timeout=20).click()
                except Exception:
                    self.js_click(locator)
                self.pause(2)
                return

    def _adicionar_email_signatario(self) -> None:
        if self._signatario_ja_na_lista():
            return

        if not self.is_present(L.CAMPO_EMAIL_SIGNATARIO, timeout=15):
            self._clicar_incluir_email_signatario()
        if not self.is_present(L.CAMPO_EMAIL_SIGNATARIO, timeout=15):
            if self._signatario_ja_na_lista():
                return
            raise AssertionError("Campo de e-mail do signatário não apareceu.")

        campo = self.wait_visible(L.CAMPO_EMAIL_SIGNATARIO)
        if not (campo.get_attribute("value") or "").strip():
            self.type_text(L.CAMPO_EMAIL_SIGNATARIO, Config.USERNAME)
            campo = self.wait_visible(L.CAMPO_EMAIL_SIGNATARIO)

        try:
            campo.send_keys(Keys.TAB)
        except Exception:
            pass
        self.pause(1)

        for locator in (L.BTN_ADICIONAR_SIGNATARIO, L.BTN_ADICIONAR_SIGNATARIO_ALT):
            if self.is_present(locator, timeout=5):
                try:
                    self.js_click(locator)
                except Exception:
                    self.safe_click(locator, dismiss=False)
                self.pause(2)
                if self._signatario_ja_na_lista():
                    self._aguardar_barra_progresso()
                    return

        try:
            campo.send_keys(Keys.ENTER)
        except Exception:
            pass
        self.pause(2)
        self._aguardar_barra_progresso()

        if not self._signatario_ja_na_lista():
            raise AssertionError("Não foi possível adicionar o signatário por e-mail.")

    def _aguardar_barra_progresso(self, timeout: int = 60) -> None:
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.invisibility_of_element_located(L.PROGRESS_BAR)
            )
        except Exception:
            pass

    def _garantir_pagina_documento(self, url_documento: str | None = None) -> None:
        if url_documento:
            self.open(url_documento)
            self.dismiss_blocking_modals()
            self.pause(2)

    # --- Desk ---

    def enviar_documento_pela_desk(self) -> str:
        self.dismiss_blocking_modals()
        self.wait_clickable(L.BOTAO_ENVIO).click()
        self.wait_visible(L.SELECT_COFRE)
        self.select_by_index(L.SELECT_COFRE, COFRE_DESK_INDEX)
        self.pause(2)
        self.upload_file(L.FILE_UPLOAD, Config.doc_testes_pdf())
        self._documento_pronto_para_signatarios()
        self.validar_aguardando_signatarios()
        return self.driver.current_url

    def _documento_pronto_para_signatarios(self, timeout: int = 120) -> None:
        WebDriverWait(self.driver, timeout).until(
            EC.any_of(
                EC.presence_of_element_located(L.AGUARDANDO_SIGNATARIOS),
                EC.url_contains("viewblob"),
                EC.presence_of_element_located(L.VIEWBLOB),
                EC.presence_of_element_located(L.CAMPO_EMAIL_SIGNATARIO),
                EC.presence_of_element_located(L.INCLUIR_EMAIL),
                EC.presence_of_element_located(L.INCLUIR_EMAIL_LEGADO),
            )
        )

    def validar_aguardando_signatarios(self) -> None:
        self.dismiss_blocking_modals()
        if self.is_present(L.AGUARDANDO_SIGNATARIOS, timeout=30):
            elemento = self.wait_visible(L.AGUARDANDO_SIGNATARIOS)
            status = (elemento.text or "").strip().upper()
            if "AGUARDANDO" in status and "SIGNAT" in status:
                return

        url = (self.driver.current_url or "").lower()
        assert "viewblob" in url, (
            f"Documento não está na viewblob. URL: {self.driver.current_url}"
        )
        assert (
            self.is_present(L.CAMPO_EMAIL_SIGNATARIO, timeout=20)
            or self.is_present(L.INCLUIR_EMAIL, timeout=5)
            or self.is_present(L.INCLUIR_EMAIL_LEGADO, timeout=5)
        ), "Viewblob aberta, mas fluxo de signatários não está visível."

    # --- Cofre ---

    def abrir_cofre_12(self) -> None:
        self.dismiss_blocking_modals()
        if not self.is_present(L.COFRE_12, timeout=5):
            self.open(Config.desk_url())
            self.pause(2)
            self.dismiss_blocking_modals()
        self.safe_click(L.COFRE_12)
        self.pause(1)
        self.dismiss_blocking_modals()

    def _aguardar_upload_cofre_concluido(self, timeout: int = 150) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.any_of(
                    EC.presence_of_element_located(L.VIEWBLOB),
                    EC.presence_of_element_located(L.VERIFICA_ASSINATURA),
                    EC.presence_of_element_located(L.AGUARDANDO_SIGNATARIOS),
                    EC.presence_of_element_located(L.CANVAS_1),
                    EC.presence_of_element_located(L.INCLUIR_EMAIL),
                    EC.presence_of_element_located(L.INCLUIR_EMAIL_LEGADO),
                    EC.presence_of_element_located(L.CAMPO_EMAIL_SIGNATARIO),
                )
            )
            return True
        except Exception:
            return False

    def enviar_documento_pelo_cofre(self) -> str:
        self.abrir_cofre_12()
        self.dismiss_blocking_modals()
        self.wait_visible(L.NOVO_ARQUIVO)
        try:
            self.wait_clickable(L.NOVO_ARQUIVO).click()
        except Exception:
            self.js_click(L.NOVO_ARQUIVO)
        self.safe_click(L.NEW_FILE, dismiss=False)
        self.pause(4)

        for tentativa in range(2):
            self.wait_present(L.FILE_UPLOAD)
            self.upload_file(L.FILE_UPLOAD, Config.doc_testes_pdf())
            if self._aguardar_upload_cofre_concluido():
                return self.driver.current_url

            self.pause(3)
            self.dismiss_blocking_modals()
            if tentativa == 0 and self.is_present(L.NEW_FILE, timeout=3):
                self.safe_click(L.NEW_FILE, dismiss=False)
                self.pause(2)

        raise AssertionError("Upload pelo cofre não concluiu.")

    # --- Assinatura ---

    def incluir_signatario_por_email(self, url_documento: str | None = None) -> None:
        self._garantir_pagina_documento(url_documento)
        self._aguardar_documento_pronto()
        if self._signatario_ja_na_lista():
            return
        self._clicar_incluir_email_signatario()
        self._adicionar_email_signatario()
        self.wait_clickable(L.BOTAO_ASSINATURA, timeout=60)

    def _abrir_modal_assinatura(self) -> None:
        self.dismiss_blocking_modals()
        self.scroll_into_view(L.ASSINAR)
        for tentativa in range(3):
            try:
                self.wait_clickable(L.ASSINAR, timeout=20).click()
            except Exception:
                self.js_click(L.ASSINAR)
            self.pause(2)
            if self.is_present(L.SENHA_CONTA, timeout=5):
                self.wait_visible(L.SENHA_CONTA)
                return
            self.dismiss_blocking_modals()
        self.wait_visible(L.SENHA_CONTA, timeout=30)

    def enviar_para_assinatura(self) -> None:
        self.scroll_into_view(L.BOTAO_ASSINATURA)
        self.wait_clickable(L.BOTAO_ASSINATURA, timeout=60)
        self.safe_click(L.BOTAO_ASSINATURA, dismiss=False)

        WebDriverWait(self.driver, 60).until(
            EC.any_of(
                EC.element_to_be_clickable(L.BOTAO_ENVIO_2),
                EC.element_to_be_clickable(L.ASSINAR),
            )
        )

        if self.is_present(L.BOTAO_ENVIO_2, timeout=5):
            try:
                botao_envio = self.driver.find_element(*L.BOTAO_ENVIO_2)
                if botao_envio.is_displayed():
                    self.scroll_into_view(L.BOTAO_ENVIO_2)
                    self.safe_click(L.BOTAO_ENVIO_2, dismiss=False)
                    self.pause(3)
            except Exception:
                pass

        self.dismiss_blocking_modals()
        self.wait_clickable(L.ASSINAR, timeout=90)

    def _aguardar_assinatura_concluida(self, timeout: int = 90) -> None:
        try:
            WebDriverWait(self.driver, 30).until(
                EC.invisibility_of_element_located(L.SENHA_CONTA)
            )
        except Exception:
            pass

        self.dismiss_blocking_modals()

        WebDriverWait(self.driver, timeout).until(
            EC.any_of(
                EC.presence_of_element_located(L.VIEWBLOB),
                EC.presence_of_element_located(L.VERIFICA_ASSINATURA),
                EC.presence_of_element_located(L.ASSINATURA_CONCLUIDA),
            )
        )

    def assinar_documento(self) -> None:
        self._abrir_modal_assinatura()
        self.type_text(L.SENHA_CONTA, Config.PASSWORD)
        self.safe_click(L.SALVAR_ASSINATURA, dismiss=False)
        self._aguardar_assinatura_concluida()

    def validar_assinatura_concluida(self) -> None:
        assert self.page_contains(L.VIEWBLOB, timeout=30) or self.page_contains(
            L.VERIFICA_ASSINATURA, timeout=30
        ), "View do documento não foi exibida após assinatura."
        assert (
            self.is_present(L.ASSINATURA_CONCLUIDA, timeout=15)
            or self.is_present(L.VERIFICA_ASSINATURA, timeout=5)
        ), "Assinatura não confirmada na interface."

    # --- Grupo ---

    def _locator_grupo(self) -> tuple[str, str]:
        for locator in (L.GRUPO, L.GRUPO_LEGADO):
            if self.is_present(locator, timeout=3):
                return locator
        return L.GRUPO

    def _locator_selecionar_grupo(self) -> tuple[str, str]:
        for locator in (L.SELECIONAR_GRUPO, L.SELECIONAR_GRUPO_LEGADO):
            if self.is_present(locator, timeout=5):
                return locator
        return L.SELECIONAR_GRUPO

    def enviar_para_grupo_assinatura(self) -> None:
        self._aguardar_documento_pronto()
        grupo = self._locator_grupo()
        self.scroll_into_view(grupo)
        self.safe_click(grupo, dismiss=False)
        self.wait_visible(L.FILTRO_GRUPO)
        self.type_text(L.FILTRO_GRUPO, "Grupo")
        selecionar = self._locator_selecionar_grupo()
        self.wait_visible(selecionar)
        self.safe_click(selecionar, dismiss=False)
        WebDriverWait(self.driver, 30).until(
            lambda driver: "carregando" not in driver.find_element(
                By.ID, "lista-assinatura"
            ).text.lower()
        )
        self.pause(1)
        self.reload()
        self.enviar_para_assinatura()

    def validar_fase_enviado(self) -> None:
        if self.is_present(L.ASSINAR, timeout=10):
            botao = self.wait_clickable(L.ASSINAR, timeout=30)
            assert botao.is_displayed(), "Botão Assinar não visível após envio."
            return
        elemento = self.wait_visible(L.FASE_ENVIADO)
        status = (elemento.text or "").strip().upper()
        assert "ASSINATURAS" in status or "ENVIADO" in status, (
            f"Documento não está na fase enviado. Status: {status!r}"
        )

    # --- Template HTML ---

    def preencher_template_html(self) -> str:
        self.abrir_cofre_12()
        self.wait_visible(L.NOVO_ARQUIVO)
        self.safe_click(L.NOVO_ARQUIVO, dismiss=False)
        self.safe_click(L.TEMPLATE_HTML, dismiss=False)
        self.type_text(L.CAMPO_MARCA, "Apple")
        self.type_text(L.CAMPO_LARANJA, "Fruta")
        self.type_text(L.CAMPO_COR, "Preto")
        self.type_text(L.CAMPO_TRUE_FALSE, "TRUE")
        self.type_text(L.CAMPO_RUA, "Av. Brasil")
        self.type_text(L.CAMPO_LUGARES, "Paris")
        self.type_text(L.CAMPO_RESTAURANT, "Taverna Medieval")
        self.safe_click(L.SALVAR_TEMPLATE, dismiss=False)
        self.wait_present(L.VERIFICA_ENVIO)
        return self.driver.current_url

    def enviar_template_html(self) -> str:
        self.incluir_signatario_por_email()
        self.pause(10)
        self.enviar_para_assinatura()
        return self.driver.current_url

    def assinar_template_html(self) -> None:
        if not self.is_present(L.ASSINAR, timeout=15):
            raise AssertionError(
                "Botão Assinar não disponível para o template HTML."
            )
        self.assinar_documento()
        assert self.page_contains(L.VERIFICA_ASSINATURA)

    # --- Lote ---

    def _fechar_modal_sucesso_lote(self) -> None:
        from selenium.webdriver.common.action_chains import ActionChains
        from selenium.webdriver.common.keys import Keys

        for selector in (
            "#sucesso button.close",
            "#sucesso [data-dismiss='modal']",
            "#sucesso .close",
        ):
            for botao in self.driver.find_elements(By.CSS_SELECTOR, selector):
                if botao.is_displayed():
                    try:
                        botao.click()
                    except Exception:
                        self.execute_script("arguments[0].click();", botao)
                    self.pause(1)
                    return

        try:
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
        except Exception:
            pass
        self.pause(1)

    def _lote_foi_processado(self) -> bool:
        if self.is_present(L.TAG_PROCESSADO, timeout=3):
            return True
        linhas = self.driver.find_elements(By.CSS_SELECTOR, "#contratos tbody tr")
        if not linhas:
            return False
        texto = (linhas[0].text or "").upper()
        return any(
            termo in texto
            for termo in ("PROCESSADO", "PROCESSED", "FINALIZADO", "CONCLUÍDO", "CONCLUIDO")
        )

    def validar_lote_processado(self) -> None:
        assert self._lote_foi_processado(), (
            "Lote não está com status de processamento concluído."
        )

    def enviar_lote(self) -> None:
        self.dismiss_blocking_modals()
        self.safe_click(L.LOTE)
        self.wait_visible(L.BTN_LOTE)
        self.safe_click(L.BTN_LOTE, dismiss=False)
        self.wait_visible(L.CAMPO_COFRE_LOTE)
        self.select_by_index(L.CAMPO_COFRE_LOTE, COFRE_LOTE_INDEX)
        self.wait_visible(L.NOME_ENVIO)
        self.type_text(L.NOME_ENVIO, "Envio em Lote - Behave")
        self.select_by_index(L.TIPO_DOC, 1)
        self.safe_click(L.BTN_SALVAR_PF, dismiss=False)
        self.pause(2)
        self.safe_click(L.BTN_OPCAO, dismiss=False)
        self.wait_visible(L.SELECIONAR_DOC)
        self.safe_click(L.SELECIONAR_DOC, dismiss=False)
        self.pause(2)
        self.upload_file(L.FILE_UPLOAD, Config.planilha_lote_xlsx())
        self.pause(5)
        if self.is_present(L.SUCESSO, timeout=5):
            self._fechar_modal_sucesso_lote()
        self.reload()
        self.safe_click(L.BTN_OPCAO, dismiss=False)
        self.wait_visible(L.PROCESSAMENTO)
        self.safe_click(L.PROCESSAMENTO, dismiss=False)
        self.pause(2)
        self.wait_visible(L.CAMPO_SENHA_LOTE)
        self.type_text(L.CAMPO_SENHA_LOTE, Config.PASSWORD)
        self.safe_click(L.BTN_FIM, dismiss=False)
        self.pause(3)
        if not self.is_present(L.TAG_PROCESSANDO, timeout=30):
            self.pause(5)

        for _ in range(30):
            self.reload()
            if self._lote_foi_processado():
                return
            self.pause(15)

        raise AssertionError("Lote não foi processado após 30 tentativas.")

    # --- PowerForm ---

    def preparar_powerform(self) -> None:
        self.dismiss_blocking_modals()
        self.safe_click(L.CLM)
        self.safe_click(L.POWERFORM)
        self.wait_visible(L.CRIAR_POWERFORM)
        self.safe_click(L.CRIAR_POWERFORM, dismiss=False)
        self.wait_present(L.MODAL_POWERFORM)
        self.select_by_index(L.CAMPO_COFRE_PF, COFRE_PF_INDEX)
        self.pause(5)
        self.select_by_index(L.CAMPO_TEMPLATE, 337)
        self.type_text(L.NOME_DOCUMENTO, "PowerForm - Automação")
        self.safe_click(L.BOTAO_CONTINUAR, dismiss=False)
        self.wait_visible(L.BTN_TOKEN)
        self.safe_click(L.BTN_TOKEN, dismiss=False)
        self.pause(2)
        self.type_text(L.CAMPO_EMAIL_PF, Config.USERNAME)
        self.wait_visible(L.CAMPO_EMAIL_PF).send_keys("\t")
        self.safe_click(L.BTN_EMAIL, dismiss=False)
        self.safe_click(L.BTN_SALVAR_PF, dismiss=False)
        self.pause(5)
        self.safe_click(L.BTN_SEND, dismiss=False)
        self.wait_visible(L.BTN_SALVAR_POWER)
        self.safe_click(L.BTN_SALVAR_POWER, dismiss=False)
        self.wait_invisible(L.BTN_SALVAR_POWER)

    # --- Pin / canvas ---

    def _aguardar_canvas_documento(self, timeout: int = 90) -> None:
        self.dismiss_blocking_modals()
        if self.is_present(L.CARREGANDO_DOCUMENTO, timeout=10):
            try:
                WebDriverWait(self.driver, timeout).until(
                    EC.invisibility_of_element_located(L.CARREGANDO_DOCUMENTO)
                )
            except Exception:
                pass

        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(L.CANVAS_1)
        )
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located(L.CANVAS_2)
            )
        except Exception:
            pass

        self.scroll_into_view(L.CANVAS_1)
        self.pause(2)

    def _aguardar_anexo_carregado(self, timeout: int = 120) -> None:
        if self.is_present(L.CARREGANDO_ANEXO, timeout=10):
            try:
                WebDriverWait(self.driver, timeout).until(
                    EC.invisibility_of_element_located(L.CARREGANDO_ANEXO)
                )
            except Exception:
                pass

        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(L.CANVAS_3)
        )
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(L.CANVAS_4)
            )
        except Exception:
            pass

        self.wait_present(L.DOCS_CARREGADOS)
        self.wait_present(L.ADD_ANEXO)

    def enviar_documento_e_validar_canvas(self) -> str:
        self.enviar_documento_pelo_cofre()
        if self.is_present(L.CARREGANDO_DOCUMENTO, timeout=10):
            try:
                WebDriverWait(self.driver, 90).until(
                    EC.invisibility_of_element_located(L.CARREGANDO_DOCUMENTO)
                )
            except Exception:
                pass
        self._aguardar_canvas_documento()
        self.scroll_into_view(L.BOTAO_ANEXO)
        try:
            self.wait_clickable(L.BOTAO_ANEXO, timeout=60).click()
        except Exception:
            self.js_click(L.BOTAO_ANEXO)
        self.pause(2)
        self.upload_file(L.FILE_UPLOAD, Config.doc_testes_pdf())
        self._aguardar_anexo_carregado()
        return self.driver.current_url

    def _selecionar_pin_canvas1(self) -> None:
        pin = self.wait_present(L.PIN_1)
        self.execute_script(
            "arguments[0].scrollIntoView({block: 'center', inline: 'center'});", pin
        )
        self.pause(1)
        try:
            pin.click()
        except Exception:
            self.execute_script("arguments[0].click();", pin)
        self.pause(1)

    def _clicar_botao_pin(self, locator: tuple[str, str]) -> None:
        self._selecionar_pin_canvas1()
        botao = self.wait_clickable(locator)
        try:
            botao.click()
        except Exception:
            self.js_click(locator)
        self.pause(1)

    def _replicar_pin_em_todas_paginas(self) -> None:
        self._clicar_botao_pin(L.BTN_REPLICAR_PIN)
        if self.is_present(L.CHECKBOX_DOC, timeout=5):
            self.safe_click(L.CHECKBOX_DOC, dismiss=False)
            if self.is_present(L.CHECKBOX_ANEXO, timeout=3):
                self.safe_click(L.CHECKBOX_ANEXO, dismiss=False)
            self.safe_click(L.BTN_MODAL_PINS, dismiss=False)
            self.pause(2)

    def adicionar_e_validar_pins(self) -> None:
        self.incluir_signatario_por_email()
        self._aguardar_signatario_na_lista()
        self._aguardar_barra_progresso()
        self.pause(2)
        self._clicar_canvas_para_adicionar_pin()
        self._aguardar_pin_canvas1()
        self.pause(2)
        self._replicar_pin_em_todas_paginas()
        self.pause(3)
        for pin in (L.PIN_1, L.PIN_2, L.PIN_3, L.PIN_4):
            assert self.page_contains(pin), f"Pin não replicado: {pin}"
        self._clicar_botao_pin(L.BTN_REMOVER_PIN)
        self.pause(1)
        if self.is_present(L.BTN_CONFIRMAR_REMOCAO, timeout=5):
            self.safe_click(L.BTN_CONFIRMAR_REMOCAO, dismiss=False)
        self.pause(2)
        for pin in (L.PIN_1, L.PIN_2, L.PIN_3, L.PIN_4):
            assert not self.is_present(pin), f"Pin ainda visível: {pin}"

    def incluir_email_para_pin(self) -> None:
        """Habilita pins no canvas (fluxo legado envio-canvas-pins.robot)."""
        self.dismiss_blocking_modals()
        self._aguardar_canvas_documento()

        if self._signatario_ja_na_lista():
            self._aguardar_barra_progresso()
            return

        self._clicar_incluir_email_signatario()
        if self.is_present(L.CAMPO_EMAIL_SIGNATARIO, timeout=10):
            self._adicionar_email_signatario()
        elif not self._signatario_ja_na_lista():
            raise AssertionError(
                "Não foi possível habilitar signatário para adicionar pin no canvas."
            )

        self._aguardar_signatario_na_lista()
        self._aguardar_barra_progresso()

    def _pin_presente_canvas1(self, timeout: int = 3) -> bool:
        return self.is_present(L.PIN_1, timeout=timeout)

    def _aguardar_pin_canvas1(self, timeout: int = 60) -> None:
        WebDriverWait(self.driver, timeout).until(
            lambda driver: self._pin_presente_canvas1(timeout=1)
        )

    def _clicar_canvas_posicao(self, offset_x: int, offset_y: int) -> None:
        self.execute_script(
            """
            var canvas = document.getElementById('canvas1');
            if (!canvas) return;
            canvas.scrollIntoView({block: 'start', inline: 'nearest'});
            var ox = arguments[0], oy = arguments[1];
            var rect = canvas.getBoundingClientRect();
            var x = rect.left + ox, y = rect.top + oy;
            if (y > window.innerHeight - 80 || y < 0) {
                window.scrollBy(0, y - window.innerHeight * 0.55);
                rect = canvas.getBoundingClientRect();
                x = rect.left + ox;
                y = rect.top + oy;
            }
            ['mousedown', 'mouseup', 'click'].forEach(function(type) {
                canvas.dispatchEvent(new MouseEvent(type, {
                    clientX: x, clientY: y, bubbles: true, cancelable: true, view: window
                }));
            });
            """,
            offset_x,
            offset_y,
        )

    def _clicar_canvas_para_adicionar_pin(self) -> None:
        from selenium.webdriver.common.action_chains import ActionChains

        self.scroll_into_view(L.CANVAS_1)
        self.execute_script("window.scrollTo(0, 0);")
        self.pause(2)

        canvas = self.wait_visible(L.CANVAS_1)
        if not canvas.is_enabled():
            raise AssertionError("Canvas do documento não está habilitado para clique.")

        for offset_x, offset_y in ((300, 600), (150, 150), (200, 400), (100, 100)):
            try:
                ActionChains(self.driver).move_to_element_with_offset(
                    canvas, offset_x, offset_y
                ).click().perform()
            except Exception:
                self._clicar_canvas_posicao(offset_x, offset_y)
            self.pause(2)
            if self._pin_presente_canvas1(timeout=3):
                return

        try:
            self.click_at_coordinates(L.CANVAS_1, 300, 600)
        except Exception:
            pass
        self.pause(2)

    def enviar_e_adicionar_pin_no_canvas(self) -> None:
        self.enviar_documento_pelo_cofre()
        self._aguardar_canvas_documento()
        self.incluir_email_para_pin()
        self.pause(2)
        self._clicar_canvas_para_adicionar_pin()
        self._aguardar_pin_canvas1(timeout=90)
