import logging
import os
import sys

from .vaudio import AudioVisualizer

logging.getLogger("http.server").setLevel(logging.WARN)
logging.getLogger("saaba").setLevel(logging.WARN)

logger = logging.getLogger()

if "pythonw" not in sys.executable:
    formatter = logging.Formatter(
        "{levelname:<10} | {name:<32} | {message}",
        style="{",
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

else:
    null = open(os.devnull, "w", encoding="utf-8")

    sys.stdout = null
    sys.stderr = null

# logger.addHandler(logging.FileHandler("vaudio.log"))

logger.setLevel(logging.INFO)


def main():
    visualizer = AudioVisualizer()

    print("\x1b[?25l", end="")  # Hide cursor

    try:
        visualizer.run()

    except KeyboardInterrupt:
        visualizer.stop()

        print("\x1b[2J\x1b[H", end="")  # Clear
        print("Goodbye!")

    except Exception as e:
        logger.exception("Uncaught exception: %s", e)

    finally:
        print("\x1b[?25h", end="")  # Show cursor
