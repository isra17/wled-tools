from rich import print
import json
import requests
import enum
import typing as t
import typer

app = typer.Typer()
wled_url: str

class Scope(enum.Enum):
    CONFIG = "cfg"
    STATE = "state"
    INFO = "info"
    EFFECTS = "eff"
    PALETTES = "pal"
    PRESETS = "presets"

@app.command()
def get():
    if api_url.endswith("/presets"):
        print(requests.get(wled_url + "/presets.json").json())
    else:
        print(requests.get(api_url).json())

@app.command()
def set(
    value: t.Annotated[t.Optional[str], typer.Option()] = None,
    file: t.Annotated[t.Optional[typer.FileText], typer.Option()] = None
) -> None:
    if api_url.endswith("/presets"):
        assert file
        print(requests.post(wled_url + "/upload", files={"data": ("/presets.json", file)}).text)
        return

    try:
        if value:
            data = json.loads(value)
            print(requests.post(api_url, json={"v": True} | data).json())
        if file:
            data = json.load(file)
            print(requests.post(api_url, json={"v": True} | data).json())
    except Exception as e:
        breakpoint()
        pass

@app.command()
def update(
    file: typer.FileBinaryRead
) -> None:
    requests.post(wled_url + "/update", files={"update": file})

@app.callback()
def main(url: str, scope: t.Annotated[t.Optional[Scope], typer.Option()]=None):
    global wled_url
    global api_url

    wled_url = url.rstrip("/")
    url = wled_url + "/json/"
    if scope:
        url += scope.value.lstrip("/")
    api_url = url

if __name__ == "__main__":
    app()

