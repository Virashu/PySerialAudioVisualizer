from abc import abstractmethod

from ..av_audio import Audio


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
    def get_data(self):
        ...

    @abstractmethod
    def get_data_mirrored(self):
        ...
