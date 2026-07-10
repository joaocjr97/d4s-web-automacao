import os
from pathlib import Path

from dotenv import load_dotenv


class Config:
    _loaded = False

    ENVIRONMENT: str = "prod"
    USERNAME: str = ""
    PASSWORD: str = ""
    TOKEN_API: str = ""
    CRYPT_KEY: str = ""
    EMAIL_TESTE: str = ""
    BROWSER: str = "chrome"
    HEADLESS: bool = False
    TIMEOUT: int = 240
    LOGIN_TIMEOUT: int = 20
    SCREENSHOT_ON_FAIL: bool = True
    RECORD_VIDEO: bool = True

    URLS = {
        "ghost": "https://ghost.d4sign.com.br/",
        "homol": "https://homol.d4sign.com.br/",
        "staging": "https://stage.d4sign.com.br/",
        "hotfix": "https://hotfix.d4sign.com.br/",
        "prod": "https://secure.d4sign.com.br/",
    }

    @classmethod
    def load(cls) -> None:
        if cls._loaded:
            return

        root = Path(__file__).resolve().parents[2]
        load_dotenv(root / ".env", override=True)

        cls.ENVIRONMENT = os.getenv("ENVIRONMENT", "prod").lower()
        cls.USERNAME = os.getenv("D4S_USERNAME") or os.getenv("USERNAME", "")
        cls.PASSWORD = os.getenv("D4S_PASSWORD") or os.getenv("PASSWORD", "")
        cls.TOKEN_API = os.getenv("TOKEN_API", "")
        cls.CRYPT_KEY = os.getenv("CRYPT_KEY", "")
        cls.EMAIL_TESTE = os.getenv("EMAIL_TESTE", "")
        cls.BROWSER = os.getenv("BROWSER", "chrome").lower()
        cls.HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
        cls.TIMEOUT = int(os.getenv("TIMEOUT", "240"))
        cls.LOGIN_TIMEOUT = int(os.getenv("LOGIN_TIMEOUT", "20"))
        cls.SCREENSHOT_ON_FAIL = os.getenv("SCREENSHOT_ON_FAIL", "true").lower() == "true"
        cls.RECORD_VIDEO = os.getenv("RECORD_VIDEO", "true").lower() == "true"
        cls._loaded = True

    @classmethod
    def base_url(cls) -> str:
        return cls.URLS.get(cls.ENVIRONMENT, cls.URLS["prod"])

    @classmethod
    def desk_url(cls) -> str:
        return f"{cls.base_url().rstrip('/')}/desk"

    @classmethod
    def login_url(cls) -> str:
        return f"{cls.base_url().rstrip('/')}/login.html"

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
    def planilha_lote_xlsx(cls) -> str:
        return cls.test_file("planilha.xlsx")

    @classmethod
    def reports_dir(cls) -> Path:
        path = cls.project_root() / "reports"
        path.mkdir(parents=True, exist_ok=True)
        return path
