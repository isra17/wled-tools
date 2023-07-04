import typing as t

def grouper(iterable: t.Iterable[T], n: int) -> t.Iterable[list[T]]:
    return zip(*([iter(iterable)] * n))

