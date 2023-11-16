# import numpy as np 
# import pyaudio as pa 
# import struct 
# import matplotlib.pyplot as plt 

# CHUNK = 1024 * 2
# FORMAT = pa.paInt16
# CHANNELS = 1
# RATE = 44100 # in Hz

# p = pa.PyAudio()

# stream = p.open(
#     # output_device_index=,
#     format = FORMAT,
#     channels = CHANNELS,
#     rate = RATE,
#     input=True,
#     output=True,
#     frames_per_buffer=CHUNK
# )



# fig,ax = plt.subplots()
# x = np.arange(0,2*CHUNK,2)
# line, = ax.plot(x, np.random.rand(CHUNK),'r')
# ax.set_ylim(-60000,60000)
# ax.ser_xlim = (0,CHUNK)
# fig.show()

# while 1:
#     data = stream.read(CHUNK)
#     dataInt = struct.unpack(str(CHUNK) + 'h', data)
#     line.set_ydata(dataInt)
#     fig.canvas.draw()
#     fig.canvas.flush_events()


import numpy as np #importing Numpy with an alias np
import pyaudio as pa 
import struct 
import matplotlib.pyplot as plt 
import soundcard as sc
import time


CHUNK = 1024 * 1
FORMAT = pa.paInt16
CHANNELS = 1
RATE = 44100 # in Hz

p = pa.PyAudio()
# get a list of all speakers:
speakers = sc.all_speakers()
# get the current default speaker on your system:
default_speaker = sc.default_speaker()

# get a list of all microphones:v
mics = sc.all_microphones(include_loopback=True)
# get the current default microphone on your system:
default_mic = mics[0]

for i in range(len(mics)):
    try:
        print(f"{i}: {mics[i].name}")
    except Exception as e:
        print(e)

# stream = p.open(
#     format = FORMAT,
#     channels = CHANNELS,
#     rate = RATE,
#     input=True,
#     output=True,
#     frames_per_buffer=CHUNK
# )

fig, (ax,ax1) = plt.subplots(2)
x_fft = np.linspace(0, RATE, CHUNK)
x = np.arange(0,2*CHUNK,2)
line, = ax.plot(x, np.random.rand(CHUNK),'r')
line_fft, = ax1.semilogx(x_fft, np.random.rand(CHUNK), 'b')
ax.set_ylim(-32000,32000)
ax.ser_xlim = (0,CHUNK)
ax1.set_xlim(20,RATE/2)
ax1.set_ylim(0,1)
fig.show()

while 1:
    # data = stream.read(CHUNK)
    with default_mic.recorder(samplerate=RATE, channels=CHANNELS) as mic:
        print("Recording...")
        data = mic.record(numframes=CHUNK)
        print(data)
        # print("Done...Stop your sound so you can hear playback")
        # time.sleep(5)
        # sp.play(data)
        dataInt = struct.unpack(str(CHUNK) + 'h', data)
        line.set_ydata(dataInt)
        line_fft.set_ydata(np.abs(np.fft.fft(dataInt))*2/(11000*CHUNK))
        fig.canvas.draw()
        fig.canvas.flush_events()





