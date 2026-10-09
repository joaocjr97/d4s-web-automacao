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
        self._tracing_ativo = False

    def is_connected(self) -> bool:
        """False se o processo do navegador crashou/morreu no meio do cenário.

        Chamadas de evidência (screenshot, trace) contra um browser já
        desconectado podem ficar penduradas esperando resposta que nunca
        chega; checar isso antes evita a suíte travar indefinidamente.
        """
        try:
            return self._browser.is_connected()
        except Exception:
            return False

    @property
    def current_url(self) -> str:
        # page.url é cache; após navegação feita pela própria página, preferir
        # location.href (força um round-trip no protocolo Sync).
        try:
            return self.page.evaluate("() => window.location.href")
        except Exception:
            return self.page.url

    def save_screenshot(self, path: str) -> bool:
        self.page.screenshot(path=path, full_page=True)
        return True

    def clear_cookies(self) -> None:
        self._context.clear_cookies()

    def get_storage_state(self) -> dict:
        """Cookies + localStorage da sessão atual (usado p/ reaproveitar login)."""
        return self._context.storage_state()

    def start_tracing(self) -> None:
        """Liga o tracing do Playwright uma única vez por contexto (BrowserContext).

        Cenários usam start_trace_chunk/stop_trace_chunk pra ter um .zip por
        cenário, mesmo quando o mesmo contexto é reaproveitado (@login/@signature).
        """
        if self._tracing_ativo:
            return
        self._context.tracing.start(screenshots=True, snapshots=True, sources=True)
        self._tracing_ativo = True

    def start_trace_chunk(self, name: str) -> None:
        if not self._tracing_ativo:
            return
        self._context.tracing.start_chunk(name=name)

    def stop_trace_chunk(self, path: str | None = None) -> None:
        if not self._tracing_ativo:
            return
        self._context.tracing.stop_chunk(path=path)

    def quit(self) -> None:
        def _parar_tracing() -> None:
            if self._tracing_ativo:
                self._context.tracing.stop()
                self._tracing_ativo = False

        # Se o navegador já crashou, tracing.stop()/context.close() ficam
        # pendurados esperando resposta de um processo morto: pula os dois
        # e vai direto pro close/stop, que toleram um alvo já desconectado.
        closers = (
            (_parar_tracing, self._context.close, self._browser.close, self._playwright.stop)
            if self.is_connected()
            else (self._browser.close, self._playwright.stop)
        )
        for closer in closers:
            try:
                closer()
            except Exception:
                pass


def create_driver(
    config: type[Config] = Config, storage_state: dict | None = None
) -> BrowserDriver:
    """Cria uma sessão Playwright Sync.

    Não chame de novo enquanto outra sessão estiver ativa no mesmo thread:
    o loop asyncio interno permanece rodando e a 2ª chamada falha com
    "Sync API inside the asyncio loop". A sessão deve viver em
    ``context.pw`` (nível feature) e ser fechada com ``quit()``.

    ``storage_state``: cookies/localStorage de um login anterior (ver
    ``features/environment.py``). Evita repetir o login completo via UI
    (navegar + preencher formulário + submeter) em toda ``.feature`` que não
    testa o próprio login — o cenário só precisa confirmar que já está
    logado (``ja_esta_logado``) e, se a sessão tiver expirado, cai no login
    normal como fallback.
    """
    playwright = sync_playwright().start()
    browser_name = (config.BROWSER or "chrome").lower()
    headless = bool(config.HEADLESS)
    launch_args = [
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-extensions",
        "--disable-popup-blocking",
        f"--window-size={VIEWPORT['width']},{VIEWPORT['height']}",
    ]
    if headless:
        # Só desliga a GPU no headless (CI/containers sem driver de vídeo).
        # Em modo headed isso força renderização por software: o embed
        # desenha cada página do documento num <canvas>, e sem GPU isso
        # fica lento e instável (trava minutos e o canvas nem termina
        # de pintar, o que também derruba a contagem de anexos).
        launch_args.append("--disable-gpu")
    else:
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
    if storage_state:
        context_kwargs["storage_state"] = storage_state

    context = browser.new_context(**context_kwargs)
    # Timeout padrão de ações nativas do Playwright (click/fill/etc. sem
    # timeout explícito) — não usar TIMEOUT (60s) aqui: isso faria
    # qualquer ação que falhe silenciosamente esperar minutos antes de
    # reportar erro. Esperas de negócio usam TIMEOUT via wait_visible/wait_until.
    context.set_default_timeout((config.ACTION_TIMEOUT or 30) * 1000)
    # set_default_timeout também vale para page.goto. O desk é pesado e,
    # num navegador recém-aberto, passa de 30s até o domcontentloaded.
    # Navegação fica no TIMEOUT de negócio; clique/fill continuam em 30s.
    context.set_default_navigation_timeout((config.TIMEOUT or 60) * 1000)
    page = context.new_page()
    driver = BrowserDriver(playwright, browser, context, page)
    if config.RECORD_TRACE:
        try:
            driver.start_tracing()
        except Exception:
            pass
    return driver
