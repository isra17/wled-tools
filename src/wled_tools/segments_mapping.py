from .segment import Segment
import typing as t
import math
import dataclasses
from .mapping import Mapping, Point

def _abs_rad(rad: float) -> float:
    return (rad + math.tau) % math.tau

@dataclasses.dataclass
class PolarCoord:
    radius: float
    theta: float

    @classmethod
    def from_vector(cls, point: Point) -> "PolarCoord":
        return cls(
            radius=point.length,
            theta=point.angle,
        )

    def to_state_dict(self) -> dict:
        theta = int(_abs_rad(self.theta) / math.pi * 32767)
        return {
            "radius": int(self.radius),
            "theta": theta
        }

@dataclasses.dataclass
class SegmentMapping:
    from_: PolarCoord
    to: PolarCoord
    pixels_count: int
    skip_pixels: int

    def __post_init__(self):
        if self.from_.radius == 0:
            self.from_.theta = self.to.theta

        if self.to.radius == 0:
            self.to.theta = self.from_.theta

    def to_state_dict(self) -> dict:
        return {
            "from": self.from_.to_state_dict(),
            "to": self.to.to_state_dict(),
        }

@dataclasses.dataclass
class SegmentGroup:
    offset: int
    count: int
    reverse: bool = False

@dataclasses.dataclass
class SegmentsMapping:
    segments: list[SegmentMapping]
    wled_segments: list[Segment] = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        self.wled_segments = []
        pixels_count = 0
        for i, segment in enumerate(self.segments):
            self.wled_segments.append(Segment(
                id=i,
                start=pixels_count + segment.skip_pixels,
                stop=pixels_count + segment.skip_pixels + segment.pixels_count,
            ))
            pixels_count += segment.pixels_count + segment.skip_pixels

    @classmethod
    def from_mapping(cls, *, mapping: Mapping, center: Point) -> "SegmentsMapping":
        return cls(
            segments=[
                SegmentMapping(
                    from_=PolarCoord.from_vector(segment.from_ - center),
                    to=PolarCoord.from_vector(segment.to - center),
                    pixels_count=segment.pixels_count,
                    skip_pixels=segment.skip_pixels,
                ) for segment in mapping.segments
            ]
        )

    def to_config_dict(self) -> dict:
        return {
            "um": {
                "segmap": {
                    "seg": [
                        segment.to_state_dict() for segment in self.segments
                    ],
                },
            }
        }

    def wled_group_segments(self, groups: list[SegmentGroup]) -> t.Iterator[Segment]:
        for i, group in enumerate(groups):
            start = self.wled_segments[group.offset]
            end = self.wled_segments[group.offset + group.count - 1]
            yield Segment(
                id=i,
                start=start.start,
                stop=end.stop,
                reverse=group.reverse,
            )
