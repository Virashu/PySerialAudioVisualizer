"""
Output audio visualizer
"""

__all__ = ["AudioVisualizer"]

import argparse
import logging
import os
import sys
import threading
from math import floor, isnan
from time import sleep, time
from typing import Iterable

import saaba
import numpy as np
from serial import SerialException

from .analyzer import Analyzer, AnalyzerFFT, AnalyzerRolling
from .av_audio import Audio
from .av_serial import Serial
from .typing import FloatArray, IntArray

DIRNAME: str = __file__.replace("\\", "/").rsplit("/", 1)[0]

SERIAL_INTERVAL: float = 0.05


logger = logging.getLogger(__name__)


def _stringify_serial(data: Iterable[int | float]) -> str:
    """
    Convert list to string.
    Prepare data for sending over serial
    """

    if isinstance(data, np.ndarray):
        ints: IntArray = data.astype(int)
        return "{" + "|".join(ints.astype(str)) + "}"

    # For non-numpy floats
    res = "{" + "|".join(("0" if isnan(a) else str(floor(a)) for a in data)) + "}"
    return res


class AudioVisualizer:
    """Audio visualizer class"""

    def __init__(self) -> None:
        self._data_mirrored: list[int] = [0] * 120
        self._rendered_data: str = _stringify_serial(np.zeros(120, int).astype(str))

        self._background: bool = False
        self._running: bool = True

        self._args: argparse.Namespace
        self._audio: Audio
        self._server: saaba.App

        self._set_mode()
        self._parse_args()

        if not self._background:
            sys.stdout.write("\x1b[?25l")  # hide cursor

        if self._args.list:
            Serial.list()
            return

    def run(self) -> None:
        """Start the visualizer"""
        audio_thread = threading.Thread(target=self._audio_thread, daemon=True)
        audio_thread.start()

        if self._args.no_serial:
            serial_thread = None
        else:
            serial_thread = threading.Thread(target=self._serial_thread, daemon=True)
            serial_thread.start()

        http_thread = threading.Thread(target=self._http_thread, daemon=True)
        http_thread.start()

        while self._running:
            # To stay responsible to things like KeyboardInterrupt
            sleep(1e6)

        audio_thread.join()

        if serial_thread:
            serial_thread.join()

        http_thread.join()

    def stop(self) -> None:
        """Interrupt execution"""
        self._running = False

        if self._server:
            self._server.stop()

    def _set_mode(self) -> None:
        if "pythonw" in sys.executable:
            self._background = True
            with open(f"{DIRNAME}/../debug.txt", "w", encoding="utf-8") as stderr:
                sys.stderr = stderr
            with open(os.devnull, "w", encoding="utf-8") as null:
                sys.stdout = null

    def _parse_args(self) -> None:
        parser = argparse.ArgumentParser(prog="PySerialAudioVisualizer")
        parser.add_argument("-p", "--port")
        # parser.add_argument("-s", "--select", action="store_true")
        parser.add_argument("--noserial", action="store_true", dest="no_serial")
        parser.add_argument(
            "-m",
            "--mode",
            choices=["fft", "rolling"],
            default="rolling",
            help="Visualization mode",
        )
        parser.add_argument(
            "-l", "--list", action="store_true", help="List available ports"
        )
        self._args = parser.parse_args()

    def _audio_thread(self) -> None:
        self._audio = Audio()
        index = Audio.select_by_name("Stereo Mix")
        if index is not None:
            self._audio.device_index = index
        else:
            logger.warning("No audio input device found")

        self._audio.setup()

        analyzer: Analyzer

        match self._args.mode:
            case "fft":
                analyzer = AnalyzerFFT(self._audio)
            case "rolling":
                analyzer = AnalyzerRolling(self._audio)
            case _:
                raise ValueError(f"Invalid mode: {self._args.mode}")

        while self._running:
            analyzer.update()

            values: FloatArray = analyzer.get_data_mirrored()
            self._data_mirrored = values.astype(int).tolist()

            self._rendered_data = _stringify_serial(values)

    def _serial_thread(self) -> None:
        if self._args.port:
            port_id = self._args.port
        # elif not self._background:
        #     port_id = Serial.select()
        else:
            raise ValueError(
                "Port not specified. "
                "Use --list argument to list available ports "
                "or --port argument to select one"
            )

        port = None
        while not port:
            try:
                port = Serial(port_id)
            except SerialException:
                sleep(1)

        delta: float = 0
        while self._running:
            if time() - delta > SERIAL_INTERVAL:
                delta = time()
                port.send(self._rendered_data)

    def _http_thread(self) -> None:
        self._server = saaba.App()

        @self._server.get("/")
        def _(_: saaba.Request, res: saaba.Response) -> None:
            res.send({"data": self._data_mirrored})

        self._server.listen("0.0.0.0", 7777)
