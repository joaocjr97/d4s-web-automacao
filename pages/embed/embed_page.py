import time

from playwright.sync_api import Frame

from pages.base_page import BasePage
from pages.embed import embed_locators as L
from recursos.utils.config import Config


class EmbedPage(BasePage):
    """Abre o embed D4Sign no Tryit do W3Schools e inspeciona os canvas."""

    def abrir_tryit(self) -> None:
        self.open(Config.TRYIT_URL)
        self._aceitar_cookies()
        self.wait_until(
            lambda: self.is_present(L.TEXTAREA_CODE, timeout=1)
            or self.is_present(L.EDITOR_CODEMIRROR, timeout=1)
            or self._tem_submit_tryit(),
            timeout=60,
            message="Editor Tryit do W3Schools não carregou.",
        )
        self.pause(1)

    def _tem_submit_tryit(self) -> bool:
        try:
            return bool(self.page.evaluate("() => typeof submitTryit === 'function'"))
        except Exception:
            return False

    def _aceitar_cookies(self) -> None:
        for seletor in (
            "#accept-choices",
            "#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll",
            "#onetrust-accept-btn-handler",
            "button:has-text('Accept all')",
            "button:has-text('Accept All')",
            "button:has-text('Allow all')",
            "button:has-text('Aceitar')",
        ):
            if self._clicar_se_visivel(seletor):
                self.pause(0.5)
                return
        try:
            cookie_frame = self.page.frame_locator(
                "iframe[id*='CybotCookiebot'], iframe[title*='Cookie']"
            )
            botao = cookie_frame.locator(
                "#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll, "
                "button:has-text('Allow all'), button:has-text('Accept')"
            ).first
            if botao.is_visible(timeout=2000):
                botao.click(timeout=3000)
        except Exception:
            pass

    def montar_e_executar_embed(self) -> None:
        Config.exigir_documento_embed()
        html = self._html_embed()
        self.page.evaluate(
            """(code) => {
                const ta = document.getElementById('textareaCode');
                if (ta) ta.value = code;
                if (window.editor) {
                    if (typeof window.editor.setValue === 'function') {
                        window.editor.setValue(code);
                    } else if (window.editor.getDoc) {
                        window.editor.getDoc().setValue(code);
                    }
                }
            }""",
            html,
        )
        self.pause(0.5)
        if self.is_visible(L.BTN_RUN, timeout=3):
            try:
                self._first(L.BTN_RUN).click(timeout=5000)
            except Exception:
                self.page.evaluate("() => { if (typeof submitTryit === 'function') submitTryit(1); }")
        else:
            self.page.evaluate("() => { if (typeof submitTryit === 'function') submitTryit(1); }")
        try:
            self.page.locator(L.IFRAME_RESULTADO).first.wait_for(
                state="attached", timeout=30000
            )
        except Exception:
            pass
        self._aguardar_iframe_d4sign()

    def _html_embed(self) -> str:
        uuid_doc = Config.EMBED_DOCUMENT_UUID
        email = Config.EMAIL_TESTE or Config.USERNAME
        display_name = Config.EMBED_DISPLAY_NAME
        documentation = Config.EMBED_DOCUMENTATION
        key_signer = Config.EMBED_KEY_SIGNER
        host = Config.embed_viewblob_host()
        return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>D4Sign Embed</title>
<style>
  html, body {{ margin: 0; padding: 0; height: 100%; background: #fff; }}
  #signature-div {{ width: 100%; min-height: 900px; }}
</style>
</head>
<body>
<div id="signature-div"></div>
<script>
    var key = {uuid_doc!r};
    var signer_disable_preview = "0";
    var signer_email = {email!r};
    var signer_display_name = {display_name!r};
    var signer_documentation = {documentation!r};
    var signer_birthday = "";
    var signer_key_signer = {key_signer!r};
    var host = {host!r};
    var container = "signature-div";
    var width = "100%";
    var height = "900";

    iframe = document.createElement("iframe");
    var src = host + "/" + key
        + "?email=" + encodeURIComponent(signer_email)
        + "&display_name=" + encodeURIComponent(signer_display_name)
        + "&documentation=" + encodeURIComponent(signer_documentation)
        + "&birthday=" + encodeURIComponent(signer_birthday)
        + "&disable_preview=" + signer_disable_preview;
    if (signer_key_signer) {{
        src += "&key_signer=" + encodeURIComponent(signer_key_signer);
    }}
    iframe.setAttribute("src", src);
    iframe.setAttribute("id", "d4signIframe");
    iframe.setAttribute("width", width);
    iframe.setAttribute("height", height);
    iframe.style.border = "0";
    iframe.style.minHeight = "900px";
    iframe.setAttribute("allow", "geolocation");
    document.getElementById(container).appendChild(iframe);
</script>
</body>
</html>
"""

    def _aguardar_iframe_d4sign(self, timeout: int | None = None) -> Frame:
        limite = timeout or self.timeout

        def achou() -> bool:
            return self._frame_embed() is not None

        self.wait_until(
            achou,
            timeout=limite,
            message="Iframe do embed D4Sign (viewblob) não carregou no Tryit.",
        )
        frame = self._frame_embed()
        if frame is None:
            raise TimeoutError("Iframe do embed D4Sign não encontrado.")
        return frame

    def _frame_embed(self) -> Frame | None:
        for frame in self.page.frames:
            url = (frame.url or "").lower()
            if "embed/viewblob" in url or "d4sign.com.br/embed" in url:
                return frame
        try:
            loc = self.page.frame_locator(L.IFRAME_RESULTADO).locator(L.IFRAME_D4SIGN)
            if loc.count() > 0:
                handle = loc.first.element_handle()
                if handle is not None:
                    content = handle.content_frame()
                    if content is not None:
                        return content
        except Exception:
            pass
        return None

    def viewblob_esta_visivel(self, timeout: int | None = None) -> bool:
        frame = self._aguardar_iframe_d4sign(timeout=timeout)
        limite = timeout or min(self.timeout, 120)
        try:
            frame.locator(f"{L.VIEWBLOB}, {L.CANVAS_1}, {L.CANVAS}").first.wait_for(
                state="attached", timeout=limite * 1000
            )
            return True
        except Exception:
            return False

    def _ids_canvas(self, frame: Frame) -> list[str]:
        try:
            ids = frame.locator(L.CANVAS).evaluate_all(
                "els => els.map(el => el.id).filter(Boolean)"
            )
            return [str(item) for item in ids]
        except Exception:
            return []

    def _rolar_para_carregar_canvas(self, frame: Frame) -> None:
        try:
            canvases = frame.locator(L.CANVAS)
            if canvases.count() > 0:
                canvases.last.scroll_into_view_if_needed(timeout=5000)
        except Exception:
            pass
        try:
            frame.evaluate(
                """() => {
                    const alvos = [
                        document.scrollingElement,
                        document.documentElement,
                        document.body,
                        document.getElementById('viewblobdiv'),
                        document.getElementById('doc-div-principal'),
                    ].filter(Boolean);
                    alvos.forEach(el => {
                        try { el.scrollBy(0, Math.max(el.clientHeight || 600, 600)); }
                        catch (e) {}
                    });
                    window.scrollBy(0, 800);
                }"""
            )
        except Exception:
            pass

    def contar_anexos_por_canvas(self, timeout: int | None = None) -> int:
        """Conta anexos pelos canvas no iframe (canvas1 = principal)."""
        frame = self._aguardar_iframe_d4sign(timeout=timeout)
        limite = timeout or self.timeout
        frame.locator(f"{L.CANVAS_1}, {L.CANVAS}").first.wait_for(
            state="attached", timeout=limite * 1000
        )
        self._aguardar_carregamento(frame)

        esperado = 1 + int(Config.EMBED_ANEXOS_ESPERADOS)
        ids: list[str] = []
        fim = time.time() + limite
        while time.time() < fim:
            ids = self._ids_canvas(frame)
            unicos = sorted(set(ids), key=lambda x: x)
            if len(unicos) >= esperado:
                break
            self._rolar_para_carregar_canvas(frame)
            self.pause(1)

        ids = sorted(set(self._ids_canvas(frame)))
        tem_principal = "canvas1" in ids or bool(ids)
        anexos = max(0, len(ids) - (1 if tem_principal else 0))
        return anexos

    def _aguardar_carregamento(self, frame: Frame) -> None:
        try:
            loader = frame.locator(L.CARREGANDO_DOCUMENTO_CSS).or_(
                frame.locator(L.CARREGANDO_DOCUMENTO_XPATH)
            ).first
            if loader.is_visible(timeout=3000):
                loader.wait_for(state="hidden", timeout=min(self.timeout, 90) * 1000)
        except Exception:
            pass
        self.pause(2)

    def ids_canvas_encontrados(self) -> list[str]:
        frame = self._frame_embed()
        if frame is None:
            return []
        return sorted(set(self._ids_canvas(frame)))
