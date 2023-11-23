from graph import graph


while True:
    with open("D:/_temp/tmp/vis/data.txt", "r") as f:
        data = f.read().strip("{").rstrip("}")
    if data:
        pt = list(map(int, data.split("|")))
        graph(pt, 20, clear=True)
