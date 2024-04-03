__all__ = ["Analyzer", "AnalyzerRolling", "AnalyzerFFT"]

from abc import abstractmethod

import numpy as np

from .av_audio import Audio, smooth_ver, smooth_hor, fade_np, smooth
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

        [1, 2, 3] -> [3, 2, 1, 1, 2, 3]"""


class AnalyzerRolling(Analyzer):
    """Create audio 'waves'"""

    def __init__(self, audio: None | Audio = None) -> None:
        super().__init__(audio)
        self.values: FloatArray = np.ndarray((60,), float)

    def update(self) -> None:
        super().update()

        avg = int(np.average(self.audio.get_values_np()))
        avg = min(max(avg, 0), 255)

        self.values = np.concatenate(([avg], self.values[0:-1]))
        self.values = fade_np(self.values, 0.001)
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
        self.fft = self.audio.get_values_np()
        self.fft = np.array(smooth_ver(fft_prev, self.fft, 4))
        sm: list[int | float] = smooth_hor(self.fft, 3)
        self.fft = np.array(sm)

    def get_data(self) -> FloatArray:
        return self.fft

    def get_data_mirrored(self) -> FloatArray:
        return np.concatenate((np.flip(self.fft), self.fft))
