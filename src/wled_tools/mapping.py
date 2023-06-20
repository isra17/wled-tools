import math
import io
import typing as t
import json
import dataclasses

VerticeId = t.NewType("VerticeId", int)


@dataclasses.dataclass
class Point:
    x: float
    y: float

    def __add__(self, other: "Point") -> "Point":
        return self.__class__(
            x=self.x + other.x,
            y=self.y + other.y,
        )

    def __sub__(self, other: "Point") -> "Point":
        return self.__class__(
            x=self.x - other.x,
            y=self.y - other.y,
        )

    @property
    def length(self) -> float:
        return math.sqrt(self.x**2 + self.y**2)

    @property
    def angle(self) -> float:
        return math.atan2(self.y, self.x)

    @classmethod
    def from_polar(cls, *, radius: float, theta: float) -> "Point":
        return cls(
            x=math.sin(theta) * radius,
            y=math.cos(theta) * radius,
        )

    def to_dict(self) -> dict[str, t.Any]:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Point":
        return cls(**data)



@dataclasses.dataclass
class Edge:
    pixels_count: int
    skip_pixels: int
    from_vertex: VerticeId
    to_vertex: VerticeId

    def to_dict(self) -> dict[str, t.Any]:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Edge":
        return cls(**data)

@dataclasses.dataclass
class Segment:
    from_: Point
    to: Point
    pixels_count: int
    skip_pixels: int

@dataclasses.dataclass
class Mapping:
    vertices: list[Point] = dataclasses.field(default_factory=list)
    edges: list[Edge] = dataclasses.field(default_factory=list)

    @classmethod
    def from_file(cls, f: io.StringIO) -> "Mapping":
        return cls.from_dict(json.load(f))

    @classmethod
    def from_dict(cls, d: dict) -> "Mapping":
        return cls(
            vertices=[Point.from_dict(d) for d in d["vertices"]],
            edges=[Edge.from_dict(e) for e in d["edges"]],
        )

    def to_dict(self) -> dict:
        return {
            "vertices": [v.to_dict() for v in self.vertices],
            "edges": [e.to_dict() for e in self.edges],
        }

    @property
    def segments(self) -> t.Iterator[Segment]:
        for edge in self.edges:
            yield Segment(
                from_=self.vertices[edge.from_vertex],
                to=self.vertices[edge.to_vertex],
                pixels_count=edge.pixels_count,
                skip_pixels=edge.skip_pixels,
            )
