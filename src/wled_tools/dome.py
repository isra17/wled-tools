import typing as t
import collections
import json
import string
import math

CENTER = (400, 400)
T = t.TypeVar("T")


def vec_add(*args):
    return list(map(sum, zip(*args)))


class RingList(list[T]):
    def __getitem__(self, index: int) -> T:
        return super().__getitem__(index % len(self))


def generate():
    keys = list(string.ascii_uppercase)
    rings = [
        RingList(keys[1:6]),
        RingList(keys[6:11]),
        RingList(keys[11:26]),
    ]

    vertices = {}
    edges = []

    vertices_iter = iter(keys)

    vertices[next(vertices_iter)] = CENTER
    for distance in (150, 300):
        for i, v in zip(range(5), vertices_iter):
            angle = (2 * math.pi / 5) * i
            point = vec_add(
                CENTER, (math.sin(angle) * distance, math.cos(angle) * distance)
            )
            vertices[v] = point

    distance = 380
    for i, v in zip(range(15), vertices_iter):
        angle = (2 * math.pi / 15) * i
        point = vec_add(
            CENTER, (math.sin(angle) * distance, math.cos(angle) * distance)
        )
        vertices[v] = point

    for i in range(10, 0, -1):
        a = rings[2][i + 1]
        b = rings[2][i]
        edges.append((a, b))

    for i in range(10, 15):
        a = rings[2][i]
        b = rings[2][i + 1]
        edges.append((a, b))

    def make_segment(
        i: int, reversed: bool = False, leg_reversed: bool = False
    ) -> list:
        a = rings[0][i - 1]
        b = rings[0][i]
        c = rings[1][i]

        r = -1 if leg_reversed else 1
        d = rings[2][i * 3 - 1 * r]
        e = rings[2][i * 3 + 1 * r]

        segment = [
            ("A", a),
            (a, b),
            (b, c),
            (c, d),
            (c, e),
        ]
        if reversed:
            return [(b, a) for a, b in segment[::-1]]
        else:
            return segment

    edges.extend(make_segment(0, reversed=True))
    edges.extend(make_segment(4, reversed=True, leg_reversed=True))
    edges.extend(make_segment(1, reversed=False))
    edges.extend(make_segment(3, reversed=True))
    edges.extend(make_segment(2, reversed=False, leg_reversed=True))

    return {
        "vertices": {
            k: {
                "x": x,
                "y": y,
            }
            for k, (x, y) in vertices.items()
        },
        "edges": [
            {
                "leds_count": 60,
                "from_vertex": a,
                "to_vertex": b,
            }
            for (a, b) in edges
        ],
    }


if __name__ == "__main__":
    print(json.dumps(generate(), indent=2))
