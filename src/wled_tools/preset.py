import itertools
import enum
from .segment import Segment
import dataclasses

@dataclasses.dataclass
class Color:
    r: int
    g: int
    b: int

    def to_list(self):
        return [self.r, self.g, self.b]

class Colors:
    Black = Color(0, 0, 0)
    White = Color(255, 255, 255)
    Red = Color(255, 0, 0)
    Green = Color(0, 255, 0)
    Blue = Color(0, 0, 255)
    Yellow = Color(255, 255, 0)
    Cyan = Color(0, 255, 255)
    Purple = Color(255, 0, 255)
    Orange = Color(255, 128, 0)

class Fx(enum.Enum):
    Static = 0
    Breath = 2
    DisolveRandom = 19
    MultiStrobe = 25
    RainbowRunner = 33
    Chase2 = 37
    FireFlicker = 45
    Firework1D = 42
    Rain = 43
    ScannerDual = 60
    Fire2012 = 66
    ColorTwinkle = 74
    MeteorSmooth = 77
    FireworkExploding = 90
    DancingShadow = 112
    Blend = 115
    CircleSpin = 118
    SpiralSpin = 119

    PixelWave = 130
    Juggles = 131
    MatriPix = 132
    Plasmoid = 134
    Puddles = 135
    MidNoise = 136
    TwoDGEQ = 140
    NoiseFire = 144
    GravCenter = 157
    GravCentric = 158
    AudioComet = 192

class Palette(enum.Enum):
    Solid = 2
    Cloud = 7
    Lava = 8
    Rainbow = 11
    RainbowBand = 12
    Sunset = 13
    RedBlue = 16
    Analogus = 18
    Splash = 19
    Vintage = 23
    Hult = 28
    Fire = 35
    Party = 37
    LightPink = 38
    Tiamat = 45
    Orangery = 47
    ToxyReaf = 58
    FairyReaf = 59
    PinkCandy = 61
    RedReaf = 62


@dataclasses.dataclass
class Effect:
    segments: list[Segment]
    palette: Palette
    fx: Fx
    speed: int
    intensity: int
    colors: list[Color] = dataclasses.field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "pal": self.palette.value,
            "fx": self.fx.value,
            "on": True,
            "frz": False,
            "bri": 255,
            "cct": 127,
            "col": self._color_list(),
            "sx": self.speed,
            "ix": self.intensity,
            "sel": True,
            "mi": False,
        }

    def _color_list(self) -> list[list]:
        return [
            c.to_list()
            for c in (self.colors + [Colors.Black]*3)
        ]




@dataclasses.dataclass
class Preset:
    name: str
    effects: list[Effect]
    main_segment: int = 0


    _segments: list[Segment] = dataclasses.field(init=False)
    _effect_by_segment: dict[Segment, Effect] = dataclasses.field(init=False)

    def __post_init__(self):
        self._segments = list(sorted({s for e in self.effects for s in e.segments}, key=lambda s: s.id))
        self._effect_by_segment = {}
        for effect in self.effects:
            for segment in effect.segments:
                self._effect_by_segment[segment] = effect


    def to_dict(self) -> dict:
        return {
            "n": self.name,
            "mainseg": self.main_segment,
            "seg": [self._to_segment_dict(s) for s in self._segments]
        }

    def _to_segment_dict(self, segment: Segment) -> dict:
        return self._effect_by_segment[segment].to_dict() | segment.to_dict()

@dataclasses.dataclass
class Playlist:
    name: str
    presets: list[Preset]

@dataclasses.dataclass
class Presets:
    playlists: list[Playlist]
    presets: list[Preset]

    def to_dict(self) -> dict:
        max_segments = max(
            len(p._segments)
            for pp in itertools.chain((pl.presets for pl in self.playlists), [self.presets])
            for p in pp
        )
        presets = {"0": {}}
        offset = len(self.playlists) + 1

        for i, preset in enumerate(self.presets):
            n = offset + i
            preset_dict = dataclasses.replace(
                preset,
                name=f"{n:02}.{preset.name}"
            ).to_dict()
            preset_dict["seg"].extend([{"stop": 0}] * (max_segments - len(preset_dict["seg"])))
            presets[str(n)] = preset_dict

        offset += len(self.presets)

        for p, playlist in enumerate(self.playlists):
            for i, preset in enumerate(playlist.presets):
                n = offset + i
                preset_dict = dataclasses.replace(
                    preset,
                    name=f"{n:02}.{preset.name}"
                ).to_dict()
                preset_dict["seg"].extend([{"stop": 0}] * (max_segments - len(preset_dict["seg"])))
                presets[str(n)] = preset_dict

            presets[str(p+1)] = {
                "playlist": {
                    "ps": [str(offset + i) for i in range(len(playlist.presets))],
                    "dur": [1800] * (len(playlist.presets)),
                    "transition": [7] * (len(playlist.presets)),
                    "repeat": "0",
                    "r": True,
                },
                "on": True,
                "n": f"{p+1:02}.{playlist.name}",
                "ql": str(p + 1),
            }

        return presets
