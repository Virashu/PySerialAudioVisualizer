import logging
import sys
from .vaudio import AudioVisualizer

# logging.getLogger("http.server").setLevel(logging.CRITICAL)
logger = logging.getLogger()
formatter = logging.Formatter(
    "{levelname:<10} | {name:<32} | {message}",
    style="{",
)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)


def main():
    visualizer = AudioVisualizer()
    try:
        visualizer.run()
    except KeyboardInterrupt:
        visualizer.stop()
        print("\x1b[2J\x1b[H", end="")
        print("Goodbye!")
