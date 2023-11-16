"""PyAudio Example: Play a wave file."""

import pyaudio
import wave


CHUNK = 512

wf = wave.open("kuro.wav", "rb")
p = pyaudio.PyAudio()

stream = p.open(
    format=p.get_format_from_width(wf.getsampwidth()),
    channels=wf.getnchannels(),
    rate=wf.getframerate(),
    output=True,
)

while len(data := wf.readframes(CHUNK)):  # Requires Python 3.8+ for :=
    stream.write(data)

stream.close()
p.terminate()
