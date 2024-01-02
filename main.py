import argparse
import os
import sys
import threading
from math import floor, isnan
from time import sleep, time

from vaudio.analyzer import AnalyzerRolling, AnalyzerFFT
from vaudio.av_audio import Audio
from vaudio.av_serial import Serial
from vaudio.graph import graph
from vaudio.api import serve


DIRNAME: str = __file__.replace("\\", "/").rsplit("/", 1)[0]

gdata: dict[str, str] = {"data": "{" + "|".join(["0"] * 120) + "}"}


def main():
    # global audio, port

    sys.stdout.write("\x1b[?25l")

    parser = argparse.ArgumentParser(prog="PySerialAudioVisualizer")
    parser.add_argument("-p", "--port", dest="port")
    parser.add_argument(
        "-m",
        "--mode",
        choices=["fft", "rolling"],
        default="rolling",
        help="Visualization mode",
    )
    args = parser.parse_args()

    audio = Audio()
    index = Audio.select_by_name("Stereo Mix")
    if index is not None:
        audio.device_index = index
    audio.setup()

    if args.port:
        port_id = args.port
    else:
        port_id = Serial.select()

    _connected = False

    while not _connected:
        try:
            port = Serial(port_id)
            _connected = True
        except Exception:
            sleep(1)

    print("\x1b[2J\x1b[H")

    match args.mode:
        case "fft":
            analyzer = AnalyzerFFT(audio)
        case "rolling":
            analyzer = AnalyzerRolling(audio)
        case _:
            raise ValueError(f"Invalid mode: {args.mode}")

    delta = 0
    while True:
        analyzer.update()
        values = analyzer.get_data_mirrored()

        graph(values, 20, clear=True)

        data = (
            "{"
            + "|".join((str(floor(a)) if not isnan(a) else "0" for a in values))
            + "}"
        )
        gdata.update({"data": data})

        if time() - delta > 0.05:
            delta = time()
            port.send(data)  # type: ignore


if __name__ == "__main__":
    if "pythonw" in sys.executable:
        sys.stderr = open(f"{DIRNAME}/../debug.txt", "w", encoding="utf-8")
        sys.stdout = open(os.devnull, "w", encoding="utf-8")
    try:
        p2 = threading.Thread(target=serve, args=(gdata,))
        p2.daemon = True
        p2.start()
        main()
        p2.join()
    except KeyboardInterrupt:
        print("\x1b[2J\x1b[H", end="")
        print("Goodbye!")
