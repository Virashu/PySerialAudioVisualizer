import pyaudio

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

audio = pyaudio.PyAudio()
devices = [
        audio.get_device_info_by_index(i) for i in range(audio.get_device_count())
        ]

for dev in devices:
    print('|', dev['index'], '\t', dev['name'])

