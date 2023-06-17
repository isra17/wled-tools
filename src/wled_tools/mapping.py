import io
import typing as t
import json
import dataclasses

VerticeId = t.NewType("VerticeId", str)


@dataclasses.dataclass
class Point:
    x: int
    y: int


@dataclasses.dataclass
class Edge:
    leds_count: int
    from_vertex: VerticeId
    to_vertex: VerticeId


@dataclasses.dataclass
class Mapping:
    vertices: dict[VerticeId, Point]
    edges: list[Edge]

    @classmethod
    def from_file(cls, f: io.StringIO) -> "Mapping":
        return cls.from_dict(json.load(f))

    @classmethod
    def from_dict(cls, d: dict) -> "Mapping":
        return cls(
            vertices={k: Point(**coord) for k, coord in d["vertices"].items()},
            edges=[Edge(**e) for e in d["edges"]],
        )

    @property
    def segments(self) -> t.Iterator[tuple[Point, Point]]:
        for edge in self.edges:
            yield (
                self.vertices[edge.from_vertex],
                self.vertices[edge.to_vertex],
            )
