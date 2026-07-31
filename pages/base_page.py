import time

from playwright.sync_api import Locator, Page, expect

from recursos.utils.config import Config


class BasePage:
    FORM_UPLOAD = "#formUpload"

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
        last_error: Exception | None = None
        for _ in range(retries):
            try:
                loc = self._first(locator)
                loc.wait_for(state="visible", timeout=(timeout or self.timeout) * 1000)
                expect(loc).to_be_enabled(timeout=(timeout or self.timeout) * 1000)
                return loc
            except Exception as exc:
                last_error = exc
                self.pause(0.5)
        if last_error:
            raise last_error
        raise TimeoutError(f"Elemento não ficou clicável: {locator}")

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
        self.wait_present(locator).set_input_files(file_path)

    def is_visible(self, locator: str, timeout: int | None = None) -> bool:
        try:
            self.wait_visible(locator, timeout=timeout or self.timeout)
            return True
        except Exception:
            return False

    def is_present(self, locator: str, timeout: int = 3) -> bool:
        try:
            self._first(locator).wait_for(state="attached", timeout=timeout * 1000)
            return True
        except Exception:
            return False

    def page_contains(self, locator: str, timeout: int | None = None) -> bool:
        return self.is_present(locator, timeout=timeout or self.timeout)

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
        time.sleep(seconds)

    def get_text(self, locator: str) -> str:
        return (self.wait_visible(locator).inner_text() or "").strip()

    def dismiss_blocking_modals(self) -> None:
        """Fecha modais de aviso/IA sem destruir modais de upload em aberto."""
        for selector in (
            "#modal-aviso-analizer .close",
            "#modal-aviso-analizer button[data-dismiss='modal']",
            "#modal-aviso-analizer button.close",
        ):
            try:
                for el in self.page.locator(selector).all():
                    try:
                        if not el.is_visible():
                            continue
                        el.click(timeout=1000)
                    except Exception:
                        try:
                            el.evaluate("node => node.click()")
                        except Exception:
                            pass
            except Exception:
                pass

        upload_aberto = self.is_present(self.FORM_UPLOAD, timeout=1)
        if not upload_aberto:
            try:
                for el in self.page.locator(".modal-backdrop.in").all():
                    try:
                        if not el.is_visible():
                            continue
                        el.click(timeout=1000)
                    except Exception:
                        try:
                            el.evaluate("node => node.click()")
                        except Exception:
                            pass
            except Exception:
                pass

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
