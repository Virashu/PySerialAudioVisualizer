import argparse
import os
import sys
import threading
from math import floor, isnan
from time import sleep, time

import saaba
from serial import SerialException

from .analyzer import AnalyzerRolling, AnalyzerFFT
from .av_audio import Audio
from .av_serial import Serial


DIRNAME: str = __file__.replace("\\", "/").rsplit("/", 1)[0]


class AudioVisualizer:
    def __init__(self) -> None:
        self._data_mirrored: list[int] = [0] * 120
        self._rendered_data: str = "{" + "|".join(["0"] * 120) + "}"
        self._args: argparse.Namespace
        self._background: bool = False
        self._audio: Audio
        self._running = True
        self._server: saaba.App

        self._set_mode()

        self._parse_args()

        if not self._background:
            sys.stdout.write("\x1b[?25l")  # hide cursor

        if self._args.list:
            Serial.list()
            return

    def run(self):
        audio_thread = threading.Thread(target=self._audio_thread, daemon=True)
        audio_thread.start()

        if not self._args.noserial:
            serial_thread = threading.Thread(target=self._serial_thread, daemon=True)
            serial_thread.start()

        http_thread = threading.Thread(target=self._http_thread, daemon=True)
        http_thread.start()

        audio_thread.join()
        if not self._args.noserial:
            serial_thread.join()

        self._server.stop()
        http_thread.join()

    def _set_mode(self) -> None:
        if "pythonw" in sys.executable:
            self._background = True
            with open(f"{DIRNAME}/../debug.txt", "w", encoding="utf-8") as stderr:
                sys.stderr = stderr
            with open(os.devnull, "w", encoding="utf-8") as null:
                sys.stdout = null

    def _parse_args(self) -> None:
        parser = argparse.ArgumentParser(prog="PySerialAudioVisualizer")
        parser.add_argument("-p", "--port", dest="port")
        parser.add_argument("--noserial", action="store_true")
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
        self._audio.setup()

        match self._args.mode:
            case "fft":
                analyzer = AnalyzerFFT(self._audio)
            case "rolling":
                analyzer = AnalyzerRolling(self._audio)
            case _:
                raise ValueError(f"Invalid mode: {self._args.mode}")

        while self._running:
            analyzer.update()
            values = analyzer.get_data_mirrored()
            self._data_mirrored = values.tolist()

            data = (
                "{"
                + "|".join(("0" if isnan(a) else str(floor(a)) for a in values))
                + "}"
            )

            self._rendered_data = data

    def _serial_thread(self) -> None:
        if self._args.port:
            port_id = self._args.port
        elif not self._background:
            port_id = Serial.select()
        else:
            raise ValueError("Port not specified")

        _connected = False

        while not _connected:
            try:
                port = Serial(port_id)
                _connected = True
            except SerialException as e:
                print(type(e))
                sleep(1)

        delta = 0
        while self._running:
            if time() - delta > 0.05:
                delta = time()
                port.send(self._rendered_data)

    def _http_thread(self) -> None:
        app = saaba.App()

        @app.get("/")
        def _(req, res) -> None:
            res.send({"data": self._data_mirrored})

        app.listen("0.0.0.0", 7777)


if __name__ == "__main__":
    visualizer = AudioVisualizer()
    try:
        visualizer.run()
    except KeyboardInterrupt:
        visualizer._running = False
        print("\x1b[2J\x1b[H", end="")
        print("Goodbye!")
        sys.exit(0)
