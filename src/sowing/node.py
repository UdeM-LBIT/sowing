from typing import Generic, Hashable, Iterable, Self, TypeVar, overload
from dataclasses import dataclass, replace, field
from .util.dataclasses import repr_default
from .zipper import Zipper


NodeData = TypeVar("NodeData", bound=Hashable)
EdgeData = TypeVar("EdgeData", bound=Hashable)


@repr_default
@dataclass(frozen=True, slots=True)
class Edge(Generic[EdgeData]):
    # Node at end of edge
    node: "Node"

    # Arbitrary data attached to this edge
    data: EdgeData | None = None

    def replace(self, **kwargs) -> Self:
        return replace(self, **kwargs)


@repr_default
@dataclass(frozen=True, slots=True)
class Node(Generic[NodeData, EdgeData]):
    # Arbitrary data attached to this node
    data: NodeData | None = None

    # Outgoing edges towards child nodes
    edges: tuple[Edge[EdgeData], ...] = ()

    # Cached hash value (to avoid needlessly traversing the whole tree)
    _hash: int = field(init=False, repr=False, compare=False, default=0)

    def __post_init__(self) -> None:
        object.__setattr__(self, "_hash", hash((self.data, self.edges)))

    def __hash__(self) -> int:
        return self._hash

    def replace(self, **kwargs) -> Self:
        return replace(self, **kwargs)

    @overload
    def add(
        self,
        node: Self,
        /,
        *,
        data: EdgeData | None = None,
        index: int = -1,
    ) -> Self:
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
    def add(self, edge: Edge[EdgeData], /, *, index: int = -1) -> Self:
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
        node_edge: Self | Edge[EdgeData],
        /,
        *,
        data: EdgeData | None = None,
        index: int = -1,
    ) -> Self:
        match node_edge:
            case self.__class__():
                edge = Edge(node=node_edge, data=data)

            case Edge():
                edge = node_edge

        if index == -1:
            index = len(self.edges)

        before = self.edges[:index]
        after = self.edges[index:]
        return self.replace(edges=before + (edge,) + after)

    def extend(self, items: Iterable[Self] | Iterable[Edge[EdgeData]]) -> Self:
        """
        Attach new nodes or edges from an iterable.

        :param items: iterable of nodes or iterable of edges
        :returns: updated node
        """
        for item in items:
            self = self.add(item)

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
        after = self.edges[index + 1 :]
        return self.replace(edges=before + after)

    def unzip(self) -> Zipper:
        """Make a zipper for this subtree pointing on its root."""
        return Zipper(self)
