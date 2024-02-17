__all__ = ["Analyzer", "AnalyzerRolling", "AnalyzerFFT"]

from abc import abstractmethod

import numpy as np
from .av_audio import Audio, smooth_ver, smooth_hor, fade_np, smooth


class Analyzer:
    def __init__(self, audio: None | Audio = None) -> None:
        if audio:
            self.audio = audio
        else:
            self.audio = Audio()
            self.audio.setup()

    def update(self) -> None:
        self.audio.update()

    @abstractmethod
    def get_data(self): ...

    @abstractmethod
    def get_data_mirrored(self): ...


class AnalyzerRolling(Analyzer):
    def __init__(self, audio: None | Audio = None) -> None:
        super().__init__(audio)
        self.values: np.ndarray = np.ndarray((60,), float)

    def update(self) -> None:
        super().update()
        avg = int(np.average(self.audio.get_values_np()))
        avg = min(max(avg, 0), 255)

        self.values = np.concatenate(([avg], self.values[0:-1]))
        self.values = fade_np(self.values, 0.001)
        self.values = smooth(self.values, 2)

    def get_data(self) -> np.ndarray:
        values_adj = self.values**2
        values_adj = np.clip(values_adj, 0, 255)
        return values_adj

    def get_data_mirrored(self) -> np.ndarray:
        v = self.get_data()
        return np.concatenate((np.flip(v), v))


class AnalyzerFFT(Analyzer):
    def __init__(self, audio: None | Audio = None) -> None:
        super().__init__(audio)
        self.fft: np.ndarray = np.ndarray((60,), float)

    def update(self) -> None:
        super().update()
        fft_pr: np.ndarray = self.fft
        self.fft: np.ndarray = self.audio.get_values_np()
        self.fft: np.ndarray = np.array(smooth_ver(fft_pr, self.fft, 4))
        sm: list[int | float] = smooth_hor(self.fft, 3)  # type: ignore
        self.fft: np.ndarray = np.array(sm)

    def get_data(self) -> np.ndarray:
        return self.fft

    def get_data_mirrored(self) -> np.ndarray:
        return np.concatenate((np.flip(self.fft), self.fft))
