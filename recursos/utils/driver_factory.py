import os

from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from recursos.utils.config import Config

VIEWPORT = {"width": 1920, "height": 1080}


class BrowserDriver:
    """Sessão Playwright exposta como ``context.driver`` nos steps/pages."""

    def __init__(
        self,
        playwright: Playwright,
        browser: Browser,
        context: BrowserContext,
        page: Page,
    ) -> None:
        self._playwright = playwright
        self._browser = browser
        self._context = context
        self.page = page
        self.documento_url: str | None = None

    @property
    def current_url(self) -> str:
        return self.page.url

    def save_screenshot(self, path: str) -> bool:
        self.page.screenshot(path=path)
        return True

    def clear_cookies(self) -> None:
        self._context.clear_cookies()

    def quit(self) -> None:
        for closer in (self._context.close, self._browser.close, self._playwright.stop):
            try:
                closer()
            except Exception:
                pass


def create_driver(config: type[Config] = Config) -> BrowserDriver:
    """Cria uma sessão Playwright Sync.

    Não chame de novo enquanto outra sessão estiver ativa no mesmo thread:
    o loop asyncio interno permanece rodando e a 2ª chamada falha com
    "Sync API inside the asyncio loop". A sessão deve viver em
    ``context.pw`` (nível feature) e ser fechada com ``quit()``.
    """
    playwright = sync_playwright().start()
    browser_name = (config.BROWSER or "chrome").lower()
    headless = bool(config.HEADLESS)
    launch_args = [
        "--disable-gpu",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-extensions",
        "--disable-popup-blocking",
        f"--window-size={VIEWPORT['width']},{VIEWPORT['height']}",
    ]
    if not headless:
        # Evita janela minúscula + viewport emulado (UI “esmagada”).
        launch_args.append("--start-maximized")

    chrome_bin = os.getenv("CHROME_BIN") or os.getenv("CHROME_PATH")

    if browser_name == "firefox":
        browser = playwright.firefox.launch(headless=headless, args=launch_args)
    elif browser_name in ("webkit", "safari"):
        browser = playwright.webkit.launch(headless=headless)
    else:
        launch_kwargs: dict = {"headless": headless, "args": launch_args}
        if chrome_bin:
            launch_kwargs["executable_path"] = chrome_bin
        try:
            browser = playwright.chromium.launch(**launch_kwargs)
        except Exception:
            launch_kwargs["channel"] = "chrome"
            browser = playwright.chromium.launch(**launch_kwargs)

    context_kwargs: dict = {"ignore_https_errors": True}
    if headless:
        context_kwargs["viewport"] = VIEWPORT
    else:
        # Sem emulação: a página usa o tamanho real da janela maximizada.
        context_kwargs["viewport"] = None

    context = browser.new_context(**context_kwargs)
    context.set_default_timeout((config.TIMEOUT or 30) * 1000)
    page = context.new_page()
    return BrowserDriver(playwright, browser, context, page)
