import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from recursos.utils.config import Config


# Frames mantidos em disco por cenário: dá contexto do que levou à falha sem
# acumular a suíte inteira, já que cenários que passam descartam tudo.
MAX_FRAMES = 20


def _status_falhou(status: Any) -> bool:
    texto = str(status).replace("Status.", "").lower()
    return texto in {"failed", "error"}


def _conectado(driver: Any) -> bool:
    """Evita chamar screenshot/trace num navegador que já crashou (fica pendurado)."""
    checar = getattr(driver, "is_connected", None)
    if checar is None:
        return True
    try:
        return bool(checar())
    except Exception:
        return False


class Evidence:
    """Evidências: screenshot, vídeo e trace do Playwright, por padrão só em falha."""

    def __init__(self) -> None:
        self._reports = Config.reports_dir()
        self._screenshots = self._reports / "screenshots"
        self._videos = self._reports / "videos"
        self._traces = self._reports / "traces"
        self._frames_dir = self._reports / "_frames"
        self._screenshots.mkdir(parents=True, exist_ok=True)
        self._videos.mkdir(parents=True, exist_ok=True)
        self._traces.mkdir(parents=True, exist_ok=True)
        self._frames_dir.mkdir(parents=True, exist_ok=True)
        self._frames: list[Path] = []
        self._scenario_slug = ""
        self._trace_ativo = False
        # Preenchido em finish_scenario quando um trace é salvo (não descartado).
        self.ultimo_trace: Path | None = None

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
        self.ultimo_trace = None
        self._trace_ativo = False
        if Config.RECORD_TRACE and hasattr(driver, "start_trace_chunk"):
            try:
                driver.start_trace_chunk(self._scenario_slug)
                self._trace_ativo = True
            except Exception:
                self._trace_ativo = False

    def capture_frame(self, driver: Any) -> None:
        """Alimenta o buffer rotativo usado no vídeo caso o cenário falhe."""
        if Config.RECORD_VIDEO:
            self._capture_frame(driver)

    def capture_screenshot(self, driver: Any, scenario_name: str) -> Path | None:
        if not _conectado(driver):
            return None
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self._slug(scenario_name)}_{timestamp}.png"
        path = self._screenshots / filename
        self._screenshot(driver, str(path))
        return path

    def _capture_frame(self, driver: Any) -> None:
        if not _conectado(driver):
            return
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        path = self._frames_dir / f"{self._scenario_slug}_{timestamp}.png"
        try:
            self._screenshot(driver, str(path))
            self._frames.append(path)
            self._descartar_frames_antigos()
        except Exception:
            pass

    def _descartar_frames_antigos(self) -> None:
        while len(self._frames) > MAX_FRAMES:
            antigo = self._frames.pop(0)
            try:
                antigo.unlink(missing_ok=True)
            except Exception:
                pass

    def finish_scenario(self, driver: Any, status: str) -> None:
        """Gera MP4/trace se o cenário falhou, ou sempre que EVIDENCE_ALWAYS=true."""
        if Config.RECORD_VIDEO and (_status_falhou(status) or Config.EVIDENCE_ALWAYS):
            self._capture_frame(driver)
            self._salvar_video(status)

        self._limpar_frames()
        self._finalizar_trace(driver, status)

    def _finalizar_trace(self, driver: Any, status: str) -> None:
        if not self._trace_ativo:
            return
        self._trace_ativo = False

        if not _conectado(driver):
            # Navegador crashou: chamar tracing.stop_chunk agora ficaria
            # pendurado esperando resposta de um processo morto.
            self.ultimo_trace = None
            return

        salvar = _status_falhou(status) or Config.EVIDENCE_ALWAYS
        path: Path | None = None
        if salvar:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            status_txt = str(status).replace("Status.", "")
            path = self._traces / f"{self._scenario_slug}_{status_txt}_{timestamp}.zip"

        try:
            if hasattr(driver, "stop_trace_chunk"):
                driver.stop_trace_chunk(str(path) if path else None)
                self.ultimo_trace = path
        except Exception:
            self.ultimo_trace = None

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
