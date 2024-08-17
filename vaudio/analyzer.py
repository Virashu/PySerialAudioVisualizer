from __future__ import annotations

__all__ = (
    "Analyzer",
    "AnalyzerRolling",
    "AnalyzerFFT",
    "AnalyzerRollingEase",
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


class Analyzer:
    """Base class for analyzers"""

    def __init__(self, audio: None | Audio = None) -> None:
        if audio:
            self.audio = audio
        else:
            self.audio = Audio()
            self.audio.setup()

    def update(self) -> None:
        self.audio.update()

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

    def __init__(self, audio: None | Audio = None) -> None:
        super().__init__(audio)
        self.values: FloatArray = np.ndarray((60,), float)

    def update(self) -> None:
        super().update()

        avg = int(np.mean(self.audio.get_values_np(60)))
        avg = min(max(avg * 0.8, 0), 255 - 50)

        self.values = np.concatenate(([avg], self.values[0:-1]))
        self.values = fade_np(self.values, 0.002)
        self.values = smooth(self.values, 2)

    def get_data(self) -> FloatArray:
        values_adj = self.values**2
        values_adj = np.clip(values_adj, 0, 255)
        return values_adj

    def get_data_mirrored(self) -> FloatArray:
        v = self.get_data()
        return np.concatenate((np.flip(v), v))


class AnalyzerFFT(Analyzer):
    """Analyze audio with Fast Fourier Transform (by frequency)"""

    def __init__(self, audio: Audio | None = None) -> None:
        super().__init__(audio)
        self.fft: FloatArray = np.ndarray((60,), float)

    def update(self) -> None:
        super().update()
        fft_prev: FloatArray = self.fft
        self.fft = self.audio.get_values_np(60)
        self.fft = np.array(
            smooth_ver_directional(fft_prev, self.fft, 0.6, 1e-9),
            dtype=float,
        )
        sm: list[int | float] = smooth_hor(list(self.fft), 1)
        self.fft = np.array(sm)

    def get_data(self) -> FloatArray:
        return self.fft

    def get_data_mirrored(self) -> FloatArray:
        return np.concatenate((np.flip(self.fft), self.fft))


class AnalyzerRollingEase(Analyzer):
    """Create audio 'waves' - using standard smooth method"""

    def __init__(self, audio: Audio | None = None) -> None:
        super().__init__(audio)
        self.values: FloatArray = np.ndarray((60,), float)

    def update(self) -> None:
        super().update()

        avg = int(np.mean(self.audio.get_values_np(60)))
        avg = min(max(avg * 0.8, 0), 255 - 50)
        new = avg

        prv = self.values[0]
        val = prv + (new - prv) * 0.3

        self.values = np.concatenate(([val], self.values[0:-1]))
        self.values = fade_np(self.values, 0.002)
        # self.values = smooth(self.values, 3, 0.9)

    def get_data(self) -> FloatArray:
        values_adj = self.values**2
        values_adj = np.clip(values_adj, 0, 255)
        return values_adj

    def get_data_mirrored(self) -> FloatArray:
        v = self.get_data()
        return np.concatenate((np.flip(v), v))
