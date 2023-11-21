import numpy as np

import argparse
import os
import sys
from math import floor
from time import sleep

from av_audio import Audio, smooth_hor, smooth_ver, fade_np, smooth
from av_serial import Serial
from graph import graph

DIRNAME = __file__.replace("\\", "/").rsplit("/", 1)[0]
BG = False


def default_():
    vals: list[int | float]
    vals_prev: list[int | float] = [0] * 60

    while True:
        audio.update()  # Analyze audio
        vals = audio.get_values()  #  Get FFT data
        vals = smooth_ver(vals_prev, vals, 4)
        vals = smooth_hor(vals, 3)
        vals_prev = vals
        vals = list(reversed(vals)) + vals  # Mirror data
        # Prepare data for sending (using homemade protocol)
        data = f"{{{'|'.join(map(lambda a: str(int(a)), vals))}}}"
        graph(vals, 20, clear=True)  # Display data to console
        port.send(data)  # Send data via serial port
        sleep(0.001)


def default():
    vals: list[int | float] = [0] * 60

    while True:
        audio.update()
        vals = smooth_ver(vals, audio.get_values(), 4)
        vals = smooth_hor(vals, 3)
        pt = list(reversed(vals)) + vals
        if not BG:
            graph(pt, 20, clear=True)
        data = "{" + "|".join(map(lambda a: str(floor(a)), pt)) + "}"
        port.send(data)
        sleep(0.01)


def rolling():
    vals = np.array([0] * 60, float)

    while True:
        audio.update()
        avg = sum(audio.get_values_np()) // 60
        avg = min(max(avg, 0), 255)
        vals = np.concatenate(([avg], vals[0:-1]))
        vals = fade_np(vals, 0.001)
        vals = smooth(vals, 2)
        vals = np.clip(vals, 0, 255)
        ts = list(reversed(vals**2)) + list(vals**2)
        data = f"{{{'|'.join(map(lambda a: str(floor(a)), ts))}}}"
        if not BG:
            graph(ts, 20, clear=True)
        port.send(data)
        sleep(0.01)


def test():
    i = 0

    while True:
        l = [0] * 120
        i = (i + 1) % 120
        l[i] = 100
        s = "{" + "|".join(map(str, l)) + "}"
        port.send(s)
        res = port._port.read_all()
        if res:
            res = res.decode()
            data = list(map(int, res.split("|")))
            graph(data, 20, clear=True)
        sleep(0.1)


def main():
    global audio, port

    sys.stdout.write("\x1b[?25l")

    parser = argparse.ArgumentParser(prog="PySerialAudioVisualizer")

    parser.add_argument("-p", "--port", dest="port")
    parser.add_argument(
        "-m",
        "--mode",
        choices=["fft", "rolling", "test"],
        default="rolling",
        help="Visualization mode",
    )

    args = parser.parse_args()

    audio = Audio()
    audio.setup()

    if not args.port:
        port = Serial(Serial.select())
    else:
        port = Serial(args.port)

    print("\x1b[2J\x1b[H")

    if args.mode == "fft":
        default()
    elif args.mode == "rolling":
        rolling()
    elif args.mode == "test":
        test()


if __name__ == "__main__":
    if "pythonw" in sys.executable:
        sys.stderr = open(f"{DIRNAME}/debug.txt", "w")
        sys.stdout = open(os.devnull, "w")
        BG = True
    try:
        sys.stderr.write("Start\n")
        main()
    except KeyboardInterrupt:
        print("\x1b[2J\x1b[H", end="")
        print("Goodbye!")
