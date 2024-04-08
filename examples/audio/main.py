from matplotlib import pyplot as plt
from vaudio.av_audio import Audio

__a = Audio()
i = __a.select_by_name("Stereo Mix")
__a.device_index = i
__a.setup()

plt.show(block=False)

try:
    while True:
        plt.xlim(0, 100)
        plt.ylim(-100, 100)

        plt.xticks(range(0, 100, 10))
        plt.yticks(range(-100, 100, 100))
        # vals = __a.get_values_np(1024)
        # plt.plot(range(len(vals)), vals)

        __a.update()
        vals = __a.get_values_np(60)

        plt.plot(range(len(vals)), vals)

        plt.pause(0.01)
        plt.clf()
except KeyboardInterrupt:
    pass
