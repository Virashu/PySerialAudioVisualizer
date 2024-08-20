from __future__ import annotations

__all__ = [
    "Audio",
    "smooth_ver",
    "smooth_hor",
    "fade_np",
    "fade",
    "smooth",
    "bounds",
    "smooth_ver_directional",
]

import struct
from typing import TYPE_CHECKING, Any, Iterable, Sequence

import numpy as np
import pyaudio as pa

if TYPE_CHECKING:
    from .typing import FloatArray


class Audio:
    @staticmethod
    def select() -> str | None:
        temp_audio = pa.PyAudio()
        device_count = temp_audio.get_device_count()

        for i in range(device_count):
            device = temp_audio.get_device_info_by_index(i)
            if device.get("maxInputChannels"):
                print(f"[{i}] {device.get('name')}")  # noqa: T201 (for user interaction)

        index = int(input())
        _x: Any = temp_audio.get_device_info_by_index(index).get("name")

        if not isinstance(_x, str):
            return None

        port: str = _x

        return port

    @staticmethod
    def select_by_name(name: str) -> int | None:
        temp_audio = pa.PyAudio()
        device_count = temp_audio.get_device_count()

        filtered: list[int] = []
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

    def __init__(self) -> None:
        self._chunk = 1024
        self._format = pa.paInt16
        self._channels = 1
        self._rate = 44100
        self._audio = pa.PyAudio()
        self._k = 1000  # Koefficient for multiplying

        self.device_index = 1

        self._stream: pa.Stream
        self._fft: FloatArray

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
        # Read raw wave data
        data: bytes = self._stream.read(self._chunk)
        data_int = struct.unpack(f"{self._chunk}h", data)

        # Calculate FFT
        fft = np.abs(np.fft.fft(data_int))

        self._fft = fft * 2 / (11000 * self._chunk)

    def loop(self) -> None:
        while True:
            self.update()

    def get_values(self, n: int = 100) -> list[int | float]:
        return self.get_values_np(n).tolist()

    def get_values_np(self, n: int = 100) -> FloatArray:
        # ins: IntArray = np.linspace(0, self._chunk, n, dtype=int, endpoint=False)
        # values_60: FloatArray = self._fft[ins]

        # values = np.array([n.mean() for n in np.array_split(self._fft, n)])

        values: FloatArray = np.resize(self._fft, n)

        return (values * self._k).astype(float)


def smooth_ver(
    old: Iterable[int | float], new: Iterable[int | float], k: float
) -> list[int | float]:
    """Make numbers go up and down smoothly

    k: koefficient of smoothing
    """

    k = 1 / k
    return [y + (x - y) * k for x, y in zip(new, old)]


def smooth_ver_directional(
    old: Iterable[int | float], new: Iterable[int | float], k_up: float, k_down: float
) -> list[int | float]:
    """Make numbers go up and down smoothly

    k: koefficient of smoothing (0-1)
    """

    return [y + (x - y) * (k_up if (x > y) else k_down) for x, y in zip(new, old)]


def smooth_hor(list_: Sequence[int | float], k: int) -> list[int | float]:
    """Moving average

    k: the size of the half-window (in one side)
    """
    return [
        sum(list_[h] for h in range(max(i - k, 0), min(i + k, len(list_))))
        // ((k + 1) * 2 - list_[max(i - k, 0) : min(i + k, len(list_))].count(0))
        for i in range(len(list_))
    ]


def smooth_hor_fix(list_: Sequence[int | float], k: int) -> list[int | float]:
    """Moving average

    k: the size of the half-window (in one side)
    """
    return [
        sum(list_[max(i - k, 0) : min(i + k, len(list_))]) // (k * 2 + 1)
        for i in range(len(list_))
    ]


def fade(list_: list[int | float]) -> list[int | float]:
    """Make numbers smaller with index

    [10, 10, 10] -> [9, 8, 7]
    """

    return [max(list_[i] - i, 0) for i in range(len(list_))]


def fade_np(arr: FloatArray, amount: float = 1) -> FloatArray:
    """Make numbers smaller with index

    arr: Array of numbers
    amount: Amount of fading (default = 1)

    Examples:
        [10, 10, 10] -> [9, 8, 7]

    """

    # Creates something similar to [1, 2, 3] if amount == 1
    # and [2, 4, 6] if amount == 2, etc.
    mask: FloatArray = np.arange(len(arr)) * amount

    # Subtract and constrain at 0
    a: FloatArray = arr - mask
    a[a < 0] = 0

    return a


def bounds(list_: list[int | float]) -> list[int | float]:
    """Constrain values in list between 0 and 255"""
    return [min(max(i, 0), 255) for i in list_]


def smooth(y: FloatArray, box_pts: int, amt: float = 1.0) -> FloatArray:
    """Smooth a numpy array with a box filter"""

    box = np.full(box_pts, amt) / box_pts
    return np.convolve(y, box, mode="same")


# def smooth_h(y: FloatArray, box_pts: int, amt: float = 1.0) -> FloatArray:
#     res: FloatArray = np.ndarray(y.shape)

#     for i in range(y.size):
