import pyaudio
from pprint import pformat


def get_devices(audio: pyaudio.PyAudio) -> list:
    devices_count = audio.get_device_count()
    devices = [audio.get_device_info_by_index(i) for i in range(devices_count)]
    return devices


p = pyaudio.PyAudio()
print(pformat(get_devices(p)))
