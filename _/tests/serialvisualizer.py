import pyaudio

# import shutup


# shutup.please()

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

audio = pyaudio.PyAudio()
devices = [audio.get_device_info_by_index(i) for i in range(audio.get_device_count())]


print("Select device by index:")
for device in devices:
    index, name = device["index"], device["name"]
    print("|", index, "|", name)

selindex = int(input())
stream = audio.open(
    input_device_index=selindex,
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    frames_per_buffer=CHUNK,
    input=True,
)

try:
    while True:
        print(stream.read(CHUNK))
except KeyboardInterrupt:
    pass

stream.stop_stream()
stream.close()
audio.terminate()
