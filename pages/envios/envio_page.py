import time

from pages.base_page import BasePage
from pages.envios import envio_locators as L
from recursos.utils.config import Config

# Índice do cofre usado nos testes legados (option[157] => index 156)
COFRE_DESK_INDEX = 156
COFRE_LOTE_INDEX = 1
COFRE_PF_INDEX = 1

TEMPLATE_PF_LABEL = "Teste Template Word.docx"
TEMPLATE_PF_INDEX = 337


class EnvioPage(BasePage):
    """Page Object com fluxos de envio da plataforma D4Sign."""

    def _aguardar_documento_pronto(self, timeout: int = 60) -> None:
        self.dismiss_blocking_modals()
        self.wait_any_present(
            L.CAMPO_EMAIL_SIGNATARIO,
            L.INCLUIR_EMAIL,
            L.INCLUIR_EMAIL_LEGADO,
            L.LISTA_ASSINATURA_ROW,
            L.BOTAO_ASSINATURA,
            timeout=timeout,
        )

    def _signatario_ja_na_lista(self) -> bool:
        for row in self.page.locator(L.LISTA_ASSINATURA_ROW).all():
            if (row.inner_text() or "").strip():
                return True
        return False

    def _aguardar_signatario_na_lista(self, timeout: int = 60) -> None:
        self.wait_until(
            lambda: self._signatario_ja_na_lista(),
            timeout=timeout,
            message="Signatário não apareceu na lista.",
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
        if not (campo.input_value() or "").strip():
            self.type_text(L.CAMPO_EMAIL_SIGNATARIO, Config.USERNAME)
            campo = self.wait_visible(L.CAMPO_EMAIL_SIGNATARIO)

        try:
            campo.press("Tab")
        except Exception:
            pass
        self.pause(1)

        self._confirmar_inclusao_signatario_um_clique(campo)

    def _locator_botao_adicionar_signatario(self) -> str | None:
        if self.is_present(L.BTN_ADICIONAR_SIGNATARIO, timeout=5):
            return L.BTN_ADICIONAR_SIGNATARIO
        if self.is_present(L.BTN_ADICIONAR_SIGNATARIO_ALT, timeout=3):
            return L.BTN_ADICIONAR_SIGNATARIO_ALT
        return None

    def _clicar_botao_adicionar_uma_vez(self, locator: str) -> None:
        """Dispara Adicionar uma vez. O fallback só roda se o clique não chegou a sair."""
        if self._signatario_ja_na_lista():
            return
        try:
            self.js_click(locator)
        except Exception:
            if self._signatario_ja_na_lista():
                return
            self.wait_clickable(locator, timeout=10).click(timeout=5000)

    def _confirmar_inclusao_signatario_um_clique(self, campo) -> None:
        if self._signatario_ja_na_lista():
            self._aguardar_barra_progresso()
            return

        locator = self._locator_botao_adicionar_signatario()
        if locator:
            self._clicar_botao_adicionar_uma_vez(locator)
            self._aguardar_barra_progresso()
            try:
                self._aguardar_signatario_na_lista(timeout=8)
                return
            except TimeoutError:
                pass

        if self._signatario_ja_na_lista():
            self._aguardar_barra_progresso()
            return

        try:
            campo.press("Enter")
        except Exception:
            pass
        self._aguardar_barra_progresso()
        try:
            self._aguardar_signatario_na_lista(timeout=15)
        except TimeoutError:
            raise AssertionError(
                "Não foi possível adicionar o signatário por e-mail."
            ) from None

    def _aguardar_barra_progresso(self, timeout: int = 60) -> None:
        try:
            self.wait_invisible(L.PROGRESS_BAR, timeout=timeout)
        except Exception:
            pass

    def _garantir_pagina_documento(self, url_documento: str | None = None) -> None:
        if url_documento:
            self.open(url_documento)
            self.dismiss_blocking_modals()
            self.pause(2)

    def _garantir_desk_limpa(self) -> None:
        """Volta à desk e fecha modais residuais (cenários @signature reusam sessão)."""
        self.open(Config.desk_url())
        self.pause(2)
        self.dismiss_blocking_modals()
        try:
            self.page.keyboard.press("Escape")
        except Exception:
            pass
        self.pause(0.5)
        self.dismiss_blocking_modals()

    # --- Desk ---

    def enviar_documento_pela_desk(self) -> str:
        self._garantir_desk_limpa()
        self.wait_clickable(L.BOTAO_ENVIO).click()
        self.wait_visible(self.FORM_UPLOAD, timeout=60)
        self.wait_visible(L.SELECT_COFRE, timeout=60)
        self.select_by_index(L.SELECT_COFRE, COFRE_DESK_INDEX)
        self.pause(2)
        self.upload_file(L.FILE_UPLOAD, Config.doc_testes_pdf())
        self._documento_pronto_para_signatarios()
        self.validar_aguardando_signatarios()
        return self.driver.current_url

    def _documento_pronto_para_signatarios(self, timeout: int = 120) -> None:
        deadline_url = timeout
        self.wait_until(
            lambda: (
                self.is_present(L.AGUARDANDO_SIGNATARIOS, timeout=0.5)
                or "viewblob" in (self.driver.current_url or "").lower()
                or self.is_present(L.VIEWBLOB, timeout=0.5)
                or self.is_present(L.CAMPO_EMAIL_SIGNATARIO, timeout=0.5)
                or self.is_present(L.INCLUIR_EMAIL, timeout=0.5)
                or self.is_present(L.INCLUIR_EMAIL_LEGADO, timeout=0.5)
            ),
            timeout=deadline_url,
            message="Documento não ficou pronto para signatários.",
        )

    def validar_aguardando_signatarios(self) -> None:
        self.dismiss_blocking_modals()
        if self.is_present(L.AGUARDANDO_SIGNATARIOS, timeout=30):
            status = self.get_text(L.AGUARDANDO_SIGNATARIOS).upper()
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
        """Abre o cofre de automação pelo link do nome, não pela estrela."""
        from pages.cofres.cofre_page import CofrePage

        CofrePage(self.driver).pesquisar_e_abrir_cofre("12")

    def _aguardar_upload_cofre_concluido(self, timeout: int = 90) -> bool:
        """Retorna True se a viewblob abriu; False se apareceu alerta ou esgotou."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            if self._upload_cofre_teve_sucesso():
                return True
            if self._texto_alerta_upload():
                return False
            self.pause(0.5)
        return False

    def _upload_cofre_teve_sucesso(self) -> bool:
        # Não usar AGUARDANDO_SIGNATARIOS aqui: a lista do cofre já mostra
        # esse status em documentos antigos e gerava falso positivo.
        try:
            url = (self.page.evaluate("() => window.location.href") or "").lower()
        except Exception:
            url = (self.driver.current_url or "").lower()
        if "viewblob" in url:
            return True
        return (
            self.is_present(L.VIEWBLOB, timeout=0.3)
            or self.is_present(L.CANVAS_1, timeout=0.3)
            or self.is_present(L.CAMPO_EMAIL_SIGNATARIO, timeout=0.3)
        )

    def _texto_alerta_upload(self) -> str:
        try:
            for alerta in self.page.locator(L.ALERTA_LIMITE_UPLOAD).all():
                if not alerta.is_visible():
                    continue
                texto = (alerta.inner_text() or "").strip()
                if texto:
                    return texto
        except Exception:
            pass
        return ""

    def _fechar_modal_upload_cofre(self) -> None:
        self._fechar_modal_ativo()
        try:
            self.page.keyboard.press("Escape")
        except Exception:
            pass
        self.pause(0.5)
        self.dismiss_blocking_modals()
        try:
            self.wait_invisible(L.MODAL_UPLOAD_COFRE, timeout=5)
        except Exception:
            pass

    def _abrir_modal_envio_cofre(self) -> None:
        """Abre o modal de envio a partir do menu Novo documento do cofre."""
        self.dismiss_blocking_modals()
        if self.is_visible(L.MODAL_UPLOAD_COFRE, timeout=2):
            return

        botao = L.BTN_NOVO_DOC if self.is_present(L.BTN_NOVO_DOC, timeout=2) else L.NOVO_ARQUIVO
        self.wait_visible(botao, timeout=30)
        try:
            self.wait_clickable(botao, timeout=15, retries=1).click()
        except Exception:
            self.js_click(botao)
        self.pause(0.5)

        # Clica só se o item do dropdown estiver visível (menu aberto).
        try:
            self.wait_clickable(L.NEW_FILE, timeout=10, retries=1).click()
        except Exception:
            try:
                self.wait_clickable(botao, timeout=5, retries=1).click()
                self.pause(0.5)
            except Exception:
                pass
            # Fallback: dispara o mesmo eModalO do href, mesmo se o <a> estiver oculto.
            self.wait_present(L.NEW_FILE, timeout=10).evaluate("el => el.click()")

        self.wait_any_present(L.FILE_UPLOAD, L.MODAL_UPLOAD_COFRE, timeout=30)

    def _enviar_arquivo_modal_cofre(self, file_path: str) -> None:
        """Anexa o arquivo no modal do cofre (input direto + fallback file chooser)."""
        self.dismiss_blocking_modals()
        loc_upload = (
            L.FILE_UPLOAD_MODAL
            if self.is_present(L.FILE_UPLOAD_MODAL, timeout=3)
            else L.FILE_UPLOAD
        )
        self.wait_present(loc_upload, timeout=30)
        self.upload_file(loc_upload, file_path)
        self.pause(2)
        if self._upload_cofre_teve_sucesso() or self._texto_alerta_upload():
            return

        # Se o plugin não processou o set_input_files, usa o botão nativo.
        botao = (
            "xpath=//div[contains(@class,'modal') and contains(@class,'in')]"
            "//*[self::button or self::a or self::label]"
            "[contains(normalize-space(.), 'Escolher documento') "
            "or contains(normalize-space(.), 'Choose document')]"
        )
        if not self.is_visible(botao, timeout=3):
            return
        try:
            with self.page.expect_file_chooser(timeout=10000) as seletor:
                self.page.locator(botao).first.click()
            seletor.value.set_files(file_path)
            self.pause(2)
        except Exception:
            pass

    def enviar_documento_pelo_cofre(self) -> str:
        self.abrir_cofre_12()
        ultimo_alerta = ""
        arquivo = Config.doc_testes_pdf()

        for tentativa in range(2):
            self.dismiss_blocking_modals()
            self._fechar_modal_upload_cofre()
            self._abrir_modal_envio_cofre()
            # Não chamar dismiss com Escape aqui — fecha o modal de upload.
            self.pause(1)
            # Remove só overlays de tour sem fechar o modal Bootstrap.
            if self._overlay_ia_visivel():
                try:
                    self.page.evaluate(
                        """() => {
                          document.querySelectorAll(
                            '.introjs-overlay, .introjs-helperLayer, .introjs-tooltipReferenceLayer, '
                            + '.introjs-tooltip, .shepherd-modal-overlay-container, '
                            + '.shepherd-element, .driver-popover, .driver-overlay'
                          ).forEach(el => el.remove());
                        }"""
                    )
                except Exception:
                    pass
            self._enviar_arquivo_modal_cofre(arquivo)

            if self._aguardar_upload_cofre_concluido(timeout=90):
                return self.driver.current_url

            ultimo_alerta = self._texto_alerta_upload()
            self._fechar_modal_upload_cofre()
            if tentativa == 0:
                self.abrir_cofre_12()

        detalhe = f" Alerta: {ultimo_alerta!r}." if ultimo_alerta else ""
        raise AssertionError(
            "Upload pelo cofre não concluiu após 2 tentativas."
            f"{detalhe} URL: {self.driver.current_url!r}"
        )

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

        self.wait_any_clickable(L.BOTAO_ENVIO_2, L.ASSINAR, timeout=60)

        if self.is_present(L.BOTAO_ENVIO_2, timeout=5):
            try:
                botao_envio = self.page.locator(L.BOTAO_ENVIO_2).first
                if botao_envio.is_visible():
                    self.scroll_into_view(L.BOTAO_ENVIO_2)
                    self.safe_click(L.BOTAO_ENVIO_2, dismiss=False)
                    self.pause(3)
            except Exception:
                pass

        self.dismiss_blocking_modals()
        self.wait_clickable(L.ASSINAR, timeout=90)

    def _aguardar_assinatura_concluida(self, timeout: int = 90) -> None:
        try:
            self.wait_invisible(L.SENHA_CONTA, timeout=30)
        except Exception:
            pass

        self.dismiss_blocking_modals()
        self.wait_any_present(
            L.VIEWBLOB,
            L.VERIFICA_ASSINATURA,
            L.ASSINATURA_CONCLUIDA,
            timeout=timeout,
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

    def _locator_grupo(self) -> str:
        for locator in (L.GRUPO, L.GRUPO_LEGADO):
            if self.is_present(locator, timeout=3):
                return locator
        return L.GRUPO

    def _locator_selecionar_grupo(self) -> str:
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
        self.wait_until(
            lambda: not any(
                termo in (self.page.locator("#lista-assinatura").inner_text() or "").lower()
                for termo in ("carregando", "loading")
            ),
            timeout=30,
            message="Lista de assinatura ainda carregando.",
        )
        self.pause(1)
        self.reload()
        self.enviar_para_assinatura()

    def validar_fase_enviado(self) -> None:
        if self.is_present(L.ASSINAR, timeout=10):
            botao = self.wait_clickable(L.ASSINAR, timeout=30)
            assert botao.is_visible(), "Botão Assinar não visível após envio."
            return
        status = self.get_text(L.FASE_ENVIADO).upper()
        assert "ASSINATURAS" in status or "ENVIADO" in status, (
            f"Documento não está na fase enviado. Status: {status!r}"
        )

    # --- Cenários de erro ---

    def _fechar_modal_ativo(self) -> None:
        for botao in self.page.locator(".modal.in button.close").all():
            if botao.is_visible():
                botao.evaluate("el => el.click()")
                self.pause(1)
                return

    def tentar_enviar_sem_signatario(self) -> None:
        self._aguardar_documento_pronto()
        assert not self._signatario_ja_na_lista(), (
            "Documento já possui signatário; cenário exige lista vazia."
        )
        self.dismiss_blocking_modals()
        self.scroll_into_view(L.BOTAO_ASSINATURA)
        # Popovers de onboarding sobre a viewblob às vezes engolem o 1º clique.
        # Só considera sucesso quando o aviso de "sem signatário" aparece
        # (qualquer .modal.in pode ser tour/IA/outro e gerava falso positivo).
        for _ in range(4):
            self.dismiss_blocking_modals()
            self.js_click(L.BOTAO_ASSINATURA)
            if self.is_visible(L.MODAL_SEM_SIGNATARIO, timeout=12):
                return
            if self.is_present(L.MODAL_ABERTO, timeout=2):
                # Modal errado (ex.: onboarding) — fecha e tenta de novo.
                self._fechar_modal_ativo()
                self.dismiss_blocking_modals()
        raise AssertionError(
            "Aviso de 'pelo menos um signatário' não apareceu após clicar em enviar."
        )

    def validar_aviso_sem_signatario(self) -> None:
        self.wait_visible(L.MODAL_SEM_SIGNATARIO, timeout=30)
        self._fechar_modal_ativo()
        self.dismiss_blocking_modals()

    def adicionar_signatario_com_email(self, email: str) -> None:
        self._aguardar_documento_pronto()
        if not self.is_present(L.CAMPO_EMAIL_SIGNATARIO, timeout=10):
            self._clicar_incluir_email_signatario()
        campo = self.wait_visible(L.CAMPO_EMAIL_SIGNATARIO)
        campo.fill(email)
        self.pause(1)
        for locator in (L.BTN_ADICIONAR_SIGNATARIO, L.BTN_ADICIONAR_SIGNATARIO_ALT):
            if self.is_present(locator, timeout=3):
                self.js_click(locator)
                break
        self.pause(3)
        self._aguardar_barra_progresso()

    def validar_nenhum_signatario_adicionado(self) -> None:
        assert not self._signatario_ja_na_lista(), (
            "Signatário inválido não deveria ter sido adicionado à lista."
        )

    def tentar_assinar_com_senha_incorreta(self) -> None:
        self.incluir_signatario_por_email()
        self.enviar_para_assinatura()
        self._abrir_modal_assinatura()
        self.type_text(L.SENHA_CONTA, "SenhaIncorreta123!")
        self.safe_click(L.SALVAR_ASSINATURA, dismiss=False)

    def validar_senha_invalida(self) -> None:
        self.wait_visible(L.MSG_SENHA_INVALIDA)
        campo = self.page.locator(L.SENHA_CONTA).first
        assert campo.is_visible(), (
            "Modal de assinatura deveria continuar aberto após senha inválida."
        )
        self._fechar_modal_ativo()

    # --- Reaproveitamento ---

    def _elemento_visivel(self, locator: str):
        for elemento in self.page.locator(locator).all():
            if elemento.is_visible():
                return elemento
        return None

    def _confirmar_modal_reaproveitamento(self) -> None:
        self.wait_until(
            lambda: self._elemento_visivel(L.BTN_CONFIRMAR_REAPROVEITAMENTO) is not None,
            timeout=30,
            message="Botão confirmar reaproveitamento não apareceu.",
        )
        botao = self._elemento_visivel(L.BTN_CONFIRMAR_REAPROVEITAMENTO)
        botao.evaluate("el => el.click()")

    def reaproveitar_documento(self) -> str:
        """Reaproveita o documento aberto na viewblob e retorna a URL original."""
        url_original = self.driver.current_url
        self.dismiss_blocking_modals()
        self.scroll_into_view(L.OPCOES_DOCUMENTO)
        self.safe_click(L.OPCOES_DOCUMENTO, dismiss=False)
        menu = self.wait_present(L.MENU_REAPROVEITAR)
        menu.evaluate("el => el.click()")
        self.wait_visible(L.MODAL_REAPROVEITAMENTO)
        self.pause(2)

        if self._elemento_visivel(L.SELECT_COFRE_REAPROVEITAMENTO) is None:
            self._confirmar_modal_reaproveitamento()
            self.pause(2)

        self.wait_until(
            lambda: self._elemento_visivel(L.SELECT_COFRE_REAPROVEITAMENTO) is not None,
            timeout=30,
            message="Select de cofre no reaproveitamento não apareceu.",
        )
        select_cofre = self._elemento_visivel(L.SELECT_COFRE_REAPROVEITAMENTO)
        if not (select_cofre.input_value() or "").strip():
            self.select_by_index(L.SELECT_COFRE_REAPROVEITAMENTO, 1)
        self._confirmar_modal_reaproveitamento()

        # A UI redireciona sozinha para o novo viewblob ~5s após esta mensagem.
        # Fechar o modal antes disso cancela o redirecionamento.
        self.wait_visible(L.MSG_REAPROVEITAMENTO_SUCESSO, timeout=90)
        return url_original

    def validar_documento_reaproveitado(self, url_original: str) -> None:
        def _novo_documento() -> bool:
            url = self.driver.current_url or ""
            if "viewblob" not in url.lower():
                return False
            if url == url_original:
                return False
            # Compara path principal (ignora fragmento/query irrelevante).
            return url.split("#")[0] != url_original.split("#")[0]

        try:
            self.wait_until(_novo_documento, timeout=120)
        except TimeoutError:
            raise TimeoutError(
                "Documento reaproveitado não abriu em nova URL viewblob. "
                f"Original: {url_original!r} | Atual: {self.driver.current_url!r}"
            ) from None
        self.dismiss_blocking_modals()
        self._documento_pronto_para_signatarios()
        self.validar_aguardando_signatarios()

    # --- Substituição de documento ---

    def substituir_documento(self) -> str:
        """Substitui o arquivo do documento aberto na viewblob; retorna a URL."""
        url_documento = self.driver.current_url
        self.dismiss_blocking_modals()
        self.scroll_into_view(L.BTN_SUBSTITUIR_DOC)
        self.safe_click(L.BTN_SUBSTITUIR_DOC, dismiss=False)
        self.wait_present(L.FILE_SUBSTITUIR)
        self.upload_file(L.FILE_SUBSTITUIR, Config.doc_substituto_pdf())
        self.wait_any_present(
            L.MSG_SUBSTITUICAO_SUCESSO,
            L.NOME_DOC_SUBSTITUTO,
            timeout=90,
        )
        return url_documento

    def validar_documento_substituido(self, url_documento: str) -> None:
        try:
            self.wait_invisible(L.MSG_SUBSTITUICAO_SUCESSO, timeout=60)
        except Exception:
            pass

        self.wait_present(L.NOME_DOC_SUBSTITUTO, timeout=90)
        assert self.driver.current_url == url_documento, (
            "A substituição deveria manter o mesmo documento (mesma URL). "
            f"Antes: {url_documento} | Depois: {self.driver.current_url}"
        )
        self.dismiss_blocking_modals()
        self.validar_aguardando_signatarios()

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
        # assinar_documento() já esperou a confirmação (_aguardar_assinatura_concluida);
        # timeout curto aqui é só uma checagem final, não uma espera de negócio.
        assert self.page_contains(L.VERIFICA_ASSINATURA, timeout=10)

    # --- Lote ---

    def _fechar_modal_sucesso_lote(self) -> None:
        for selector in (
            "#sucesso button.close",
            "#sucesso [data-dismiss='modal']",
            "#sucesso .close",
        ):
            for botao in self.page.locator(selector).all():
                if botao.is_visible():
                    try:
                        botao.click(timeout=1000)
                    except Exception:
                        botao.evaluate("el => el.click()")
                    self.pause(1)
                    return

        try:
            self.page.keyboard.press("Escape")
        except Exception:
            pass
        self.pause(1)

    def _lote_foi_processado(self) -> bool:
        if self.is_present(L.TAG_PROCESSADO, timeout=3):
            return True
        linhas = self.page.locator("#contratos tbody tr").all()
        if not linhas:
            return False
        texto = (linhas[0].inner_text() or "").upper()
        return any(
            termo in texto
            for termo in ("PROCESSADO", "PROCESSED", "FINALIZADO", "CONCLUÍDO", "CONCLUIDO")
        )

    def validar_lote_processado(self) -> None:
        assert self._lote_foi_processado(), (
            "Lote não está com status de processamento concluído."
        )

    def _abrir_menu_opcoes_lote(self) -> None:
        self.dismiss_blocking_modals()
        self.wait_visible(L.BTN_OPCAO, timeout=30)
        self.safe_click(L.BTN_OPCAO, dismiss=False)
        self.pause(1)

    def _clicar_opcao_lote(self, *locators: str) -> None:
        for locator in locators:
            if self.is_visible(locator, timeout=5):
                self.safe_click(locator, dismiss=False)
                return
        # Menu pode ter fechado — reabre e tenta o primeiro locator.
        self._abrir_menu_opcoes_lote()
        self.wait_visible(locators[0], timeout=15)
        self.safe_click(locators[0], dismiss=False)

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
        self._abrir_menu_opcoes_lote()
        self._clicar_opcao_lote(L.SELECIONAR_DOC, L.SELECIONAR_DOC_LEGADO)
        self.pause(2)
        loc_upload = (
            L.FILE_UPLOAD_MODAL
            if self.is_present(L.FILE_UPLOAD_MODAL, timeout=5)
            else L.FILE_UPLOAD
        )
        self.upload_file(loc_upload, Config.planilha_lote_xlsx())
        # Mesmo teto de espera do pause(5)+is_present(timeout=5) anterior, mas
        # sem forçar 5s fixos antes de começar a checar (o polling do
        # is_present já cobre o tempo de processamento do upload).
        if self.is_present(L.SUCESSO, timeout=10):
            self._fechar_modal_sucesso_lote()
        self.reload()
        self.pause(2)

        senha_ok = False
        for _ in range(3):
            self.dismiss_blocking_modals()
            self._abrir_menu_opcoes_lote()
            self._clicar_opcao_lote(L.PROCESSAMENTO, L.PROCESSAMENTO_LEGADO)
            self.pause(2)
            if self.is_visible(L.CAMPO_SENHA_LOTE, timeout=20):
                senha_ok = True
                break
            self._fechar_modal_ativo()
            self.dismiss_blocking_modals()
        if not senha_ok:
            raise AssertionError(
                "Campo #senhaConta não apareceu após acionar processamento do lote."
            )

        self.type_text(L.CAMPO_SENHA_LOTE, Config.PASSWORD)
        self.safe_click(L.BTN_FIM, dismiss=False)
        # Mesmo teto do pause(3)+is_present(timeout=30) anterior (33s), mas
        # detecta a tag "processando" assim que ela aparecer, em vez de
        # sempre perder os 3s iniciais dormindo.
        if not self.is_present(L.TAG_PROCESSANDO, timeout=33):
            self.pause(5)

        self._aguardar_lote_processado()

    #Poll com backoff crescente (começa rápido, espaça depois).
    def _aguardar_lote_processado(self, timeout: int = 120) -> None:
       
        '''Teto de 2 minutos: se o lote não processar nesse prazo, o cenário falha
        em vez de ficar minutos no polling. O caso comum (lote pronto em
        poucos ciclos) sai assim que a tag aparecer.'''
      
        deadline = time.time() + timeout
        intervalo = 3.0
        while time.time() < deadline:
            self.reload()
            if self._lote_foi_processado():
                return
            self.pause(intervalo)
            intervalo = min(intervalo * 1.5, 20.0)

        raise AssertionError(f"Lote não foi processado em até {timeout}s.")

    # --- PowerForm ---

    def _selecionar_template_powerform(self, timeout: int = 60) -> None:
        # A lista recarrega por AJAX a cada troca de cofre; no CI isso passa
        # dos 5s que o fluxo legado esperava antes de selecionar pelo índice.
        select = self.wait_visible(L.CAMPO_TEMPLATE)
        try:
            self.wait_until(
                lambda: select.evaluate(
                    "(el, alvo) => [...el.options].some(o => o.text.trim() === alvo)",
                    TEMPLATE_PF_LABEL,
                ),
                timeout=timeout,
            )
            select.select_option(label=TEMPLATE_PF_LABEL, timeout=10000)
        except Exception:
            self.select_by_index(L.CAMPO_TEMPLATE, TEMPLATE_PF_INDEX)

    def _avancar_etapa_powerform(self, timeout: int = 60) -> None:
        try:
            botao = self.wait_clickable(L.BOTAO_CONTINUAR_VISIVEL, timeout=timeout, retries=1)
            botao.click(timeout=5000)
        except Exception:
            # Em headless o rodapé do modal às vezes nunca é exibido; o onclick
            # do botão (moveToStep) funciona mesmo com o elemento oculto.
            self.wait_present(L.BOTAO_CONTINUAR).evaluate("el => el.click()")

    def preparar_powerform(self) -> None:
        self.dismiss_blocking_modals()
        self.safe_click(L.CLM)
        self.safe_click(L.POWERFORM)
        self.wait_visible(L.CRIAR_POWERFORM)
        self.safe_click(L.CRIAR_POWERFORM, dismiss=False)
        self.wait_present(L.MODAL_POWERFORM)
        self.select_by_index(L.CAMPO_COFRE_PF, COFRE_PF_INDEX)
        self.pause(5)
        self._selecionar_template_powerform()
        self.type_text(L.NOME_DOCUMENTO, "PowerForm - Automação")
        self.wait_visible(L.NOME_DOCUMENTO).press("Tab")
        self._avancar_etapa_powerform()
        self.wait_visible(L.BTN_TOKEN)
        self.safe_click(L.BTN_TOKEN, dismiss=False)
        self.pause(2)
        self.type_text(L.CAMPO_EMAIL_PF, Config.USERNAME)
        self.wait_visible(L.CAMPO_EMAIL_PF).press("Tab")
        self.safe_click(L.BTN_EMAIL, dismiss=False)
        self.safe_click(L.BTN_SALVAR_PF, dismiss=False)
        self.pause(5)
        self.safe_click(L.BTN_SEND, dismiss=False)
        self.wait_visible(L.BTN_SALVAR_POWER)
        self.safe_click(L.BTN_SALVAR_POWER, dismiss=False)
        self.wait_invisible(L.BTN_SALVAR_POWER)

    # --- Pin / canvas ---

    def _aguardar_canvas_documento(
        self, timeout: int = 90, timeout_canvas2: int = 30
    ) -> None:
        self.dismiss_blocking_modals()
        if self.is_present(L.CARREGANDO_DOCUMENTO, timeout=2):
            try:
                self.wait_invisible(L.CARREGANDO_DOCUMENTO, timeout=timeout)
            except Exception:
                pass

        self.wait_present(L.CANVAS_1, timeout=timeout)
        try:
            self.wait_present(L.CANVAS_2, timeout=timeout_canvas2)
        except Exception:
            pass

        self.scroll_into_view(L.CANVAS_1)
        self.pause(1)

    def _aguardar_anexo_carregado(self, timeout: int = 120) -> None:
        if self.is_present(L.CARREGANDO_ANEXO, timeout=10):
            try:
                self.wait_invisible(L.CARREGANDO_ANEXO, timeout=timeout)
            except Exception:
                pass

        self.wait_present(L.CANVAS_3, timeout=timeout)
        try:
            self.wait_present(L.CANVAS_4, timeout=timeout)
        except Exception:
            pass

        self.wait_present(L.DOCS_CARREGADOS)
        self.wait_present(L.ADD_ANEXO)

    def enviar_documento_e_validar_canvas(self) -> str:
        self.enviar_documento_pelo_cofre()
        if self.is_present(L.CARREGANDO_DOCUMENTO, timeout=10):
            try:
                self.wait_invisible(L.CARREGANDO_DOCUMENTO, timeout=90)
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
        pin = self.wait_present(L.PIN_1).first
        pin.evaluate(
            "el => el.scrollIntoView({block: 'center', inline: 'center'})"
        )
        self.pause(1)
        try:
            pin.click()
        except Exception:
            pin.evaluate("el => el.click()")
        self.pause(1)

    def _clicar_botao_pin(self, locator: str) -> None:
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
        self.dismiss_blocking_modals()
        self._aguardar_canvas_documento()
        self._clicar_canvas_para_adicionar_pin()
        self._aguardar_pin_canvas1()
        self.pause(2)
        self._replicar_pin_em_todas_paginas()
        self.pause(3)
        # Timeout explícito: antes dependia do default de page_contains() cair
        # no timeout de negócio (60s); agora page_contains() é fail-fast
        # por padrão, então cada replicação de pin precisa do próprio prazo.
        for pin in (L.PIN_1, L.PIN_2, L.PIN_3, L.PIN_4):
            assert self.page_contains(pin, timeout=15), f"Pin não replicado: {pin}"
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
        if not self.is_present(L.CANVAS_1, timeout=1):
            self._aguardar_canvas_documento()

        if self._signatario_ja_na_lista():
            self._aguardar_barra_progresso()
            return

        self._clicar_incluir_email_signatario()
        try:
            self._aguardar_signatario_na_lista(timeout=8)
        except TimeoutError:
            if self.is_present(L.CAMPO_EMAIL_SIGNATARIO, timeout=10):
                self._adicionar_email_signatario()
            elif not self._signatario_ja_na_lista():
                raise AssertionError(
                    "Não foi possível habilitar signatário para adicionar pin no canvas."
                )

        self._aguardar_signatario_na_lista()
        self._aguardar_barra_progresso()

    def _pin_ficou_visivel(self, timeout_ms: int) -> bool:
        try:
            self._first(L.PIN_1).wait_for(state="visible", timeout=timeout_ms)
            return True
        except Exception:
            return False

    def _aguardar_pin_canvas1(self, timeout: int = 60) -> None:
        if self._pin_ficou_visivel(timeout * 1000):
            return
        raise TimeoutError("Pin no canvas1 não apareceu.")

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
        self.scroll_into_view(L.CANVAS_1)

        canvas = self.wait_visible(L.CANVAS_1)
        if not canvas.is_enabled():
            raise AssertionError("Canvas do documento não está habilitado para clique.")

        for offset_x, offset_y in ((150, 150), (200, 400), (300, 600), (100, 100)):
            self._clicar_canvas_posicao(offset_x, offset_y)
            if self._pin_ficou_visivel(1500):
                return
            try:
                self.click_at_coordinates(L.CANVAS_1, offset_x, offset_y)
            except Exception:
                pass
            if self._pin_ficou_visivel(1500):
                return

    TIPOS_PIN = {"assinatura": "0", "rubrica": "1", "selo": "2"}

    def _valor_tipo_pin(self, tipo: str) -> str:
        valor = self.TIPOS_PIN.get(tipo.strip().lower())
        if valor is None:
            raise AssertionError(f"Tipo de pin desconhecido: {tipo!r}")
        return valor

    def alterar_tipo_pin(self, tipo: str) -> None:
        valor = self._valor_tipo_pin(tipo)
        self._clicar_botao_pin(L.BTN_TIPO_PIN)
        opcao = (
            "#pin-container-overlay-canvas1 .custom-select-options "
            f"li[data-value='{valor}']"
        )
        self.wait_visible(opcao)
        try:
            self.wait_clickable(opcao, timeout=10).click()
        except Exception:
            self.js_click(opcao)
        self.pause(2)

    def validar_tipo_pin(self, tipo: str) -> None:
        valor = self._valor_tipo_pin(tipo)
        self.wait_until(
            lambda: self.page.locator(L.PIN_ELEMENTO).first.get_attribute("data-type")
            == valor,
            timeout=30,
            message=f"Pin não mudou para o tipo {tipo!r}.",
        )

    def enviar_e_adicionar_pin_no_canvas(self) -> None:
        self.enviar_documento_pelo_cofre()
        self._aguardar_canvas_documento(timeout_canvas2=3)
        self.incluir_email_para_pin()
        self._clicar_canvas_para_adicionar_pin()
        if not self._pin_ficou_visivel(300):
            self._aguardar_pin_canvas1(timeout=10)
