__all__ = ["Audio", "smooth_ver", "smooth_hor", "fade_np", "fade", "smooth", "bounds"]

import struct
from typing import Iterable, Sequence

import numpy as np
import pyaudio as pa


class Audio:
    @staticmethod
    def select() -> str | int | float | None:
        temp_audio = pa.PyAudio()
        device_count = temp_audio.get_device_count()

        for i in range(device_count):
            device = temp_audio.get_device_info_by_index(i)
            if device.get("maxInputChannels"):
                print(f"[{i}] {device.get('name')}")

        index = int(input())
        port: str | int | float | None = temp_audio.get_device_info_by_index(index).get(
            "name"
        )
        return port

    @staticmethod
    def select_by_name(name: str) -> int | None:
        temp_audio = pa.PyAudio()
        device_count = temp_audio.get_device_count()

        filtered = []
        for i in range(device_count):
            device = temp_audio.get_device_info_by_index(i)
            if device.get("maxInputChannels"):
                device_name = device.get("name")

                if not isinstance(device_name, str):
                    continue

                if name in device_name:
                    filtered.append(i)

        if len(filtered) == 0:
            return None

        return filtered[0]

    def __init__(self, buffer_size: int = 60) -> None:
        self._chunk = 1024
        self._format = pa.paInt16
        self._channels = 1
        self._rate = 44100
        self._audio = pa.PyAudio()
        self._buffer_size = buffer_size

        self.device_index = 1

        self._stream: pa.Stream
        self._values: np.ndarray

    def setup(self) -> None:
        self._stream = self._audio.open(
            input_device_index=self.device_index,
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
