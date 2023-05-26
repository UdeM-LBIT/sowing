from dataclasses import dataclass
from typing import Hashable
from immutables import Map
from sowing.util import repr_default


Color = tuple[int, int, int, int]


@repr_default
@dataclass(frozen=True, slots=True)
class Confidence:
    value: float
    stddev: float | None = None


@repr_default
@dataclass(frozen=True, slots=True)
class Taxonomy:
    id: str | None = None
    code: str | None = None
    scientific_name: str | None = None
    common_name: str | None = None
    authority: str | None = None


@repr_default
@dataclass(frozen=True, slots=True)
class Property:
    applies_to: str
    unit: str
    value: Hashable


@repr_default
@dataclass(frozen=True, slots=True)
class Branch:
    length: float | None = None
    props: Map[str, Property] = Map()


@repr_default
@dataclass(frozen=True, slots=True)
class Clade:
    name: str = ""
    confidences: Map[str, Confidence] = Map()
    props: Map[str, Property] = Map()

    width: float | None = None
    color: Color | None = None
    taxonomies: tuple[Taxonomy, ...] = ()

    # TODO
    # sequence: ...
    # events: ...
    # binary_characters: ...
    # distribution: ...
    # date: ...
    # reference: ...
