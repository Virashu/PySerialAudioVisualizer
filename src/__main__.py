from abc import abstractmethod
import numpy as np

import argparse
import os
import sys
from math import floor
from time import time

from av_audio import Audio, smooth_hor, smooth_ver, fade_np, smooth
from av_serial import Serial
from graph import graph

DIRNAME = __file__.replace("\\", "/").rsplit("/", 1)[0]


class Analyzer:
    def __init__(self, audio: None | Audio = None) -> None:
        if audio:
            self.audio = audio
        else:
            self.audio = Audio()

    def update(self) -> None:
        self.audio.update()

    @abstractmethod
    def get_data(self):
        ...

    @abstractmethod
    def get_data_mirrored(self):
        ...


class AnalyzerFFT(Analyzer):
    def __init__(self, audio: None | Audio = None) -> None:
        super().__init__(audio)
        self.fft: np.ndarray = np.ndarray((60,), float)

    def update(self) -> None:
        super().update()
        fft_pr: np.ndarray = self.fft
        self.fft: np.ndarray = self.audio.get_values_np()
        self.fft: np.ndarray = np.array(smooth_ver(fft_pr, self.fft, 4))
        sm: list[int | float] = smooth_hor(self.fft, 3)  # type: ignore
        self.fft: np.ndarray = np.array(sm)

    def get_data(self) -> np.ndarray:
        return self.fft

    def get_data_mirrored(self) -> np.ndarray:
        return np.concatenate((np.flip(self.fft), self.fft))


class AnalyzerRolling(Analyzer):
    def __init__(self, audio: None | Audio = None) -> None:
        super().__init__(audio)
        self.values: np.ndarray = np.ndarray((60,), float)

    def update(self) -> None:
        super().update()
        avg = int(np.average(audio.get_values_np()))
        avg = min(max(avg, 0), 255)

        self.values = np.concatenate(([avg], self.values[0:-1]))
        self.values = fade_np(self.values, 0.001)
        self.values = smooth(self.values, 2)

    def get_data(self) -> np.ndarray:
        values_adj = self.values**2
        values_adj = np.clip(values_adj, 0, 255)
        return values_adj

    def get_data_mirrored(self) -> np.ndarray:
        v = self.get_data()
        return np.concatenate((np.flip(v), v))


# def default():
#     vals: list[int | float] = [0] * 60

#     while True:
#         audio.update()
#         vals = smooth_ver(vals, audio.get_values(), 4)
#         vals = smooth_hor(vals, 3)
#         vals_mirrored = list(reversed(vals)) + vals
#         try_graph(vals_mirrored)
#         data = "{" + "|".join(map(lambda a: str(floor(a)), vals_mirrored)) + "}"
#         writefile(data)
#         port.send(data)
#         sleep(0.01)


# def writefile(data):
#     try:
#         with open("D:/_TEMP/tmp/vis/data.txt", "w") as f:
#             f.write(data)
#     except:
#         pass


# def rolling():
#     vals = np.ndarray((60,), float)
#     delta = time()

#     while True:
#         audio.update()

#         avg = sum(audio.get_values_np()) // 60
#         avg = min(max(avg, 0), 255)
#         vals = np.concatenate(([avg], vals[0:-1]))
#         vals = fade_np(vals, 0.001)
#         vals = smooth(vals, 2)

#         # vals_mirrored = list(reversed(vals**2)) + list(vals**2)
#         vals_adj = vals**2
#         vals_adj = np.clip(vals_adj, 0, 255)

#         vals_mirrored = np.concatenate((np.flip(vals_adj), vals_adj))
#         try_graph(vals_mirrored)
#         data = f"{{{'|'.join(map(lambda a: str(floor(a)), vals_mirrored))}}}"
#         writefile(data)
#         if time() - delta > 0.01:
#             delta = time()
#             port.send(data)


def main():
    global audio, port

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
    audio.setup()

    if args.port:
        port = Serial(args.port)
    else:
        port = Serial(Serial.select())

    print("\x1b[2J\x1b[H")

    # if args.mode == "fft":
    #     default()
    # elif args.mode == "rolling":
    #     rolling()

    analyzer = AnalyzerRolling(audio)
    delta = 0
    while True:
        analyzer.update()
        values = analyzer.get_data_mirrored()
        graph(values, 20, clear=True)
        data = "{" + "|".join((str(floor(a)) for a in values)) + "}"

        try:
            with open("D:/_temp/tmp/vis/data.txt", "w") as f:
                f.write(data)
        except:
            pass

        if time() - delta > 0.05:
            delta = time()
            port.send(data)


if __name__ == "__main__":
    if "pythonw" in sys.executable:
        sys.stderr = open(f"{DIRNAME}/debug.txt", "w")
        sys.stdout = open(os.devnull, "w")
    try:
        sys.stderr.write("Start\n")
        main()
    except KeyboardInterrupt:
        print("\x1b[2J\x1b[H", end="")
        print("Goodbye!")
