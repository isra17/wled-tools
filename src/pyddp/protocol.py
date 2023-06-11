import struct
import enum
import typing as t
import io
import dataclasses


class DDPError(Exception):
    pass


@dataclasses.dataclass
class Flags:
    # 2-bits for protocol version number, this module implement version 1 (01).
    version: int

    # reserved
    reserved: bool

    # timecode field added to end of header
    # if Timecode & Push are set, Push at specified time
    timecode: bool

    # If set, data comes from Storage, not data-field
    storage: bool

    # Marks reply to Query packet.
    # always set when any packet is sent by a Display.
    # if Reply, Query flag is ignored.
    reply: bool

    # Requests len data from ID at offset (no data sent)
    # if clear, is a Write buffer packet
    query: bool

    # For display synchronization, or marks last packet of Reply
    push: bool


class ColorType(enum.IntEnum):
    UNDEFINED = 0
    RGB = 1
    HSL = 2
    RGBW = 3
    GRAYSCALE = 4
    UNK1 = 5
    UNK2 = 6
    UNK3 = 7


_size_map: t.Final[dict[int, int]] = {
    0: 0,
    1: 1,
    2: 4,
    3: 8,
    4: 16,
    5: 24,
    6: 32,
    7: 0,
}


@dataclasses.dataclass
class DataType:
    # C is 0 for standard types or 1 for Customer defined
    custom: bool

    # R is reserved and should be 0.
    reserved: bool

    # TTT is data type
    # 000 = undefined
    # 001 = RGB
    # 010 = HSL
    # 011 = RGBW
    # 100 = grayscale
    color_type: ColorType

    # SSS is size in bits per pixel element (like just R or G or B data)
    # 0=undefined, 1=1, 2=4, 3=8, 4=16, 5=24, 6=32
    bits: int


class TargetId(enum.IntEnum):
    RESERVED = 0
    DEFAULT = 1
    JSON_CONTROL = 246
    JSON_CONFIG = 250
    JSON_STATUS = 251
    DMX_TRANSIT = 254
    ALL = 255


@dataclasses.dataclass(frozen=True)
class Packet:
    flags: Flags

    # Sequence number from 1-15, or zero if not used
    # The sequence number should be incremented with each new packet sent.
    # A sender can send duplicate packets with the same sequence number and DDP header for redundancy.
    # A receiver can ignore duplicates received back-to-back.
    # The sequence number is ignored if zero.
    sequence: int

    data_type: t.Optional[DataType]

    target_id: t.Union[int, TargetId]

    data_offset: int
    data_size: int
    timecode: t.Optional[int]
    data: bytes


class DDP:
    def __init__(self) -> None:
        pass

    def parse_packet(self, packet: bytes) -> Packet:
        if len(packet) < 10:
            raise DDPError("Expected header")

        flags = self.parse_flags(packet[0])
        sequence = packet[1] & 0xF
        data_type = self.parse_data_type(packet[2])
        try:
            target_id = TargetId(packet[3])
        except ValueError:
            target_id = packet[3]

        offset, size = struct.unpack(">IH", packet[4:10])

        timecode: t.Optional[int] = None
        if flags.timecode:
            if len(packet) < 14:
                raise DDPError("Expected timecode")

            (timecode,) = struct.unpack(">I", packet[10:14])

        return Packet(
            flags=flags,
            sequence=sequence,
            data_type=data_type,
            target_id=target_id,
            data_offset=offset,
            data_size=size,
            timecode=timecode,
            data=packet[14:] if flags.timecode else packet[10:],
        )

    def parse_flags(self, byte: int) -> Flags:
        return Flags(
            version=(byte >> 6) & 0b11,
            reserved=bool((byte >> 5) & 1),
            timecode=bool((byte >> 4) & 1),
            storage=bool((byte >> 3) & 1),
            reply=bool((byte >> 2) & 1),
            query=bool((byte >> 1) & 1),
            push=bool(byte & 1),
        )

    def parse_data_type(self, byte: int) -> t.Optional[DataType]:
        if not byte:
            return None
        return DataType(
            custom=bool((byte >> 7) & 1),
            reserved=bool((byte >> 6) & 1),
            color_type=ColorType((byte >> 3) & 0b111),
            bits=_size_map[byte & 0b111],
        )
