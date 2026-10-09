import time

from playwright.sync_api import Locator, Page, expect

from recursos.utils.config import Config


class BasePage:
    FORM_UPLOAD = "#formUpload"
    # Teto de uma tentativa de wait_clickable quando o chamador não passa timeout.
    # Visível e habilitado dividem esse prazo; as 3 tentativas já existentes continuam.
    CLICK_ATTEMPT_TIMEOUT = 15

    def __init__(self, driver, timeout: int | None = None) -> None:
        # Aceita BrowserDriver (com .page) ou Page direto.
        self.driver = driver
        self.page: Page = getattr(driver, "page", driver)
        self.timeout = timeout or Config.TIMEOUT
        self._timeout_ms = self.timeout * 1000

    def open(self, url: str) -> None:
        self.page.goto(url, wait_until="domcontentloaded")

    def _loc(self, locator: str) -> Locator:
        return self.page.locator(locator)

    def _first(self, locator: str) -> Locator:
        # Equivalente ao find_element do Selenium (primeiro match).
        return self._loc(locator).first

    def wait_visible(self, locator: str, timeout: int | None = None) -> Locator:
        loc = self._first(locator)
        loc.wait_for(state="visible", timeout=(timeout or self.timeout) * 1000)
        return loc

    def wait_clickable(
        self, locator: str, timeout: int | None = None, retries: int = 3
    ) -> Locator:
        """Espera o elemento ficar visível e habilitado.

        Sem timeout, cada tentativa dura no máximo CLICK_ATTEMPT_TIMEOUT
        segundos (as duas checagens dividem o prazo). Timeout explícito
        continua sendo o prazo de cada checagem.
        """
        last_error: Exception | None = None
        for _ in range(retries):
            try:
                loc = self._first(locator)
                if timeout is None:
                    self._aguardar_clicavel(loc, self.CLICK_ATTEMPT_TIMEOUT)
                else:
                    limite_ms = timeout * 1000
                    loc.wait_for(state="visible", timeout=limite_ms)
                    expect(loc).to_be_enabled(timeout=limite_ms)
                return loc
            except Exception as exc:
                last_error = exc
                self.pause(0.5)
        if last_error:
            raise last_error
        raise TimeoutError(f"Elemento não ficou clicável: {locator}")

    def _aguardar_clicavel(self, loc: Locator, limite: float) -> None:
        inicio = time.monotonic()

        def restante_ms() -> int:
            restante = int((limite - (time.monotonic() - inicio)) * 1000)
            if restante <= 0:
                raise TimeoutError(f"Elemento não ficou clicável em {limite:.0f}s.")
            return restante

        loc.wait_for(state="visible", timeout=restante_ms())
        expect(loc).to_be_enabled(timeout=restante_ms())

    def wait_present(self, locator: str, timeout: int | None = None) -> Locator:
        loc = self._first(locator)
        loc.wait_for(state="attached", timeout=(timeout or self.timeout) * 1000)
        return loc

    def wait_invisible(self, locator: str, timeout: int | None = None) -> bool:
        self._first(locator).wait_for(
            state="hidden", timeout=(timeout or self.timeout) * 1000
        )
        return True

    def wait_any_present(self, *locators: str, timeout: int | None = None) -> None:
        deadline = time.time() + (timeout or self.timeout)
        while time.time() < deadline:
            for locator in locators:
                if self.is_present(locator, timeout=0.5):
                    return
            self.pause(0.3)
        raise TimeoutError(f"Nenhum locator presente: {locators}")

    def wait_any_clickable(self, *locators: str, timeout: int | None = None) -> None:
        deadline = time.time() + (timeout or self.timeout)
        while time.time() < deadline:
            for locator in locators:
                try:
                    loc = self._loc(locator).first
                    if loc.is_visible() and loc.is_enabled():
                        return
                except Exception:
                    pass
            self.pause(0.3)
        raise TimeoutError(f"Nenhum locator clicável: {locators}")

    def wait_url_contains(self, text: str, timeout: int | None = None) -> None:
        self.wait_until(
            lambda: text in (self.page.url or ""),
            timeout=timeout,
            message=f"URL não contém {text!r}",
        )

    def wait_until(self, predicate, timeout: int | None = None, message: str = "") -> None:
        deadline = time.time() + (timeout or self.timeout)
        while time.time() < deadline:
            try:
                if predicate():
                    return
            except Exception:
                pass
            self.pause(0.3)
        raise TimeoutError(message or "Condição não satisfeita a tempo.")

    def click(self, locator: str, dismiss: bool = True) -> None:
        self.safe_click(locator, dismiss=dismiss)

    def safe_click(self, locator: str, dismiss: bool = True) -> None:
        if dismiss:
            self.dismiss_blocking_modals()
        element = self.wait_clickable(locator)
        try:
            element.click(timeout=5000)
        except Exception:
            self.js_click(locator)

    def js_click(self, locator: str) -> None:
        self.wait_present(locator).evaluate("el => el.click()")

    def select_by_index(self, locator: str, index: int) -> None:
        loc = self._first(locator)
        try:
            loc.wait_for(state="attached", timeout=self._timeout_ms)
            loc.select_option(index=index, timeout=10000)
        except Exception:
            self.wait_visible(locator).select_option(index=index)

    def type_text(self, locator: str, text: str) -> None:
        loc = self.wait_visible(locator)
        loc.fill(text)

    def upload_file(self, locator: str, file_path: str) -> None:
        loc = self.wait_present(locator)
        loc.set_input_files(file_path)
        # Alguns plugins (ex.: jQuery File Upload da D4Sign) só processam o
        # arquivo depois do change/input — set_input_files às vezes não basta.
        try:
            loc.evaluate(
                """el => {
                    el.dispatchEvent(new Event('input', { bubbles: true }));
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                }"""
            )
        except Exception:
            pass

    # Timeout de "checagem rápida" (existe/está visível agora?), usado quando
    # is_visible/is_present/page_contains são chamados sem timeout explícito.
    # Propositalmente curto: NÃO deve cair no timeout de negócio (self.timeout,
    # 60s), senão uma checagem vira uma espera "escondida" de um minuto
    # sempre que o elemento realmente não existe.
    CHECK_TIMEOUT = 3

    def is_visible(self, locator: str, timeout: int | None = None) -> bool:
        try:
            self.wait_visible(
                locator, timeout=timeout if timeout is not None else self.CHECK_TIMEOUT
            )
            return True
        except Exception:
            return False

    def is_present(self, locator: str, timeout: int | None = None) -> bool:
        limite = timeout if timeout is not None else self.CHECK_TIMEOUT
        try:
            self._first(locator).wait_for(state="attached", timeout=limite * 1000)
            return True
        except Exception:
            return False

    def page_contains(self, locator: str, timeout: int | None = None) -> bool:
        return self.is_present(locator, timeout=timeout if timeout is not None else self.CHECK_TIMEOUT)

    def execute_script(self, script: str, *args) -> None:
        if not args:
            self.page.evaluate(f"() => {{ {script} }}")
            return
        if len(args) == 1 and isinstance(args[0], Locator):
            body = script.replace("arguments[0]", "el")
            args[0].evaluate(f"el => {{ {body} }}")
            return
        self.page.evaluate(
            f"(args) => {{ const arguments = args; {script} }}",
            list(args),
        )

    def evaluate(self, expression: str, arg=None):
        if arg is None:
            return self.page.evaluate(expression)
        return self.page.evaluate(expression, arg)

    def reload(self) -> None:
        self.page.reload(wait_until="domcontentloaded")

    def press_escape(self, locator: str) -> None:
        self.wait_visible(locator).press("Escape")

    def scroll_into_view(self, locator: str) -> None:
        self.wait_present(locator).evaluate(
            "el => el.scrollIntoView({block: 'center'})"
        )

    def click_at_coordinates(self, locator: str, x: int, y: int) -> None:
        """Clique com offset a partir do canto superior esquerdo do elemento."""
        box = self.wait_visible(locator).bounding_box()
        if not box:
            raise TimeoutError(f"Sem bounding box para {locator}")
        self.page.mouse.click(box["x"] + x, box["y"] + y)

    def pause(self, seconds: float) -> None:
        """Espera processando eventos do Playwright.

        ``time.sleep`` congelaria o loop interno da Sync API: propriedades de
        cache como ``page.url`` só se atualizam quando alguma chamada ao
        protocolo roda. Laços de espera que dormem e leem ``page.url`` nunca
        enxergariam uma navegação feita pela própria página.
        """
        try:
            self.page.wait_for_timeout(seconds * 1000)
        except Exception:
            time.sleep(seconds)

    def get_text(self, locator: str) -> str:
        return (self.wait_visible(locator).inner_text() or "").strip()

    def _clicar_se_visivel(self, locator: str) -> bool:
        try:
            for el in self.page.locator(locator).all():
                try:
                    if not el.is_visible():
                        continue
                    try:
                        el.click(timeout=1000)
                    except Exception:
                        el.evaluate("node => node.click()")
                    return True
                except Exception:
                    continue
        except Exception:
            pass
        return False

    def _overlay_ia_visivel(self) -> bool:
        seletores = (
            "xpath=//*[contains(normalize-space(.), 'Inteligência Artificial da D4Sign')]",
            "xpath=//*[contains(@class,'popover') or contains(@class,'introjs-tooltip') "
            "or contains(@class,'shepherd-element') or contains(@class,'driver-popover')]"
            "[.//button or .//a]",
            ".modal.in",
            ".modal.show",
            ".modal-backdrop.in",
            ".modal-backdrop.show",
            ".modal-backdrop",
            ".swal2-container",
            ".sweet-alert",
            ".introjs-overlay",
            ".introjs-tooltip",
        )
        for seletor in seletores:
            try:
                for el in self.page.locator(seletor).all():
                    if el.is_visible():
                        return True
            except Exception:
                continue
        return False

    def _upload_modal_aberto(self) -> bool:
        return self.is_present(self.FORM_UPLOAD, timeout=0.5) or self.is_present(
            "xpath=//div[contains(@class,'modal') and contains(@class,'in')]"
            "[.//*[@id='fileupload' or @id='formUpload']]",
            timeout=0.5,
        )

    def dismiss_blocking_modals(self) -> None:
        """Fecha modais de aviso/IA/onboarding sem destruir modais de upload em aberto."""
        for selector in (
            "#modal-aviso-analizer .close",
            "#modal-aviso-analizer button[data-dismiss='modal']",
            "#modal-aviso-analizer button.close",
        ):
            self._clicar_se_visivel(selector)

        upload_aberto = self._upload_modal_aberto()

        # Fechar popups genéricos (tour, "Entendi", sweet-alert) mesmo sem texto de IA.
        # Sem isso o overlay intercepta o clique e o wait_clickable parece um loop (3 x 15s).
        if not upload_aberto:
            for selector in (
                "xpath=//div[contains(@class,'modal') and "
                "(contains(@class,'in') or contains(@class,'show'))]"
                "//*[self::button or self::a]["
                "contains(@class,'close') or @data-dismiss='modal' "
                "or contains(normalize-space(.), 'Entendi') "
                "or contains(normalize-space(.), 'Got it') "
                "or contains(normalize-space(.), 'Continuar') "
                "or normalize-space(.)='OK' or normalize-space(.)='Ok' "
                "or normalize-space(.)='Fechar' or normalize-space(.)='Close' "
                "or contains(normalize-space(.), 'Pular') "
                "or contains(normalize-space(.), 'Skip')"
                "]",
                ".modal.in button.close",
                ".modal.show button.close",
                ".modal.in [data-dismiss='modal']",
                ".modal.show [data-dismiss='modal']",
                ".sweet-alert button.confirm",
                ".swal2-container .swal2-confirm",
                "xpath=//*[contains(@class,'popover') or contains(@class,'introjs') "
                "or contains(@class,'shepherd') or contains(@class,'driver-popover') "
                "or contains(@class,'onboard')]"
                "//*[self::button or self::a]["
                "contains(@class,'close') or @aria-label='Close' or @aria-label='Fechar' "
                "or contains(normalize-space(.), 'Pular') "
                "or contains(normalize-space(.), 'Skip') "
                "or contains(normalize-space(.), 'Entendi') "
                "or contains(normalize-space(.), '×') "
                "or normalize-space(.)='x' or normalize-space(.)='X'"
                "]",
                "xpath=//button[contains(@class,'introjs-skipbutton') "
                "or contains(@class,'introjs-donebutton') "
                "or contains(@class,'shepherd-cancel-icon')]",
            ):
                if self._clicar_se_visivel(selector):
                    break
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
            try:
                self.page.keyboard.press("Escape")
            except Exception:
                pass
            self._clicar_se_visivel(".modal-backdrop.in")
            self._clicar_se_visivel(".modal-backdrop.show")
            self._clicar_se_visivel(".modal-backdrop")

    def dismiss_modals_if_present(self) -> None:
        """Alias mantido para compatibilidade."""
        self.dismiss_blocking_modals()

    def wait_for_document_loaded(self, loading_locator: str, canvas_locator: str) -> None:
        if self.is_present(loading_locator, timeout=10):
            try:
                self.wait_invisible(loading_locator)
            except Exception:
                pass
        self.wait_visible(canvas_locator)
