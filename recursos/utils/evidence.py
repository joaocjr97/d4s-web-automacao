import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from recursos.utils.config import Config


def _status_falhou(status: Any) -> bool:
    texto = str(status).replace("Status.", "").lower()
    return texto in {"failed", "error"}


class Evidence:
    """Evidências visuais: screenshot e vídeo **somente em falha**."""

    def __init__(self) -> None:
        self._reports = Config.reports_dir()
        self._screenshots = self._reports / "screenshots"
        self._videos = self._reports / "videos"
        self._frames_dir = self._reports / "_frames"
        self._screenshots.mkdir(parents=True, exist_ok=True)
        self._videos.mkdir(parents=True, exist_ok=True)
        self._frames_dir.mkdir(parents=True, exist_ok=True)
        self._frames: list[Path] = []
        self._scenario_slug = ""

    @staticmethod
    def _slug(name: str) -> str:
        slug = re.sub(r"[^\w\-]+", "_", name, flags=re.UNICODE).strip("_")
        return slug[:120] or "cenario"

    @staticmethod
    def _screenshot(driver: Any, path: str) -> None:
        if hasattr(driver, "save_screenshot"):
            driver.save_screenshot(path)
        elif hasattr(driver, "page"):
            driver.page.screenshot(path=path)
        else:
            driver.screenshot(path=path)

    def start_scenario(self, scenario_name: str, driver: Any) -> None:
        self._scenario_slug = self._slug(scenario_name)
        self._frames = []
        # Não captura frame no início: cenários que passam não geram evidência.

    def capture_frame(self, driver: Any) -> None:
        """Captura frame para o vídeo de falha (chamado só em steps/cenários failed)."""
        if Config.RECORD_VIDEO:
            self._capture_frame(driver)

    def capture_screenshot(self, driver: Any, scenario_name: str) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self._slug(scenario_name)}_{timestamp}.png"
        path = self._screenshots / filename
        self._screenshot(driver, str(path))
        return path

    def _capture_frame(self, driver: Any) -> None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        path = self._frames_dir / f"{self._scenario_slug}_{timestamp}.png"
        try:
            self._screenshot(driver, str(path))
            self._frames.append(path)
        except Exception:
            pass

    def finish_scenario(self, driver: Any, status: str) -> None:
        """Gera MP4 apenas se o cenário falhou; em sucesso só limpa frames."""
        if Config.RECORD_VIDEO and _status_falhou(status):
            self._capture_frame(driver)
            self._salvar_video(status)

        self._limpar_frames()

    def _limpar_frames(self) -> None:
        for frame in self._frames:
            if frame.exists():
                try:
                    frame.unlink()
                except Exception:
                    pass
        self._frames = []

    def _salvar_video(self, status: str) -> None:
        """Gera MP4 a partir dos frames do erro (ffmpeg via imageio-ffmpeg)."""
        if len(self._frames) < 1:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        status_txt = str(status).replace("Status.", "")
        video_path = self._videos / f"{self._scenario_slug}_{status_txt}_{timestamp}.mp4"

        try:
            self._escrever_mp4(video_path)
        except Exception as exc:
            fallback = self._videos / f"{self._scenario_slug}_{status_txt}_{timestamp}.png"
            ultimo = self._frames[-1]
            if ultimo.exists():
                fallback.write_bytes(ultimo.read_bytes())
            info = self._videos / f"{self._scenario_slug}_{status_txt}_{timestamp}.txt"
            info.write_text(
                f"Cenario: {self._scenario_slug}\n"
                f"Status: {status_txt}\n"
                f"Frames: {len(self._frames)}\n"
                f"Erro ao gerar MP4: {exc}\n",
                encoding="utf-8",
            )

    def _escrever_mp4(self, video_path: Path, fps: int = 2) -> None:
        import imageio_ffmpeg

        frames_validos = [f for f in self._frames if f.exists()]
        if not frames_validos:
            raise RuntimeError("Nenhum frame disponível para o vídeo.")

        if len(frames_validos) == 1:
            frames_validos = frames_validos * 4

        lista = self._frames_dir / f"{self._scenario_slug}_list.txt"
        with lista.open("w", encoding="utf-8") as fh:
            for frame in frames_validos:
                caminho = frame.resolve().as_posix().replace("'", r"'\''")
                fh.write(f"file '{caminho}'\n")
                fh.write(f"duration {1 / fps}\n")
            ultimo = frames_validos[-1].resolve().as_posix().replace("'", r"'\''")
            fh.write(f"file '{ultimo}'\n")

        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        cmd = [
            ffmpeg,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(lista),
            "-vf",
            "scale=trunc(iw/2)*2:trunc(ih/2)*2",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            str(video_path),
        ]
        result = subprocess.run(
            cmd, capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
        try:
            lista.unlink()
        except Exception:
            pass

        if result.returncode != 0 or not video_path.exists() or video_path.stat().st_size == 0:
            raise RuntimeError(result.stderr[-500:] if result.stderr else "Falha ffmpeg")
