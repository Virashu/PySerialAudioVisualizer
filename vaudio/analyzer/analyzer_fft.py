import numpy as np

from .analyzer import Analyzer
from ..av_audio import Audio, smooth_ver, smooth_hor


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
