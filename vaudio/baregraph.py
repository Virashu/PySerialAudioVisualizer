import requests
import graph
from time import sleep


while True:
    r = requests.get("http://127.0.0.1:7777/")
    data = r.json().get("data")
    graph.graph(data, 20, clear=True)
    sleep(0.01)
