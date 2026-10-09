import re

from pages.base_page import BasePage
from pages.cofres import cofre_locators as L
from recursos.utils.config import Config


class CofrePage(BasePage):
    """Consulta de cofre existente: pesquisa, abertura e contagem de documentos."""

    def ir_para_desk(self) -> None:
        """Vai para a desk inicial (lista de cofres), só se ainda não estiver nela."""
        url = (self.driver.current_url or "").lower()
        if "/desk" not in url or "/desk/cofres/" in url:
            self.open(Config.desk_url())
            self.pause(1)
        self.dismiss_blocking_modals()
        self.wait_visible(L.CAMPO_BUSCA_COFRE, timeout=30)

    def garantir_desk(self) -> None:
        self.ir_para_desk()

    def _locator_visivel(self, locator: str) -> bool:
        try:
            return bool(self.page.locator(locator).first.is_visible())
        except Exception:
            return False

    def _filtrar_sidebar(self, termo: str, voltar_desk: bool = False) -> None:
        """Filtra a lista da esquerda. Não recarrega a desk se já estiver no cofre/pasta."""
        if voltar_desk:
            self.ir_para_desk()
        else:
            self.dismiss_blocking_modals()
            if not self._locator_visivel(L.CAMPO_BUSCA_COFRE):
                self.ir_para_desk()
        campo = self.wait_visible(L.CAMPO_BUSCA_COFRE)
        campo.fill(termo)
        campo.press("Enter")
        self.pause(0.6)

    def _eh_cofre_compartilhado_automacao(self, nome: str) -> bool:
        n = nome.strip().lower()
        return "automação compartilhado" in n or "automacao compartilhado" in n

    def _alvos_link_cofre(self, nome: str) -> list[str]:
        alvos = [L.link_cofre_por_nome(nome), L.link_cofre_contendo_nome(nome)]
        if nome.strip() == "12":
            alvos.insert(0, L.COFRE_AUTOMACAO)
        if self._eh_cofre_compartilhado_automacao(nome):
            alvos.insert(0, L.LINK_COFRE_AUTOMACAO_COMPARTILHADO)
            alvos.insert(0, L.COFRE_AUTOMACAO_COMPARTILHADO)
        return alvos

    def _alvo_cofre(self, nome: str) -> str:
        alvos = self._alvos_link_cofre(nome)
        for alvo in alvos:
            if self._locator_visivel(alvo):
                return alvo
        return alvos[0]

    def pesquisar_cofre(self, nome: str) -> None:
        self._filtrar_sidebar(nome, voltar_desk=True)
        alvos = self._alvos_link_cofre(nome)
        if not any(self._locator_visivel(alvo) for alvo in alvos):
            if self._locator_visivel(L.CARREGAR_MAIS_COFRES):
                self._clicar_link_consulta(L.CARREGAR_MAIS_COFRES)
                self.pause(1)
                campo = self.wait_visible(L.CAMPO_BUSCA_COFRE)
                campo.fill(nome)
                campo.press("Enter")
                self.pause(0.6)
        self.wait_any_present(*alvos, timeout=30)

    def _popup_cofre_visivel(self) -> bool:
        for locator in (
            L.MODAL_BACKDROP,
            L.MODAL_ABERTO,
            "#modal-aviso-analizer",
            ".sweet-alert",
            ".swal2-container",
            ".introjs-overlay",
            ".introjs-tooltip",
        ):
            try:
                if self.page.locator(locator).first.is_visible():
                    return True
            except Exception:
                continue
        return False

    def _clicar_backdrop_popup(self) -> bool:
        loc = self.page.locator(L.MODAL_BACKDROP).first
        try:
            loc.wait_for(state="visible", timeout=1500)
            loc.click(timeout=2000, force=True)
            return True
        except Exception:
            return self._clicar_se_visivel(L.MODAL_BACKDROP)

    def _fechar_popup_apos_abrir_cofre(self, aguardar: bool = True) -> None:
        """Fecha o popup que surge ao abrir o cofre compartilhado, sem espera longa."""
        if aguardar:
            for _ in range(8):
                if self._popup_cofre_visivel():
                    break
                self.pause(0.2)
            else:
                self.dismiss_blocking_modals()
                return

        for _ in range(8):
            self.dismiss_blocking_modals()
            if not self._popup_cofre_visivel():
                return
            fechou = (
                self._clicar_se_visivel(L.BTN_CONFIRMAR_POPUP_COFRE)
                or self._clicar_se_visivel(L.BTN_FECHAR_POPUP_COFRE)
                or self._clicar_backdrop_popup()
            )
            if not fechou:
                try:
                    self.page.keyboard.press("Escape")
                except Exception:
                    pass
            self.pause(0.4)
        self.dismiss_blocking_modals()

    def abrir_cofre_pesquisado(self, nome: str) -> None:
        alvo = self._alvo_cofre(nome)
        self._clicar_link_consulta(alvo)
        self.wait_url_contains("/desk/cofres/", timeout=30)
        if self._eh_cofre_compartilhado_automacao(nome):
            self._fechar_popup_apos_abrir_cofre(aguardar=True)
        else:
            self.dismiss_blocking_modals()
        self.wait_visible(L.TABELA_DOCUMENTOS, timeout=60)
        if self._eh_cofre_compartilhado_automacao(nome):
            self._fechar_popup_apos_abrir_cofre(aguardar=False)
        else:
            self.dismiss_blocking_modals()
        self.wait_any_present(L.OPCOES_COFRE, L.LINHAS_DOCUMENTO, timeout=30)

    def pesquisar_e_abrir_cofre(self, nome: str) -> None:
        self.pesquisar_cofre(nome)
        self.abrir_cofre_pesquisado(nome)

    def _url_tem_pasta_aberta(self) -> bool:
        url = (self.driver.current_url or "").lower()
        if "/desk/cofres/" not in url:
            return False
        caminho = url.split("/desk/cofres/")[-1].split(".html")[0]
        return len([parte for parte in caminho.split("/") if parte]) >= 3

    def _clicar_link_consulta(self, locator: str) -> None:
        """Clica bypassando overlay: popup de onboarding intercepta wait_clickable (TIMEOUT alto)."""
        for _ in range(3):
            self.dismiss_blocking_modals()
            self.scroll_into_view(locator)
            try:
                self.js_click(locator)
                return
            except Exception:
                self.pause(0.5)
        self.safe_click(locator, dismiss=True)

    def pesquisar_pasta(self, nome: str) -> None:
        """Filtra a sidebar pelo nome da pasta, sem voltar para a desk nem abrir o item."""
        self._filtrar_sidebar(nome, voltar_desk=False)
        if self._locator_visivel(L.link_pasta_por_nome(nome)):
            return
        if self._locator_visivel(L.CARREGAR_MAIS_COFRES):
            self._clicar_link_consulta(L.CARREGAR_MAIS_COFRES)
            self.pause(1)
            campo = self.wait_visible(L.CAMPO_BUSCA_COFRE)
            campo.fill(nome)
            campo.press("Enter")
            self.pause(0.6)
        if self._locator_visivel(L.link_pasta_por_nome(nome)):
            return
        try:
            chevrons = self.page.locator(L.CHEVRON_PASTAS)
            limite = min(chevrons.count(), 15)
            for i in range(limite):
                if self._locator_visivel(L.link_pasta_por_nome(nome)):
                    return
                try:
                    chevrons.nth(i).evaluate("el => el.click()")
                    self.pause(0.3)
                except Exception:
                    continue
        except Exception:
            pass
        self.wait_visible(L.link_pasta_por_nome(nome), timeout=30)

    def _eh_pasta_compartilhada_automacao(self, nome: str) -> bool:
        return nome.strip().lower() == "pasta de automação"

    def _alvos_link_pasta(self, nome: str) -> list[str]:
        alvos = [L.link_pasta_por_nome(nome)]
        if nome.strip().lower() == "pasta":
            alvos.insert(0, L.PASTA_AUTOMACAO)
        if self._eh_pasta_compartilhada_automacao(nome):
            alvos.insert(0, L.LINK_PASTA_DE_AUTOMACAO)
            alvos.insert(0, L.PASTA_DE_AUTOMACAO)
        return alvos

    def _alvo_pasta(self, nome: str) -> str:
        alvos = self._alvos_link_pasta(nome)
        for alvo in alvos:
            if self._locator_visivel(alvo):
                return alvo
        return alvos[0]

    def pesquisar_e_abrir_pasta(self, nome: str) -> None:
        self.pesquisar_pasta(nome)
        self.abrir_pasta(nome)

    def garantir_pasta_visivel(self, nome: str) -> None:
        self.dismiss_blocking_modals()
        alvos = self._alvos_link_pasta(nome)
        if any(self._locator_visivel(alvo) for alvo in alvos):
            return
        if self._locator_visivel(L.CHEVRON_PASTAS):
            self._clicar_link_consulta(L.CHEVRON_PASTAS)
            self.pause(0.5)
        self.wait_any_present(*alvos, timeout=30)

    def abrir_pasta(self, nome: str) -> None:
        self.garantir_pasta_visivel(nome)
        alvo = self._alvo_pasta(nome)
        self._clicar_link_consulta(alvo)
        self.wait_until(
            self._url_tem_pasta_aberta,
            timeout=30,
            message="A pasta não abriu (URL sem identificador de pasta).",
        )
        if self._eh_pasta_compartilhada_automacao(nome):
            self._fechar_popup_apos_abrir_cofre(aguardar=True)
        else:
            self.dismiss_blocking_modals()
        self.wait_any_present(
            L.CONTADOR_TOTAL,
            L.INFO_DATATABLES,
            L.TABELA_DOCUMENTOS,
            L.BTN_NOVA_PASTA,
            timeout=30,
        )

    def abrir_pasta_sem_pesquisa(self, nome: str) -> None:
        """Abre a pasta na desk, sem filtrar a sidebar."""
        self.garantir_desk()
        self.abrir_pasta(nome)

    def pasta_esta_aberta(self, nome: str | None = None) -> bool:
        if not self._url_tem_pasta_aberta():
            return False
        if nome:
            ibox = ""
            try:
                ibox = (self.page.locator(".ibox-title").first.inner_text() or "")
            except Exception:
                pass
            if nome in ibox:
                return True
            try:
                titulos = self.page.locator(L.NOME_PASTA)
                for i in range(titulos.count()):
                    texto = (titulos.nth(i).inner_text() or "").strip()
                    if texto == nome:
                        return True
            except Exception:
                pass
            return False
        return True

    def cofre_esta_aberto(self) -> bool:
        url = (self.driver.current_url or "").lower()
        return "/desk/cofres/" in url and self.is_present(L.TABELA_DOCUMENTOS, timeout=10)

    def _inteiro_do_texto(self, texto: str) -> int | None:
        if not texto:
            return None
        compacto = texto.replace(".", "").replace(",", "").replace("\xa0", "")
        digitos = "".join(ch for ch in compacto if ch.isdigit())
        if not digitos:
            return None
        return int(digitos)

    def _total_info_datatables(self, texto: str) -> int | None:
        if not texto:
            return None
        match = re.search(r"(?:de|of)\s+([\d.\s]+)", texto, re.I)
        if match:
            total = self._inteiro_do_texto(match.group(1))
            if total is not None:
                return total
        return self._inteiro_do_texto(texto)

    def contar_documentos(self) -> int:
        """Total de documentos do cofre/pasta (contador da UI, não só a página visível)."""
        self.dismiss_blocking_modals()
        self.wait_any_present(
            L.CONTADOR_TOTAL,
            L.INFO_DATATABLES,
            L.TABELA_DOCUMENTOS,
            timeout=15,
        )
        self.pause(0.3)

        try:
            badges = self.page.locator(L.CONTADOR_TOTAL)
            for i in range(badges.count()):
                el = badges.nth(i)
                try:
                    if not el.is_visible():
                        continue
                except Exception:
                    continue
                total = self._inteiro_do_texto(el.inner_text() or "")
                if total is not None:
                    return total
        except Exception:
            pass

        if self._locator_visivel(L.INFO_DATATABLES):
            total = self._total_info_datatables(
                (self.page.locator(L.INFO_DATATABLES).first.inner_text() or "")
            )
            if total is not None:
                return total

        if self._locator_visivel(L.LINHA_VAZIA):
            return 0
        if not self.is_present(L.TABELA_DOCUMENTOS, timeout=2):
            return 0
        linhas = self.page.locator(L.LINHAS_DOCUMENTO)
        try:
            return max(linhas.count() - self.page.locator(L.LINHA_VAZIA).count(), 0)
        except Exception:
            return 0
