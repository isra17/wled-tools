import typing as t

T = t.TypeVar("T")

def grouper(iterable: t.Iterable[T], n: int) -> t.Iterable[list[T]]:
    return zip(*([iter(iterable)] * n))

