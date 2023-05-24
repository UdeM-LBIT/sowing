from dataclasses import dataclass
from typing import Hashable, Optional
from immutables import Map


Color = tuple[int, int, int, int]


@dataclass(frozen=True, slots=True)
class Confidence:
    value: float
    stddev: Optional[float] = None


@dataclass(frozen=True, slots=True)
class Taxonomy:
    id: Optional[str] = None
    code: Optional[str] = None
    scientific_name: Optional[str] = None
    common_name: Optional[str] = None
    authority: Optional[str] = None


@dataclass(frozen=True, slots=True)
class Property:
    applies_to: str
    unit: str
    value: Hashable


@dataclass(frozen=True, slots=True)
class Clade:
    name: str = ""
    branch_length: Optional[float] = None
    confidences: Map[str, Confidence] = Map()
    props: Map[str, Property] = Map()

    width: Optional[float] = None
    color: Optional[Color] = None
    taxonomies: tuple[Taxonomy] = ()

    # TODO
    # sequence: ...
    # events: ...
    # binary_characters: ...
    # distribution: ...
    # date: ...
    # reference: ...
