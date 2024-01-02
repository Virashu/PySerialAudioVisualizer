from .server import App, Request, Response


def serve(data: dict[str, str]):
    gdata: dict[str, str] = data
    app = App()

    @app.get("/")
    def _(req: Request, res: Response) -> None:
        nonlocal gdata
        data = gdata.get("data")
        if data:
            pt = list(map(int, data.strip("{").rstrip("}").split("|")))
            res.send({"data": pt})

    try:
        app.listen("0.0.0.0", 7777)
    except KeyboardInterrupt:
        pass
