import typing as t
from . import display
import socketserver


class DDPHandler(socketserver.BaseRequestHandler):
    server: "DDPServer"

    def handle(self):
        try:
            # self.request is the TCP socket connected to the client
            data = self.request[0]
            self.server.display.feed_packet(data)
        except (Exception, KeyboardInterrupt):
            raise
        except BaseException as e:
            raise KeyboardInterrupt from e


class DDPServer(socketserver.UDPServer):
    def __init__(self, *, host: str, port: int):
        super().__init__((host, port), DDPHandler)
        self.display = display.VirtualDisplay()


if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 4048
    with DDPServer(host=HOST, port=PORT) as server:
        server.serve_forever()
