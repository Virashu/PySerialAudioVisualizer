from av_audio import Audio, smooth_hor, smooth_ver, fade, bounds
from av_serial import Serial
from graph import graph
from sys import argv
import numpy as np


def default() -> None:
    audio = Audio()
    audio.setup()

    if "-p" in argv:
        port = Serial(argv[argv.index("-p") + 1])
    else:
        port = Serial(Serial.select())

    vals: list[int | float] = [0] * 60
    vals_prev: list[int | float] = [0] * 60

    print(f"\x1b[2J\x1b[H")

    while True:
        audio.update()  # Analyze audio
        vals = audio.get_values()  #  Get FFT data
        vals = smooth_ver(vals_prev, vals, 4)
        vals = smooth_hor(vals, 1)
        vals_prev = vals
        vals = list(reversed(vals)) + vals  # Mirror data
        # Prepare data for sending (using homemade protocol)
        data = f"{{{'|'.join(map(lambda a: str(int(a)), vals))}}}"
        # graph(vals_prev, 20, clear=True)  # Display data to console
        port.send(data)  # Send data via serial port


def rolling() -> None:
    audio = Audio()
    audio.setup()

    if "-p" in argv:
        port = Serial(argv[argv.index("-p") + 1])
    else:
        port = Serial(Serial.select())

    vals: list[int | float] = [0] * 60

    print(f"\x1b[2J\x1b[H")

    while True:
        audio.update()  # Analyze audio
        avg = sum(audio.get_values()) // 60  #  Get FFT data
        avg = min(max(avg, 0), 255)
        vals.insert(0, avg)
        vals.pop()
        vals = bounds(fade(vals))
        ts = list(reversed(vals)) + vals  # Mirror data
        # Prepare data for sending (using homemade protocol)
        data = f"{{{'|'.join(map(lambda a: str(int(a)), ts))}}}"
        graph(vals, 20, clear=True)  # Display data to console
        port.send(data)  # Send data via serial port


if __name__ == "__main__":
    try:
        rolling()
    except KeyboardInterrupt:
        print("\x1b[2J\x1b[H", end="")
        print("Goodbye!")
