import os
from pathlib import Path

from dotenv import load_dotenv


class Config:
    _loaded = False
    # Cookies/localStorage do último login bem-sucedido nesta execução do
    # Behave. Fica na classe (não em features/environment.py) porque o Behave
    # carrega environment.py via exec(), não via import — um módulo "normal"
    # importado de dois lugares (hooks e steps) viraria duas cópias
    # desconectadas. Config já é importado normalmente em todo o projeto,
    # então é a forma segura de compartilhar esse estado entre
    # features/environment.py e features/steps/common/auth_steps.py.
    _login_storage_state: dict | None = None

    ENVIRONMENT: str = "prod"
    USERNAME: str = ""
    PASSWORD: str = ""
    TOKEN_API: str = ""
    CRYPT_KEY: str = ""
    EMAIL_TESTE: str = ""
    EMBED_DOCUMENT_UUID: str = ""
    EMBED_KEY_SIGNER: str = ""
    EMBED_DISPLAY_NAME: str = ""
    EMBED_DOCUMENTATION: str = ""
    EMBED_ANEXOS_ESPERADOS: int = 3
    TRYIT_URL: str = "https://www.w3schools.com/js/tryit.asp?filename=tryjs_editor"
    BROWSER: str = "chrome"
    HEADLESS: bool = False
    TIMEOUT: int = 60
    # Timeout padrão nativo do Playwright (context.set_default_timeout): cobre
    # ações como click/fill/select_option quando chamadas sem timeout explícito.
    # Não cobre navegação (page.goto): essa usa TIMEOUT via
    # set_default_navigation_timeout.
    # Propositalmente bem menor que TIMEOUT: esperar uma ação de UI ficar
    # "acionável" (visível/estável/habilitada) deveria levar segundos, não
    # minutos. Esperas de negócio (documento processar, lote finalizar) usam
    # TIMEOUT explicitamente via wait_visible/wait_until, não este valor.
    ACTION_TIMEOUT: int = 30
    LOGIN_TIMEOUT: int = 20
    SCREENSHOT_ON_FAIL: bool = True
    RECORD_VIDEO: bool = True
    RECORD_TRACE: bool = True
    EVIDENCE_ALWAYS: bool = False

    URLS = {
        "homol": "https://homol.d4sign.com.br/",
        "staging": "https://stage.d4sign.com.br/",
        "stage": "https://stage.d4sign.com.br/",
        "hotfix": "https://hotfix.d4sign.com.br/",
        "prod": "https://secure.d4sign.com.br/",
        "secure": "https://secure.d4sign.com.br/",
    }

    # Sufixos aceitos em VAR_PROD, VAR_HOMOL, VAR_STAGING...
    _SUFIXOS_AMBIENTE = {
        "prod": ("PROD", "SECURE"),
        "secure": ("SECURE", "PROD"),
        "homol": ("HOMOL",),
        "staging": ("STAGING", "STAGE"),
        "stage": ("STAGE", "STAGING"),
        "hotfix": ("HOTFIX",),
    }

    @classmethod
    def _getenv_ambiente(cls, nome: str, default: str = "") -> str:
        """Lê NOME_PROD / NOME_HOMOL / ... e cai para NOME se a específica estiver vazia."""
        for sufixo in cls._SUFIXOS_AMBIENTE.get(
            cls.ENVIRONMENT, (cls.ENVIRONMENT.upper(),)
        ):
            valor = (os.getenv(f"{nome}_{sufixo}") or "").strip()
            if valor:
                return valor
        return (os.getenv(nome) or default).strip() or default

    @classmethod
    def load(cls) -> None:
        if cls._loaded:
            return

        root = Path(__file__).resolve().parents[2]
        load_dotenv(root / ".env", override=True)

        cls.ENVIRONMENT = os.getenv("ENVIRONMENT", "prod").lower()
        cls.USERNAME = os.getenv("D4S_USERNAME") or os.getenv("USERNAME", "")
        cls.PASSWORD = os.getenv("D4S_PASSWORD") or os.getenv("PASSWORD", "")
        cls.TOKEN_API = cls._getenv_ambiente("TOKEN_API")
        cls.CRYPT_KEY = cls._getenv_ambiente("CRYPT_KEY")
        cls.EMAIL_TESTE = os.getenv("EMAIL_TESTE", "")
        # Um UUID só: prod, homol, stage e hotfix compartilham o banco.
        # A URL do iframe muda em embed_viewblob_host(), conforme ENVIRONMENT.
        cls.EMBED_DOCUMENT_UUID = cls._uuid_embed()
        cls.EMBED_KEY_SIGNER = cls._getenv_ambiente("EMBED_KEY_SIGNER")
        cls.EMBED_DISPLAY_NAME = os.getenv("EMBED_DISPLAY_NAME", "")
        cls.EMBED_DOCUMENTATION = os.getenv("EMBED_DOCUMENTATION", "")
        anexos = cls._getenv_ambiente("EMBED_ANEXOS_ESPERADOS", "3")
        cls.EMBED_ANEXOS_ESPERADOS = int(anexos or "3")
        cls.TRYIT_URL = os.getenv(
            "TRYIT_URL",
            "https://www.w3schools.com/js/tryit.asp?filename=tryjs_editor",
        )
        cls.BROWSER = os.getenv("BROWSER", "chrome").lower()
        cls.HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
        cls.TIMEOUT = int(os.getenv("TIMEOUT", "60"))
        cls.ACTION_TIMEOUT = int(os.getenv("ACTION_TIMEOUT", "30"))
        cls.LOGIN_TIMEOUT = int(os.getenv("LOGIN_TIMEOUT", "20"))
        cls.SCREENSHOT_ON_FAIL = os.getenv("SCREENSHOT_ON_FAIL", "true").lower() == "true"
        cls.RECORD_VIDEO = os.getenv("RECORD_VIDEO", "true").lower() == "true"
        cls.RECORD_TRACE = os.getenv("RECORD_TRACE", "true").lower() == "true"
        # Debug local: evidência (screenshot por step + vídeo/trace) em TODO
        # cenário, não só na falha. Deixe false no CI pra não inflar o artefato.
        cls.EVIDENCE_ALWAYS = os.getenv("EVIDENCE_ALWAYS", "false").lower() == "true"
        cls._loaded = True

    @classmethod
    def base_url(cls) -> str:
        return cls.URLS.get(cls.ENVIRONMENT, cls.URLS["prod"])

    @classmethod
    def obter_estado_login(cls) -> dict | None:
        return cls._login_storage_state

    @classmethod
    def salvar_estado_login(cls, estado: dict | None) -> None:
        cls._login_storage_state = estado

    @classmethod
    def _uuid_embed(cls) -> str:
        """UUID compartilhado. Aceita o nome antigo EMBED_DOCUMENT_UUID_PROD."""
        for nome in ("EMBED_DOCUMENT_UUID", "EMBED_DOCUMENT_UUID_PROD"):
            valor = (os.getenv(nome) or "").strip()
            if valor:
                return valor
        return ""

    @classmethod
    def exigir_documento_embed(cls) -> None:
        if cls.EMBED_DOCUMENT_UUID:
            return
        raise ValueError(
            f"Sem UUID de embed (ENVIRONMENT={cls.ENVIRONMENT}, "
            f"host {cls.embed_viewblob_host()}). "
            "Preencha EMBED_DOCUMENT_UUID no .env. "
            "O mesmo UUID vale para prod, homol, stage e hotfix."
        )

    @classmethod
    def desk_url(cls) -> str:
        return f"{cls.base_url().rstrip('/')}/desk"

    @classmethod
    def login_url(cls) -> str:
        return f"{cls.base_url().rstrip('/')}/login.html"

    @classmethod
    def embed_viewblob_host(cls) -> str:
        return f"{cls.base_url().rstrip('/')}/embed/viewblob"

    @classmethod
    def project_root(cls) -> Path:
        return Path(__file__).resolve().parents[2]

    @classmethod
    def test_file(cls, filename: str) -> str:
        return str((cls.project_root() / "data" / "files" / filename).resolve())

    @classmethod
    def doc_testes_pdf(cls) -> str:
        return cls.test_file("doc-testes.pdf")

    @classmethod
    def doc_substituto_pdf(cls) -> str:
        return cls.test_file("doc-substituto.pdf")

    @classmethod
    def planilha_lote_xlsx(cls) -> str:
        return cls.test_file("planilha.xlsx")

    @classmethod
    def reports_dir(cls) -> Path:
        path = cls.project_root() / "reports"
        path.mkdir(parents=True, exist_ok=True)
        return path
