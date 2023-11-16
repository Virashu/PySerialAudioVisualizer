import numpy as np
import pyaudio as pa
import serial
import serial.tools.list_ports

import struct

from graph import graph


class _Audio:
    def __init__(self, buffer_size: int = 60) -> None:
        self._chunk = 1024
        self._format = pa.paInt16
        self._channels = 1
        self._rate = 44100
        self._audio = pa.PyAudio()
        self._buffer_size = buffer_size

    def setup(self) -> None:
        self._stream = self._audio.open(
            format=self._format,
            channels=self._channels,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
        )

    def update(self) -> None:
        data = self._stream.read(self._chunk)
        dataInt = struct.unpack(str(self._chunk) + "h", data)
        fft = np.abs(np.fft.fft(dataInt)) * 2 / (11000 * self._chunk)
        ins = np.linspace(
            0, self._chunk, num=self._buffer_size, dtype=np.int32, endpoint=False
        )
        values_60 = fft[ins]
        values_60_int = (values_60 * 1000).astype(int)
        self._values = values_60_int

    def loop(self) -> None:
        while True:
            self.update()

    def get_values(self) -> list[int]:
        return self._values.tolist()


class _Serial:
    def __init__(self, port: str | None = None):
        if port is None:
            avail_ports = serial.tools.list_ports.comports()

            for i, p in enumerate(avail_ports):
                print(f"[{i}] {p}")

            port_num = int(input())
            port = avail_ports[port_num].name

        self._port = serial.Serial(port=port, baudrate=115200)

    def send(self, data: str) -> None:
        self._port.write(data.encode())


def smooth_ver(old: list, new: list, k: int) -> list[int | float]:
    k = 1 / k
    return list(
        map(
            lambda x: x[1] + (x[0] - x[1]) * k,
            # lambda x: (x[1] + x[0]) / 2,
            zip(new, old),
        )
    )


def smooth_hor(l: list, k: int) -> list[int | float]:
    """k is num of diodes in each size"""
    return [
        sum((l[h] for h in range(max(i - k, 0), min(i + k, len(l))))) // ((k + 1) * 2)
        for i in range(len(l))
    ]


def main() -> None:
    audio = _Audio()
    audio.setup()
    port = _Serial()

    vals = [0] * 60
    vals_prev = [0] * 60

    while True:
        audio.update()
        vals = audio.get_values()
        vals = smooth_ver(vals_prev, vals, 4)
        vals = smooth_hor(vals, 3)
        vals_prev = vals
        vals = list(reversed(vals)) + vals
        data = f"{{{'|'.join(map(lambda a: str(int(a)), vals))}}}"
        graph(vals_prev, 20, clear=True)
        port.send(data)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Goodbye!")
