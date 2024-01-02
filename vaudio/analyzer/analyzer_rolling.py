import numpy as np

from .analyzer import Analyzer
from ..av_audio import Audio, fade_np, smooth


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
