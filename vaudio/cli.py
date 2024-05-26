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
    with open(os.devnull, "w", encoding="utf-8") as null:
        sys.stdout = null
        sys.stderr = null

# logger.addHandler(logging.FileHandler("vaudio.log"))

logger.setLevel(logging.INFO)


def main():
    try:
        visualizer = AudioVisualizer()
        visualizer.run()
    except KeyboardInterrupt:
        visualizer.stop()
        print("\x1b[2J\x1b[H", end="")
        print("Goodbye!")
    except Exception as e:
        logger.exception("Uncaught exception: %s", e)
    finally:
        print("\x1b[?25h", end="")
