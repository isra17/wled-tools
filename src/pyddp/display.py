import typing as t
import dataclasses
from pyddp import protocol

T = t.TypeVar("T")


def grouper(iterable: t.Iterable[T], n: int) -> t.Iterable[list[T]]:
    return zip(*([iter(iterable)] * n))


@dataclasses.dataclass
class Pixel:
    r: int = 0
    g: int = 0
    b: int = 0

    def as_tuple(self) -> tuple[int, int, int]:
        return self.r, self.g, self.b

    @classmethod
    def from_raw(cls, data: bytes) -> list["Pixel"]:
        pixels: list[Pixel] = []
        for pixel_data in grouper(data, 3):
            pixels.append(cls(*pixel_data))
        return pixels


class VirtualDisplay:
    def __init__(self) -> None:
        self.framebuffer: list[Pixel] = []
        self.protocol = protocol.DDP()

    def feed_packet(self, data: bytes) -> None:
        packet = self.protocol.parse_packet(data)
        # Only support WLED DDP format right now.
        pixels = Pixel.from_raw(packet.data)
        start = packet.data_offset // 3
        if len(self.framebuffer) < start:
            self.framebuffer.extend([Pixel() for _ in range(packet.data_offset)])

        end = start + packet.data_size // 3
        self.framebuffer[start:end] = pixels
