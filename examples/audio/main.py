# type: ignore[reportUnknownMemberType]

from typing import NoReturn

from matplotlib import pyplot as plt

from viravis.av_audio import Audio


def loop(audio: Audio) -> NoReturn:
    while True:
        plt.xlim(0, 100)
        plt.ylim(-100, 100)

        plt.xticks(range(0, 100, 10))
        plt.yticks(range(-100, 100, 100))

        audio.update()
        vals = audio.get_values_np(60)

        plt.plot(range(len(vals)), vals)

        plt.pause(0.01)
        plt.clf()


def main(device_name: str) -> None:
    audio = Audio()
    i = Audio.select_by_name(device_name)

    if not i:
        msg = "Device not found"
        raise ValueError(msg)

    audio.device_index = i
    audio.setup()

    try:
        plt.show(block=False)
        loop(audio)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    name = Audio.select()

    if name:
        main(name)
