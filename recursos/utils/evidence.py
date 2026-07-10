import re
from datetime import datetime
from pathlib import Path

from selenium.webdriver.remote.webdriver import WebDriver

from recursos.utils.config import Config


class Evidence:
    def __init__(self) -> None:
        self._reports = Config.reports_dir()
        self._screenshots = self._reports / "screenshots"
        self._videos = self._reports / "videos"
        self._screenshots.mkdir(parents=True, exist_ok=True)
        self._videos.mkdir(parents=True, exist_ok=True)
        self._frames: list[Path] = []
        self._scenario_slug = ""

    @staticmethod
    def _slug(name: str) -> str:
        slug = re.sub(r"[^\w\-]+", "_", name, flags=re.UNICODE).strip("_")
        return slug[:120] or "cenario"

    def start_scenario(self, scenario_name: str, driver: WebDriver) -> None:
        self._scenario_slug = self._slug(scenario_name)
        self._frames = []
        if Config.RECORD_VIDEO:
            self._capture_frame(driver)

    def capture_screenshot(self, driver: WebDriver, scenario_name: str) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self._slug(scenario_name)}_{timestamp}.png"
        path = self._screenshots / filename
        driver.save_screenshot(str(path))
        return path

    def _capture_frame(self, driver: WebDriver) -> None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        path = self._screenshots / f"_frame_{self._scenario_slug}_{timestamp}.png"
        driver.save_screenshot(str(path))
        self._frames.append(path)

    def finish_scenario(self, driver: WebDriver, status: str) -> None:
        if Config.RECORD_VIDEO and self._frames:
            self._save_video_stub(driver, status)

        for frame in self._frames:
            if frame.exists():
                frame.unlink()

        self._frames = []

    def _save_video_stub(self, driver: WebDriver, status: str) -> None:
        """Salva evidência visual do cenário (screenshot final + metadados).

        Para gravação de vídeo nativa, use Playwright ou Selenoid no CI.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        evidence_path = self._videos / f"{self._scenario_slug}_{status}_{timestamp}.png"
        driver.save_screenshot(str(evidence_path))

        if len(self._frames) >= 2:
            info_path = self._videos / f"{self._scenario_slug}_{status}_{timestamp}.txt"
            info_path.write_text(
                f"Cenario: {self._scenario_slug}\n"
                f"Status: {status}\n"
                f"Frames capturados: {len(self._frames)}\n",
                encoding="utf-8",
            )
