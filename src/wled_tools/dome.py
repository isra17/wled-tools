import typing as t
import collections
import json
import string
import math

CENTER = (400, 400)
T = t.TypeVar("T")

def vec_add(*args):
    return list(map(sum, zip(*args)))

class RingList(list):
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
                CENTER,
                (
                    math.sin(angle) * distance,
                    math.cos(angle) * distance
                )
            )
            vertices[v] = point

    distance = 380
    for i, v in zip(range(15), vertices_iter):
        angle = (2 * math.pi / 15) * i
        point = vec_add(
            CENTER,
            (
                math.sin(angle) * distance,
                math.cos(angle) * distance
            )
        )
        vertices[v] = point

    for i in rings[0]:
        edges.append(("A", i))

    for i in range(5):
        a = rings[0][i]
        b = rings[0][i+1]
        edges.append((a, b))

    for i in range(5):
        a = rings[0][i]
        b = rings[1][i]
        c = rings[2][i*3+1]
        d = rings[2][i*3-1]
        edges.append((a, b))
        edges.append((b, c))
        edges.append((b, d))

    for i in range(15):
        a = rings[2][i]
        b = rings[2][i+1]
        edges.append((a, b))

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
        ]
    }

if __name__ == '__main__':
    print(json.dumps(generate(), indent=2))

