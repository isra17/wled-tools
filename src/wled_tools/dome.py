import dataclasses
from itertools import islice
from .preset import Preset, Presets, Palette, Effect, Fx, Colors, Playlist
from .segment import Segment
from .segments_mapping import SegmentsMapping, SegmentGroup
import typing as t
import json
import string
import math
from .mapping import Mapping, Point, Edge

CENTER = Point(400, 400)
T = t.TypeVar("T")

class RingList(list[T]):
    def __getitem__(self, index: int) -> T:
        return super().__getitem__(index % len(self))

@dataclasses.dataclass
class TriSegments:
    around: list[Segment]
    middle: list[Segment]
    top: list[Segment]

    @property
    def all(self) -> list[Segment]:
        return self.around + self.middle + self.top

    @classmethod
    def from_mapping(cls, mapping: SegmentsMapping):
        segments = mapping.wled_group_segments(
            groups=[
                # Around
                SegmentGroup(offset=0, count=5),
                SegmentGroup(offset=5, count=5),
                SegmentGroup(offset=10, count=5, reverse=True),
                # Middle
                SegmentGroup(offset=15, count=3),
                SegmentGroup(offset=20, count=3),
                SegmentGroup(offset=26, count=1, reverse=True),
                SegmentGroup(offset=28, count=2, reverse=True),
                SegmentGroup(offset=30, count=3),
                SegmentGroup(offset=36, count=1, reverse=True),
                SegmentGroup(offset=38, count=2, reverse=True),
                # Top
                SegmentGroup(offset=18, count=2),
                SegmentGroup(offset=23, count=2),
                SegmentGroup(offset=25, count=1, reverse=True),
                SegmentGroup(offset=27, count=1, reverse=True),
                SegmentGroup(offset=33, count=2),
                SegmentGroup(offset=35, count=1, reverse=True),
                SegmentGroup(offset=37, count=1, reverse=True),
            ]
        )

        return cls(
            around=list(islice(segments, 3)),
            middle=list(islice(segments, 7)),
            top=list(islice(segments, 7)),
        )

@dataclasses.dataclass
class PentaSegments:
    around: list[Segment]
    sides: list[Segment]

    @property
    def all(self) -> list[Segment]:
        return self.around + self.sides

    @classmethod
    def from_mapping(cls, mapping: SegmentsMapping):
        segments = mapping.wled_group_segments(
            groups=[
                # Around
                SegmentGroup(offset=0, count=5),
                SegmentGroup(offset=5, count=5),
                SegmentGroup(offset=10, count=5, reverse=True),
                # Sides
                SegmentGroup(offset=15, count=5),
                SegmentGroup(offset=20, count=5),
                SegmentGroup(offset=25, count=5, reverse=True),
                SegmentGroup(offset=30, count=5),
                SegmentGroup(offset=35, count=5, reverse=True),
            ]
        )

        return cls(
            around=list(islice(segments, 3)),
            sides=list(islice(segments, 5)),
        )


EDGES_PIXELS_COUNT = [
    57, 57, 56, 57, 57, # 1
    56, 57, 57, 57, 57, # 2

    56, 55, 56, 56, 56, # 3
    56, 56, 57, 57, 57, # 4

    56, 53, 56, 57, 57, # 5
    56, 56, 57, 57, 57, # 6

    56, 57, 56, 58, 57, # 7
    57, 56, 56, 57, 59, # 8
]

SKIP_PIXELS = [
    0, 0, 0, 0, 0,
    0, 0, 0, 0, 0,

    0, 1, 1, 0, 1,
    0, 0, 0, 0, 0,

    0, 0, 1, 0, 0,
    0, 0, 0, 0, 0,

    0, 0, 0, 0, 0,
    0, 0, 0, 0, 0,

    0, 0, 0, 0, 0,
    0, 0, 0, 0, 0,
]

def generate():
    rings = [
        RingList(list(range(1, 6))),
        RingList(list(range(6, 16))),
        RingList(list(range(16, 31))),
    ]

    vertices = []
    edges = []

    middle_extra = []

    vertices.append(CENTER)
    for i in range(5):
        angle = (2 * math.pi / 5) * i
        vertices.append(CENTER + Point.from_polar(radius=150, theta=angle))

    for i in range(10):
        angle = (2 * math.pi / 10) * i
        vertices.append(CENTER + Point.from_polar(radius=300, theta=angle))

    distance = 380
    for i in range(15):
        angle = (2 * math.pi / 15) * i
        vertices.append(CENTER + Point.from_polar(radius=distance, theta=angle))

    for i in range(9, -1, -1):
        a = rings[2][i + 1]
        b = rings[2][i]
        edges.append((a, b))

    for i in range(10, 15):
        a = rings[2][i]
        b = rings[2][i + 1]
        edges.append((a, b))

    def make_segment(
        i: int, reversed: bool = False, leg_reversed: bool = False, v_left: t.Optional[bool] = None,
    ) -> list:
        a = rings[0][i - 1]
        b = rings[0][i]
        c = rings[1][i*2]

        r = -1 if leg_reversed else 1
        d = rings[2][i * 3 - 1 * r]
        e = rings[2][i * 3 + 1 * r]
        b_fix = rings[1][(i-1)*2 + (1 if v_left else -1)]

        segment = [
            (0, a),
            (a, b),
            (b, c),
            (c, d),
            (c, e),
        ]
        if v_left is not None:
            segment = [
                (0, a),
                (a, b_fix),
                (a, b),
                (b, c),
                (c, e),
            ]


        if reversed:
            return [(b, a) for a, b in segment[::-1]]
        else:
            return segment

    edges.extend(make_segment(0, reversed=True))
    edges.extend(make_segment(4, reversed=True, leg_reversed=True))
    edges.extend(make_segment(1, reversed=False, v_left=True))
    edges.extend(make_segment(3, reversed=True))
    edges.extend(make_segment(2, reversed=False, leg_reversed=True, v_left=True))

    return Mapping(
        vertices=vertices,
        edges=[
            Edge(
                pixels_count=pixels_count,
                skip_pixels=skip,
                from_vertex=a,
                to_vertex=b,
            ) for pixels_count, skip, [a, b] in zip(EDGES_PIXELS_COUNT, SKIP_PIXELS, edges)
        ]
    )

def main():
    mapping = generate()
    segmap = SegmentsMapping.from_mapping(mapping=mapping, center=CENTER)

    with open("settings/dome.json", "w") as f:
        json.dump(mapping.to_dict(), f, indent=2)

    ### Generate the presets.
    full_segments = segmap.wled_segments
    tri_segments = TriSegments.from_mapping(segmap)
    penta_segment = PentaSegments.from_mapping(segmap)
    one_segment = list(segmap.wled_group_segments([SegmentGroup(offset=0, count=40)]))

    shared_presets = [
        Preset(
            name="Light Pink Spiral",
            effects=[
                Effect(
                    segments=full_segments,
                    palette=Palette.LightPink,
                    fx=Fx.SpiralSpin,
                    speed=150,
                    intensity=35,
                )
            ]
        ),
        Preset(
            name="Rainbox Bands Spin",
            effects=[
                Effect(
                    segments=full_segments,
                    palette=Palette.RainbowBand,
                    fx=Fx.CircleSpin,
                    speed=28,
                    intensity=0,
                )
            ]
        ),
        Preset(
            name="Lava Spiral",
            effects=[
                Effect(
                    segments=full_segments,
                    palette=Palette.Lava,
                    fx=Fx.CircleSpin,
                    speed=150,
                    intensity=215,
                )
            ]
        ),
        Preset(
            name="Red Blue Spiral",
            effects=[
                Effect(
                    segments=full_segments,
                    palette=Palette.RedBlue,
                    fx=Fx.SpiralSpin,
                    speed=150,
                    intensity=10,
                )
            ]
        ),
        Preset(
            name="Rainbow Runner",
            effects=[
                Effect(
                    segments=penta_segment.all,
                    palette=Palette.Hult,
                    fx=Fx.RainbowRunner,
                    speed=200,
                    intensity=255,
                )
            ]
        ),
        Preset(
            name="Party Fireworks",
            effects=[
                Effect(
                    segments=penta_segment.all,
                    palette=Palette.Party,
                    fx=Fx.FireworkExploding,
                    speed=64,
                    intensity=64,
                )
            ]
        ),
    ]

    summer69 = Playlist(name="Summer69", presets=[
        Preset(
            name="Pink Audio Comet",
            effects=[Effect(
                segments=penta_segment.all,
                palette=Palette.LightPink,
                fx=Fx.AudioComet,
                speed=220,
                intensity=255,
            )]),
        Preset(
            name="Hult 2DGEQ",
            effects=[Effect(
                segments=penta_segment.all,
                palette=Palette.Hult,
                fx=Fx.TwoDGEQ,
                speed=220,
                intensity=255,
            )]),
        Preset(
            name="Cloud Puddles",
            effects=[Effect(
                segments=penta_segment.all,
                palette=Palette.Cloud,
                fx=Fx.Puddles,
                speed=128,
                intensity=220,
            )]),
        Preset(
            name="Party Plasmoid",
            effects=[Effect(
                segments=penta_segment.all,
                palette=Palette.Party,
                fx=Fx.Plasmoid,
                speed=128,
                intensity=190,
            )]),
        Preset(
            name="Pink Pixel Wave",
            effects=[Effect(
                segments=penta_segment.all,
                palette=Palette.PinkCandy,
                fx=Fx.PixelWave,
                speed=128,
                intensity=255,
            )]),
        Preset(
            name="Pink Noise Fire",
            effects=[Effect(
                segments=penta_segment.all,
                palette=Palette.PinkCandy,
                fx=Fx.NoiseFire,
                speed=70,
                intensity=255,
            )]),
        Preset(
            name="Hult Mid Noise",
            effects=[Effect(
                segments=penta_segment.all,
                palette=Palette.Hult,
                fx=Fx.MidNoise,
                speed=0,
                intensity=255,
            )]),
        Preset(
            name="Red Reaf MatriPix",
            effects=[Effect(
                segments=penta_segment.all,
                palette=Palette.RedReaf,
                fx=Fx.MatriPix,
                speed=200,
                intensity=255,
            )]),
        Preset(
            name="Hult Juggles",
            effects=[Effect(
                segments=penta_segment.all,
                palette=Palette.Hult,
                fx=Fx.Juggles,
                speed=150,
                intensity=255,
            )]),
        Preset(
            name="RedBlue GravCenter",
            effects=[Effect(
                segments=penta_segment.all,
                palette=Palette.RedBlue,
                fx=Fx.GravCenter,
                speed=200,
                intensity=200,
            )]),
        Preset(
            name="Fairy GravCentric",
            effects=[Effect(
                segments=penta_segment.all,
                palette=Palette.FairyReaf,
                fx=Fx.GravCentric,
                speed=200,
                intensity=255,
            )]),
    ] + shared_presets)

    losstidburn = Playlist(name="Losstidburn", presets=shared_presets + [
        Preset(
            name="Full Rainbox Spin",
            effects=[
                Effect(
                    segments=full_segments,
                    palette=Palette.Rainbow,
                    fx=Fx.CircleSpin,
                    speed=28,
                    intensity=0,
                )
            ]
        ),
        Preset(
            name="Tiamat Spiral Spin",
            effects=[
                Effect(
                    segments=full_segments,
                    palette=Palette.Tiamat,
                    fx=Fx.SpiralSpin,
                    speed=108,
                    intensity=0,
                )
            ]
        ),
        Preset(
            name="Vintage Fast Spiral",
            effects=[
                Effect(
                    segments=full_segments,
                    palette=Palette.Vintage,
                    fx=Fx.SpiralSpin,
                    speed=255,
                    intensity=16,
                )
            ]
        ),
        Preset(
            name="Light Pink Spiral",
            effects=[
                Effect(
                    segments=full_segments,
                    palette=Palette.LightPink,
                    fx=Fx.SpiralSpin,
                    speed=150,
                    intensity=35,
                )
            ]
        ),
        Preset(
            name="Cloud Spiral",
            effects=[
                Effect(
                    segments=full_segments,
                    palette=Palette.Cloud,
                    fx=Fx.SpiralSpin,
                    speed=150,
                    intensity=0,
                )
            ]
        ),
        Preset(
            name="Rain",
            effects=[
                Effect(
                    segments=tri_segments.around,
                    palette=Palette.Cloud,
                    fx=Fx.ColorTwinkle,
                    speed=180,
                    intensity=180,
                ),
                Effect(
                    segments=tri_segments.middle,
                    palette=Palette.Cloud,
                    fx=Fx.Rain,
                    speed=230,
                    intensity=255,
                ),
                Effect(
                    segments=tri_segments.top,
                    palette=Palette.Cloud,
                    fx=Fx.ColorTwinkle,
                    speed=180,
                    intensity=180,
                )
            ]
        ),
        Preset(
            name="Strobe",
            effects=[
                Effect(
                    segments=[segment],
                    palette=Palette.Solid,
                    colors=[Colors.Black, Colors.White],
                    fx=Fx.MultiStrobe,
                    speed=150 - i*5,
                    intensity=8,
                )
                for i, segment in enumerate(tri_segments.all)
            ]
        ),
        Preset(
            name="Analog Blend",
            effects=[
                Effect(
                    segments=penta_segment.all,
                    palette=Palette.Analogus,
                    fx=Fx.Blend,
                    speed=255,
                    intensity=64,
                )
            ]
        ),
        Preset(
            name="Splash Breath",
            effects=[
                Effect(
                    segments=penta_segment.all,
                    palette=Palette.Splash,
                    fx=Fx.Breath,
                    speed=70,
                    intensity=255,
                )
            ]
        ),
        Preset(
            name="Pink Dancing Shadow",
            effects=[
                Effect(
                    segments=penta_segment.all,
                    palette=Palette.PinkCandy,
                    fx=Fx.DancingShadow,
                    speed=170,
                    intensity=255,
                )
            ]
        ),
        Preset(
            name="Toxy Chase",
            effects=[
                Effect(
                    segments=penta_segment.around,
                    palette=Palette.ToxyReaf,
                    fx=Fx.Blend,
                    speed=255,
                    intensity=255,
                ),
                Effect(
                    segments=penta_segment.sides,
                    palette=Palette.ToxyReaf,
                    fx=Fx.Chase2,
                    speed=255,
                    intensity=255,
                )
            ]
        ),
        Preset(
            name="Fairy Dual",
            effects=[
                Effect(
                    segments=penta_segment.all,
                    palette=Palette.FairyReaf,
                    fx=Fx.ScannerDual,
                    speed=100,
                    intensity=200,
                )
            ]
        ),
        Preset(
            name="Pink Meteor",
            effects=[
                Effect(
                    segments=penta_segment.all,
                    palette=Palette.PinkCandy,
                    fx=Fx.MeteorSmooth,
                    speed=128,
                    intensity=128,
                )
            ]
        ),
        Preset(
            name="Sunset Disolve",
            effects=[
                Effect(
                    segments=one_segment,
                    palette=Palette.Sunset,
                    fx=Fx.DisolveRandom,
                    speed=128,
                    intensity=32,
                )
            ]
        ),
        Preset(
            name="Fire",
            effects=[
                Effect(
                    segments=penta_segment.sides,
                    palette=Palette.Lava,
                    fx=Fx.Fire2012,
                    speed=80,
                    intensity=150,
                ),
                Effect(
                    segments=penta_segment.around,
                    palette=Palette.Orangery,
                    fx=Fx.FireFlicker,
                    speed=120,
                    intensity=240,
                )
            ]
        ),
    ])

    with open("settings/presets.json", "w") as f:
        json.dump(Presets(
            playlists=[summer69],
            presets=[
                Preset(
                    name="Segment Calibration",
                    effects=[
                        Effect(
                            segments=[penta_segment.all[i]],
                            colors=[color],
                            palette=Palette.Solid,
                            fx=Fx.Static,
                            speed=255,
                            intensity=64,
                        )
                        for i, color in enumerate([Colors.White, Colors.Green, Colors.Blue, Colors.Orange, Colors.Yellow, Colors.Cyan, Colors.Purple, Colors.Orange])
                    ]
                ),
                Preset(
                    name="Strip Calibration",
                    effects=[
                        Effect(
                            segments=full_segments[::2],
                            palette=Palette.Solid,
                            colors=[Colors.Red],
                            fx=Fx.Static,
                            speed=0,
                            intensity=0,
                        ),
                        Effect(
                            segments=full_segments[1::2],
                            palette=Palette.Solid,
                            colors=[Colors.Blue],
                            fx=Fx.Static,
                            speed=0,
                            intensity=0,
                        )
                    ]
                ),
            ]
        ).to_dict(), f)

    ### Generate 2 Configuration: LED and Virtual.
    base_config = segmap.to_config_dict()
    base_config |= {
        "def": {
            "ps": 1,
            "on": True,
            "bri": 128
        },
        "if": {
            "sync": {
                "port0": 21324,
                "port1": 65506,
                "recv": {
                    "bri": False,
                    "col": False,
                    "fx": False,
                    "grp": 0,
                    "seg": False,
                    "sb": False
                },
                "send": {
                    "dir": False,
                    "btn": False,
                    "va": False,
                    "hue": False,
                    "macro": False,
                    "twice": False,
                    "grp": 0
                }
            },
            "nodes": {
                "list": False,
                "bcast": False
            }
        },
        "hw": {
            "digitalmic": {
                "en": 3,
                "pins": {
                    "i2ssd": 12,
                    "i2sws": 2,
                    "i2sck": 15,
                    "i2smclk": 0
                }
            }
        },
        "snd": {
            "cfg": {
                "sq": 10,
                "gn": 40,
                "agc": 1,
            }
        }
    }
    led_config = base_config | {
        "hw": {
            "led": {
                "ins": [
                    {"start": start, "len": length, **pin}
                    for (start, length), pin in zip(
                        mapping.led_config(4),
                        [
                            {'pin': [4], 'type': 22},
                            {'pin': [3], 'type': 22},
                            {'pin': [16], 'type': 22},
                            {'pin': [1], 'type': 22},
                        ]
                    )
                ]
            }
        }
    }

    start, length = list(mapping.led_config(1))[0]
    virtual_config = base_config | {
        "hw": {
            "led": {
                "ins": [
                    {'start': start, 'len': length, 'pin': [192, 168, 1, 205], 'type': 80},
                ]
            }
        }
    }

    with open("settings/cfg.base.json", "w") as f:
        json.dump(base_config, f)

    with open("settings/cfg.led.json", "w") as f:
        json.dump(led_config, f)

    with open("settings/cfg.virtual.json", "w") as f:
        json.dump(virtual_config, f)


if __name__ == "__main__":
    main()
