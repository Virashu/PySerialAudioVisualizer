from server import App


app = App()


@app.get("/")
def _(req, res):
    with open("D:/_temp/tmp/vis/data.txt", "r") as f:
        data = f.read().strip("{").rstrip("}")
    pt = list(map(int, data.split("|")))
    # print(pt)
    print("GET", req.client)
    res.send({"data": pt})


try:
    app.listen("0.0.0.0", 7777)
except KeyboardInterrupt:
    ...
