import json
from time import sleep
from urllib import request

import viravis.graph as graph


def get(url: str) -> str:
    with request.urlopen(url) as r:
        return r.read().decode("utf-8")


while True:
    r = get("http://127.0.0.1:7777")
    data = json.loads(r).get("data")
    graph.graph(data, 20, clear=True)
    sleep(0.01)
