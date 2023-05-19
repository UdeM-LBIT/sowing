from typing import Hashable
from collections import OrderedDict

class Net:
    __slots__ = ["_data", "_children", "_hash"]

    def __init__(
        self,
        data: Hashable = None,
        children: tuple[tuple["Net", Hashable]] = ()
    ):
        self._data = data
        self._children = OrderedDict(children)
        self._hash = hash((data, *children))

    @property
    def data(self):
        return self._data

    @property
    def children(self):
        return self._children

    def __hash__(self) -> int:
        return self._hash

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False

        return self._data == other._data and self._children == other._children

    def attach(self, data: Hashable) -> "Net":
        """Attach data to this node."""
        return Net(
            data=data,
            children=self._children,
        )

    def add(self, child: "Net", data: Hashable = None) -> "Net":
        """Add or replace a link to another node."""
        return Net(
            data=self._data,
            children=self._children | {child: data},
        )

    def remove(self, child: "Net") -> "Net":
        """Remove a link to a node."""
        if child not in self._children:
            raise KeyError(child)

        return self.discard(child)

    def discard(self, child: "Net") -> "Net":
        """Remove a link to a node, if one exists."""
        copy = self._children.copy()
        copy.pop(child, None)
        return Net(data=self._data, children=copy)
