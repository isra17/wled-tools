from typing_extensions import Annotated
import typer
import threading
from .server import DDPServer
import pyglet
from pyglet import shapes
from .mapping import Mapping
from .display import VirtualDisplay

class Viewer:
    def __init__(
        self,
        mapping: Mapping,
        display: VirtualDisplay,
    ) -> None:
        self.window = pyglet.window.Window(800, 800)
        self.batch = pyglet.graphics.Batch()
        self.display = display
        self.pixels = []

        for (start, end) in mapping.segments:
            for i in range(60):
                rate = i/60
                dx = rate * (end.x - start.x)
                dy = rate * (end.y - start.y)
                px = start.x + dx
                py = start.y + dy

                pixel = shapes.Circle(
                    px, py,
                    radius=1,
                    color=(255, 0, 0),
                    batch=self.batch
                )
                self.pixels.append(pixel)


        self.window.event(self.on_draw)

    def on_draw(self):
        for frame_pixel, display_pixel in zip(self.display.framebuffer, self.pixels):
            display_pixel.color = frame_pixel.as_tuple()

        self.window.clear()
        self.batch.draw()

    def run(self):
        pyglet.app.run()


def main(mapping_file: typer.FileText, port: int=4048):
    mapping = Mapping.from_file(mapping_file)
    server = DDPServer(host="0.0.0.0", port=port)
    viewer = Viewer(mapping=mapping, display=server.display)

    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    try:
        viewer.run()
    finally:
        server.shutdown()
        server_thread.join()


if __name__ == '__main__':
    typer.run(main)

