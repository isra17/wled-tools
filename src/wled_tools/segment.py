import dataclasses

@dataclasses.dataclass(frozen=True)
class Segment:
    id: int
    start: int
    stop: int
    reverse: bool = False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "start": self.start,
            "stop": self.stop,
            "grp": 1,
            "spc": 0,
            "of": 0,
            "rev": self.reverse,
        }
