import sys
from typing import Iterable

# full, empty = "▮▯"
full, empty = "▉░"


def graph(data: Iterable[int | float], max_length: int, clear: bool = False) -> None:
    """
    Print a graph based on the input data.

    Args:
        data: An iterable containing numbers to be plotted on the graph.
        max_length: The maximum length of the graph.
        clear: A boolean indicating whether to clear the console before printing the graph.

    Returns:
        None
    """
    graph_string = ""

    for y in range(max_length):
        for x in data:
            graph_string += full if (max_length - x) <= y else empty

        graph_string += "\n"

    if clear:
        graph_string = f"\x1b[{max_length + 1}A\x1b[2K" + graph_string
    print(graph_string, end="")
