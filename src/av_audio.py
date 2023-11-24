from typing import Collection, Iterable, Sequence, Sized, Union
import numpy as np
import pyaudio as pa

import struct

__name__ = "AudioVisualizer_Audio"
__all__ = ["Audio", "smooth_ver", "smooth_hor", "fade_np", "fade", "smooth", "bounds"]


class Audio:
    @staticmethod
    def select() -> str:
        ...

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
    old: Iterable[int | float], new: Iterable[int | float], k: int | float
) -> list[int | float]:
    k = 1 / k
    return list(
        map(
            lambda x: x[1] + (x[0] - x[1]) * k,
            zip(new, old),
        )
    )


def smooth_hor(l: Sequence[int | float], k: int) -> list[int | float]:
    """k is num of diodes in each direction"""
    return list(
        (
            sum((l[h] for h in range(max(i - k, 0), min(i + k, len(l)))))
            // ((k + 1) * 2)
            for i in range(len(l))
        )
    )


def fade(l: list[int | float]) -> list[int | float]:
    return [l[i] - i for i in range(len(l))]


def fade_np(l: np.ndarray, amount: float = 1) -> np.ndarray:
    a = l - (np.arange(len(l)) * amount)
    a[a < 0] = 0

    return a


def bounds(l: list[int | float]) -> list[int | float]:
    return [min(max(i, 0), 255) for i in l]


def smooth(y, box_pts):
    box = np.ones(box_pts) / box_pts
    y_smooth = np.convolve(y, box, mode="same")
    return y_smooth
