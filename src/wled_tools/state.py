import typing as t
from .preset import Color, Fx, Palette
import dataclasses

def apply_effect_to_segments(
    segments_state: list[dict],
    *,
    segments: t.Optional[list[int]],
    color: t.Optional[Color],
    effect: t.Optional[Fx],
    palette: t.Optional[Palette],
    speed: t.Optional[int],
    intensity: t.Optional[int],
    brightness: t.Optional[int],
    on: bool,
) -> list[dict]:
    sel_segments = segments_state
    if segments:
        sel_segments = [segments_state[i] for i in segments]

    for segment in sel_segments:
        if color:
            segment["col"][0:1] = [color.to_list()]
        if effect:
            segment["fx"] = effect.value
        if palette:
            segment["pal"] = palette.value
        if speed is not None:
            segment["sx"] = speed
        if intensity is not None:
            segment["ix"] = intensity
        if brightness is not None:
            segment["bri"] = brightness
        segment["on"] = on
    return segments_state
