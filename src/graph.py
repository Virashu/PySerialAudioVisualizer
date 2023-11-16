import sys

# full, empty = "▮▯"
full, empty = "▉░"


def graph(l: list[int | float], m: int, clear: bool = False) -> None:
    if clear:
        # erases (m + 1) lines above the cursor
        sys.stdout.write(f"\x1b[{m + 1}A\x1b[2K")
        # erases entire screen (laggy)
        # sys.stdout.write("\x1b[2J")
    p = ""
    for y in range(m):
        for x in range(len(l)):
            p += full if (m - l[x]) <= y else empty
        p += "\n"
    print(p)
