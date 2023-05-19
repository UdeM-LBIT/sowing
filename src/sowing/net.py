from typing import Hashable

class Net:
    __slots__ = ["_data", "_children", "_hash"]

    def __init__(
        self,
        data: Hashable = None,
        children: tuple[tuple["Net", Hashable]] = ()
    ):
        self._data = data
        self._children = children
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
            children=self._children + ((child, data),),
        )

    def remove(self, target: "Net") -> "Net":
        """Remove all links to a node."""
        return Net(
            data=self._data,
            children=tuple(
                (child, data)
                for child, data in self._children
                if child != target
            ),
        )
