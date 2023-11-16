import numpy as np
import pyaudio as pa

import struct

__all__ = ["Audio", "smooth_ver", "smooth_hor"]


class Audio:
    def __init__(self, buffer_size: int = 60) -> None:
        self._chunk = 1024
        self._format = pa.paInt16
        self._channels = 1
        self._rate = 44100
        self._audio = pa.PyAudio()
        self._buffer_size = buffer_size

    def setup(self) -> None:
        self._stream = self._audio.open(
            input_device_index=1,
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

    def get_values(self) -> list[int | float]:
        return self._values.tolist()

    def get_values_np(self) -> np.ndarray:
        return self._values


def smooth_ver(
    old: list[int | float], new: list[int | float], k: int | float
) -> list[int | float]:
    k = 1 / k
    return list(
        map(
            lambda x: x[1] + (x[0] - x[1]) * k,
            zip(new, old),
        )
    )


def smooth_hor(l: list[int | float], k: int) -> list[int | float]:
    """k is num of diodes in each direction"""
    return [
        sum((l[h] for h in range(max(i - k, 0), min(i + k, len(l))))) // ((k + 1) * 2)
        for i in range(len(l))
    ]


def fade(l: list[int | float]) -> list[int | float]:
    return [l[i] - i for i in range(len(l))]


def bounds(l: list[int | float]) -> list[int | float]:
    return [min(max(i, 0), 255) for i in l]
