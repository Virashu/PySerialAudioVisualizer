import numpy as np
import pyaudio as pa
import struct
import matplotlib.pyplot as plt


class AudioE:
    def __init__(self, ui=False) -> None:
        self._chunk = 1024
        self._format = pa.paInt16
        self._channels = 1
        self._rate = 44100
        self.audio = pa.PyAudio()
        self.ui = ui
        self.leds = 60

    def setup(self) -> None:
        self.stream = self.audio.open(
            format=self._format,
            channels=self._channels,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
        )
        if self.ui:
            self.fig, (
                plot_wave,
                plot_fft,
                plot_fft_reduced,
            ) = plt.subplots(3)

            x = np.arange(0, 2 * self._chunk, 2)
            x_fft = np.linspace(0, self._rate, self._chunk)
            x_fft_reduced = np.arange(0, self.leds, dtype=int)

            (self.line,) = plot_wave.plot(x, np.random.rand(self._chunk), "r")
            (self.line_fft,) = plot_fft.semilogx(
                x_fft, np.random.rand(self._chunk), "b"
            )
            (self.line_fft_reduced,) = plot_fft_reduced.plot(
                x_fft_reduced, np.random.rand(self.leds), "g"
            )

            plot_wave.set_ylim(-32000, 32000)
            plot_wave.set_xlim(0, self._chunk)

            plot_fft.set_xlim(20, self._rate / 2)
            plot_fft.set_ylim(0, 1)

            plot_fft_reduced.set_ylim(0, 100)
            plot_fft_reduced.set_xlim(0, self.leds)

            self.fig.show()

    def loop(self) -> None:
        while True:
            data = self.stream.read(self._chunk)
            dataInt = struct.unpack(str(self._chunk) + "h", data)

            self.line.set_ydata(dataInt)

            fft = np.abs(np.fft.fft(dataInt)) * 2 / (11000 * self._chunk)
            ins = np.linspace(
                0, self._chunk, num=self.leds, dtype=np.int32, endpoint=False
            )

            values_60 = fft[ins]
            values_60_int = (values_60 * 1000).astype(int)

            self.line_fft_reduced.set_ydata(values_60_int)
            self.line_fft.set_ydata(fft)

            self.fig.canvas.draw()
            self.fig.canvas.flush_events()


if __name__ == "__main__":
    audioE = AudioE(ui=True)
    audioE.setup()
    audioE.loop()
