import logging
import os
import sys
from pathlib import Path

from .vaudio import AudioVisualizer

ROOT: str = str(Path(__file__).parent.parent.resolve())

logging.getLogger("http.server").setLevel(logging.WARNING)
logging.getLogger("saaba").setLevel(logging.WARNING)

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
    null = Path(os.devnull).open("w")  # noqa: SIM115
    # (the file should be open till the end of execution)

    sys.stdout = null
    sys.stderr = null

# logger.addHandler(logging.FileHandler("vaudio.log"))

logger.setLevel(logging.INFO)


def main() -> None:
    visualizer = AudioVisualizer()

    print("\x1b[?25l", end="")  # Hide cursor

    try:
        visualizer.run()

    except KeyboardInterrupt:
        visualizer.stop()

        print("\x1b[2J\x1b[H", end="")  # Clear
        print("Goodbye!")

    except Exception as e:
        with Path(f"{ROOT}/crash.log").open("w") as f:
            f.write(str(e))
        logger.exception("Uncaught exception")

    finally:
        print("\x1b[?25h", end="")  # Show cursor
