from typing import Hashable, Iterable, Self, overload
from dataclasses import dataclass, replace, field
from enum import Enum, auto
from .util.dataclasses import repr_default
from .zipper import Zipper


@repr_default
@dataclass(frozen=True, slots=True)
class Edge:
    # Node at end of edge
    node: "Node"

    # Arbitrary data attached to this edge
    data: Hashable = None

    def replace(self, **kwargs) -> Self:
        return replace(self, **kwargs)


@repr_default
@dataclass(frozen=True, slots=True)
class Node:
    # Arbitrary data attached to this node
    data: Hashable = None

    # Outgoing edges towards child nodes
    edges: tuple[Edge, ...] = ()

    # Cached hash value (to avoid needlessly traversing the whole tree)
    _hash: int = field(init=False, repr=False, compare=False, default=0)

    def __post_init__(self) -> None:
        object.__setattr__(self, "_hash", hash((self.data, self.edges)))

    def __hash__(self) -> int:
        return self._hash

    def replace(self, **kwargs) -> Self:
        return replace(self, **kwargs)

    @overload
    def add(self, node: Self, data: Hashable = None, index: int = -1) -> Self:
        """
        Add a new child to this node.

        :param node: new child node
        :param data: optional data to be attached to the linking edge
        :param index: index before which to insert the new child
            (default: insert at the end)
        :returns: updated node
        """
        ...

    @overload
    def add(self, edge: Edge, index: int = -1) -> Self:
        """
        Add an outgoing edge to this node.

        :param edge: new edge to be added
        :param index: index before which to insert the new edge
            (default: insert at the end)
        :returns: updated node
        """
        ...

    def add(
        self,
        node: Self | Edge,
        data: Hashable = None,
        index: int = -1,
    ) -> Self:
        if isinstance(node, self.__class__):
            edge = Edge(node=node, data=data)
        else:
            edge = node

        if index == -1:
            index = len(self.edges)

        before = self.edges[:index]
        after = self.edges[index:]
        return self.replace(edges=before + (edge,) + after)

    @overload
    def extend(self, nodes: Iterable[Self]) -> Self:
        """
        Append child nodes from an iterable.

        :param nodes: iterable of nodes
        :returns: updated node
        """
        ...

    @overload
    def extend(self, edges: Iterable[Edge]) -> Self:
        """
        Append edges from an iterable.

        :param edges: iterable of edges
        :returns: updated node
        """
        ...

    def extend(self, nodes: Iterable[Self] | Iterable[Edge]) -> Self:
        for node in nodes:
            self = self.add(node)

        return self

    def pop(self, index: int = -1) -> Self:
        """
        Remove an outgoing edge from this node.

        :param index: index of the edge to remove
            (default: remove the last one)
        :returns: updated node
        """
        if index == -1:
            index = len(self.edges) - 1

        before = self.edges[:index]
        after = self.edges[index + 1:]
        return self.replace(edges=before + after)

    def unzip(self) -> "Zipper":
        """Make a zipper for this subtree pointing on its root."""
        return Zipper(self)
