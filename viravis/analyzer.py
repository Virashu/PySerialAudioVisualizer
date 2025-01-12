from __future__ import annotations

__all__ = (
    "Analyzer",
    "AnalyzerRolling",
    "AnalyzerFFT",
    "AnalyzerRollingEase",
    "AnalyzerFlat",
)

from abc import abstractmethod
from typing import TYPE_CHECKING

import numpy as np

from .av_audio import (
    Audio,
    fade_np,
    smooth,
    smooth_hor,
    smooth_ver_directional,
)

if TYPE_CHECKING:
    from .typing import FloatArray


def constrain(n: float, min_: float, max_: float) -> float:
    return min(max(n, min_), max_)


class Analyzer:
    """Base class for analyzers"""

    def __init__(self, size: int, audio: None | Audio = None) -> None:
        if audio:
            self.audio = audio
        else:
            self.audio = Audio()
            self.audio.setup()

        self.size: int = size
        self.levels: FloatArray = np.full(100, 0.0, float)
        self.level: float = 1

    def update(self) -> None:
        self.audio.update()

        max_: float = max(float(np.max(self.get_data())), 1.0)
        self.levels = np.concatenate(([max_], self.levels[:-1]))
        self.level = float(np.mean(self.levels))

    @abstractmethod
    def get_data(self) -> FloatArray:
        """Get analyzed data array"""

    @abstractmethod
    def get_data_mirrored(self) -> FloatArray:
        """Get analyzed data array, mirrored

        [1, 2, 3] -> [3, 2, 1, 1, 2, 3]
        """


class AnalyzerRolling(Analyzer):
    """Create audio 'waves'"""

    def __init__(self, size: int, audio: None | Audio = None) -> None:
        super().__init__(size, audio)
        self.values: FloatArray = np.ndarray((self.size,), float)
        self.fade_k = 1 / (3 * 10e4) * self.size

    def update(self) -> None:
        super().update()

        avg = int(np.mean(self.audio.get_values_np(self.size)))
        # avg = min(max(avg * 0.8, 0), 255 - 50)
        avg = constrain(avg * 0.8, 0, 255)

        nonzero: FloatArray = self.values[self.values != 0]

        if len(nonzero):
            baseline: float = float(np.mean(nonzero))
        else:
            baseline = 1.0

        self.values = np.concatenate(([avg / baseline], self.values[0:-1]))
        self.values = fade_np(self.values, 0.002)
        self.values = smooth(self.values, 2)

    def get_data(self) -> FloatArray:
        values_adj = self.values
        values_adj = values_adj / self.level * 10
        return np.clip(values_adj, 0, 255)

    def get_data_mirrored(self) -> FloatArray:
        v = self.get_data() * 2
        return np.concatenate((np.flip(v), v))


class AnalyzerFFT(Analyzer):
    """Analyze audio with Fast Fourier Transform (by frequency)"""

    def __init__(self, size: int, audio: Audio | None = None) -> None:
        super().__init__(size, audio)
        self.fft: FloatArray = np.ndarray((self.size,), float)

    def update(self) -> None:
        super().update()
        fft_prev: FloatArray = self.fft
        self.fft = self.audio.get_values_np(self.size)
        self.fft = np.array(
            smooth_ver_directional(fft_prev, self.fft, 0.6, 1e-3),
            dtype=float,
        )
        sm: list[int | float] = smooth_hor(list(self.fft), 2)
        self.fft = np.array(sm)

    def get_data(self) -> FloatArray:
        return self.fft / self.level * 10

    def get_data_mirrored(self) -> FloatArray:
        return np.concatenate((np.flip(self.fft), self.fft))


class AnalyzerRollingEase(Analyzer):
    """Create audio 'waves' - using standard smooth method"""

    def __init__(self, size: int, audio: Audio | None = None) -> None:
        super().__init__(size, audio)
        self.values: FloatArray = np.ndarray((self.size,), float)

    def update(self) -> None:
        super().update()

        avg = int(np.mean(self.audio.get_values_np(self.size)))
        avg = min(max(avg * 0.8, 0), 255 - 50)
        new = avg

        prv = self.values[0]
        val = prv + (new - prv) * 0.3

        self.values = np.concatenate(([val], self.values[0:-1]))
        self.values = fade_np(self.values, 0.002)
        # self.values = smooth(self.values, 3, 0.9)

    def get_data(self) -> FloatArray:
        values_adj = self.values**2
        return np.clip(values_adj, 0, 255)

    def get_data_mirrored(self) -> FloatArray:
        v = self.get_data()
        return np.concatenate((np.flip(v), v))


class AnalyzerFlat(Analyzer):
    """Flat"""

    def __init__(self, size: int, audio: Audio | None = None) -> None:
        super().__init__(size, audio)
        self.current: float = 0.0
        self.value: float = 0.0
        self.history: FloatArray = np.ndarray(10, float)

    def update(self) -> None:
        super().update()

        avg = int(np.mean(self.audio.get_values_np(self.size)))
        new: float = min(max(avg * 0.8, 0), 255 - 50)

        prv: float = self.history[0]
        self.current = prv + (new - prv) * 0.1

        self.history = np.concatenate(([self.current], self.history[:-1]))

        self.value = avg

        # self.values = smooth(self.values, 3, 0.9)

    def get_data(self) -> FloatArray:
        values = np.full(self.size, self.current, float)
        values_adj = values**2
        return np.clip(values_adj, 0, 255, dtype=float)

    def get_data_mirrored(self) -> FloatArray:
        v = self.get_data()
        return np.concatenate((np.flip(v), v))
