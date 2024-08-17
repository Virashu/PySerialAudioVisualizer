"""Output audio visualizer"""

from __future__ import annotations

__all__ = ["AudioVisualizer"]

import argparse
import logging
import sys
from math import floor, isnan
from threading import Thread
from time import sleep, time
from typing import Iterable, Literal

import numpy as np
import saaba
from serial import SerialException

from .analyzer import (
    Analyzer,
    AnalyzerFFT,
    AnalyzerFlat,
    AnalyzerRolling,
    AnalyzerRollingEase,
)
from .av_audio import Audio
from .av_serial import Serial

DIRNAME: str = __file__.replace("\\", "/").rsplit("/", 1)[0]


logger = logging.getLogger(__name__)


class Args(argparse.Namespace):
    list: bool
    mode: Literal["fft", "rolling", "rollingease", "flat"]
    port: str
    no_serial: bool
    device: str | None
    size: int


def to_hex(n: int) -> str:
    return hex(n).removeprefix("0x").title()


def _stringify_serial(data: Iterable[int | float]) -> str:
    """Convert list to string.

    Prepare data for sending over serial
    """
    str_arr: Iterable[str]

    if isinstance(data, np.ndarray):
        v = np.vectorize(to_hex)
        str_arr = v(data.astype(int))
    else:
        # For non-numpy floats
        str_arr = ("0" if isnan(a) else str(to_hex(floor(a))) for a in data)

    return f"[{",".join(str_arr)}]"


class VAudioService:
    def __init__(self, analyzer: Analyzer) -> None:
        self.analyzer = analyzer
        self.running: bool

    def run(self) -> None:
        self.running = True

    def stop(self) -> None:
        self.running = False


class VAudioHttpServer(VAudioService):
    def __init__(self, analyzer: Analyzer) -> None:
        super().__init__(analyzer)
        self._server = saaba.App()

        @self._server.get("/")
        def _(_: saaba.Request, res: saaba.Response) -> None:
            res.send({"data": self.analyzer.get_data_mirrored().astype(int).tolist()})

    def run(self) -> None:
        self._server.listen("0.0.0.0", 7777)  # noqa: S104

    def stop(self) -> None:
        self._server.stop()


class VAudioSerial(VAudioService):
    def __init__(self, analyzer: Analyzer, port: str) -> None:
        super().__init__(analyzer)

        self.port_name = port
        self.send_interval: float = 0.05

    def run(self) -> None:
        super().run()

        port = None

        while port is None:
            if not self.running:
                return

            try:
                port = Serial(self.port_name)
            except SerialException:
                logger.warning(
                    "Serial port %s not found. Retry after 1 second", self.port_name
                )
                sleep(1)

        delta: float = 0
        while self.running:
            if time() - delta > self.send_interval:
                delta = time()
                data = _stringify_serial(self.analyzer.get_data_mirrored())
                port.send(data)


class AudioVisualizer:
    """Audio visualizer class"""

    def __init__(self) -> None:
        self._running: bool = True

        self._args: Args

        self._parse_args()

        self.size = self._args.size

        self._data_mirrored: list[int] = [0] * self.size
        self._rendered_data: str = _stringify_serial(
            np.zeros(self.size, int).astype(str)
        )

        self.services: list[VAudioService] = []
        self.threads: list[Thread] = []

        if self._args.list:
            Serial.list()
            sys.exit(0)

    def run(self) -> None:
        """Start the visualizer"""

        audio = Audio()

        if self._args.device is not None:
            device_name = self._args.device
        else:
            match sys.platform:
                case "win32":
                    device_name = "Stereo Mix"
                case _:
                    device_name = "default"

        logger.info("Chosen device: %s", device_name)

        index = Audio.select_by_name(device_name)

        if index is not None:
            audio.device_index = index
        else:
            msg = "No audio input device found"
            raise RuntimeError(msg)

        audio.setup()

        analyzer: Analyzer

        match self._args.mode:
            case "fft":
                analyzer = AnalyzerFFT(self.size, audio)
            case "rolling":
                analyzer = AnalyzerRolling(self.size, audio)
            case "rollingease":
                analyzer = AnalyzerRollingEase(self.size, audio)
            case "flat":
                analyzer = AnalyzerFlat(self.size, audio)

        if not self._args.no_serial:
            self.services.append(VAudioSerial(analyzer, self._args.port))

        self.services.append(VAudioHttpServer(analyzer))

        for s in self.services:
            _t = Thread(target=s.run, daemon=True)
            _t.start()
            logger.info("Service started: %s", s.__class__.__name__)
            self.threads.append(_t)

        while self._running:
            # To stay responsible to things like KeyboardInterrupt
            # sleep(0.1)
            analyzer.update()

        for s in self.services:
            s.stop()

        for t in self.threads:
            t.join()

    def stop(self) -> None:
        """Interrupt execution"""
        self._running = False

    def _parse_args(self) -> None:
        self._args = Args()

        parser = argparse.ArgumentParser(prog="PySerialAudioVisualizer")

        # Serial port
        parser_serial = parser.add_mutually_exclusive_group(required=True)

        parser_serial.add_argument("-p", "--port", help="Select port by name")
        parser_serial.add_argument(
            "-l",
            "--list",
            action="store_true",
            help="List available ports",
        )
        parser_serial.add_argument("--noserial", action="store_true", dest="no_serial")

        # Analyzer
        parser.add_argument(
            "-m",
            "--mode",
            choices=["fft", "rolling", "rollingease", "flat"],
            default="rolling",
            help="Visualization mode",
        )
        parser.add_argument(
            "-d", "--device", default=None, help="Select audio input device by name"
        )

        parser.add_argument("-s", "--size", default=120, type=int)

        parser.parse_args(namespace=self._args)

        # Groups:
        # - General
        # - Analyzer
        # - Serial
        # - HTTP
