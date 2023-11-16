import numpy as np
import pyaudio as pa
import struct
import matplotlib.pyplot as plt
import soundcard as sc


CHUNK = 1024 * 1
CHANNELS = 1
RATE = 44100

mics = sc.all_microphones(include_loopback=True)

for i, m in enumerate(mics):
    print(f"{i}: {m.name}")

s = int(input())
default_mic = mics[s]


fig, (ax, ax1) = plt.subplots(2)
x_fft = np.linspace(0, RATE, CHUNK)
x = np.arange(0, 2 * CHUNK, 2)
(line,) = ax.plot(x, np.random.rand(CHUNK), "r")
(line_fft,) = ax1.semilogx(x_fft, np.random.rand(CHUNK), "b")
ax.set_ylim(-32000, 32000)
ax.ser_xlim = (0, CHUNK)
ax1.set_xlim(20, RATE / 2)
ax1.set_ylim(0, 1)
fig.show()

while 1:
    with default_mic.recorder(samplerate=RATE, channels=CHANNELS) as mic:
        data = mic.record(numframes=CHUNK)
        dataInt = data * 100
        print(dataInt)
        line.set_ydata(dataInt)
        fft = np.abs(np.fft.fft(dataInt)) * 2 / (11000 * CHUNK)
        line_fft.set_ydata(fft)
        fig.canvas.draw()
        fig.canvas.flush_events()
