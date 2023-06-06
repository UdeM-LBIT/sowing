"""Model for phylogenetic information."""
from dataclasses import dataclass, replace
from typing import Hashable, Self
from immutables import Map
from sowing.util.dataclasses import repr_default


@repr_default
@dataclass(frozen=True, slots=True)
class Branch:
    length: float | None = None
    props: Map[str, Hashable] = Map()

    def replace(self, **kwargs) -> Self:
        return replace(self, **kwargs)


@repr_default
@dataclass(frozen=True, slots=True)
class Clade:
    name: str = ""
    props: Map[str, Hashable] = Map()

    def replace(self, **kwargs) -> Self:
        return replace(self, **kwargs)
