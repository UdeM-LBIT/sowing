from typing import Any, Generic, Hashable, Iterable, Self, TypeVar, overload
from dataclasses import dataclass, replace, field
from collections.abc import Set, Mapping
from .util.dataclasses import repr_default
from .zipper import Zipper


NodeData = TypeVar("NodeData", bound=Hashable)
EdgeData = TypeVar("EdgeData", bound=Hashable)


@repr_default
@dataclass(frozen=True, slots=True)
class Edge(Generic[NodeData, EdgeData]):
    # Node at end of edge
    node: "Node[NodeData, EdgeData]"

    # Arbitrary data attached to this edge
    data: EdgeData = None

    def replace(self, **kwargs) -> Self:
        """
        Create a copy of the current edge in which the attributes given
        as keyword arguments are replaced with the specified value.

        Values which are callables are invoked with the current edge
        to compute the actual value used for replacement.
        """
        for key, value in kwargs.items():
            if callable(value):
                kwargs[key] = value(getattr(self, key))

        return replace(self, **kwargs)


@repr_default
@dataclass(frozen=True, slots=True)
class Node(Generic[NodeData, EdgeData]):
    # Arbitrary data attached to this node
    data: NodeData = None

    # Outgoing edges towards child nodes
    edges: tuple[Edge[NodeData, EdgeData], ...] = ()

    # Cached hash value (to avoid needlessly traversing the whole tree)
    _hash: int = field(init=False, repr=False, compare=False, default=0)

    def __post_init__(self) -> None:
        object.__setattr__(self, "_hash", hash((self.data, self.edges)))

    def __hash__(self) -> int:
        return self._hash

    def __eq__(self, rhs: Any) -> bool:
        if self is rhs:
            return True

        if not isinstance(rhs, self.__class__):
            return NotImplemented

        if self._hash != rhs._hash:
            return False

        seen_lhs = {}
        seen_rhs = {}

        cursor_lhs = self.unzip()
        cursor_rhs = rhs.unzip()

        while True:
            node_lhs = cursor_lhs.node
            id_lhs = id(node_lhs)
            node_rhs = cursor_rhs.node
            id_rhs = id(node_rhs)
            visited = id_lhs in seen_lhs and id_rhs in seen_rhs

            if visited and seen_lhs[id_lhs] == seen_rhs[id_rhs]:
                # Optimization which avoids exponential time comparisons
                # for trees containing a lot of repeated subtrees: skip
                # visiting subtrees that are repeated in both trees,
                # simply make sure they refer to the same subtree
                cursor_lhs = cursor_lhs.next(preorder=True, skip=(node_lhs,))
                cursor_rhs = cursor_rhs.next(preorder=True, skip=(node_rhs,))

            else:
                # Trees with no repeated parts are compared normally:
                # same node data and outgoing edge data
                if node_lhs.data != node_rhs.data:
                    return False

                if len(node_lhs.edges) != len(node_rhs.edges):
                    return False

                if any(
                    edge_lhs.data != edge_rhs.data
                    for edge_lhs, edge_rhs in zip(node_lhs.edges, node_rhs.edges)
                ):
                    return False

                if visited:
                    seen_lhs[id_lhs] = seen_rhs[id_rhs]
                else:
                    seen_lhs[id_lhs] = len(seen_lhs)
                    seen_rhs[id_rhs] = len(seen_rhs)

                cursor_lhs = cursor_lhs.next(preorder=True)
                cursor_rhs = cursor_rhs.next(preorder=True)

            # Trees should have the same size, i.e., the root should be
            # reached again at the same iteration
            if cursor_lhs.is_root() and cursor_rhs.is_root():
                return True

            if cursor_lhs.is_root() or cursor_rhs.is_root():
                return False

    def replace(self, **kwargs) -> Self:
        """
        Create a copy of the current node in which the attributes given
        as keyword arguments are replaced with the specified value.

        Values which are callables are invoked with the current node
        to compute the actual value used for replacement.
        """
        for key, value in kwargs.items():
            if callable(value):
                kwargs[key] = value(getattr(self, key))

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
    def add(self, edge: Edge[NodeData, EdgeData], /, *, index: int = -1) -> Self:
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
        node_edge: Self | Edge[NodeData, EdgeData],
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

            case _:
                raise TypeError(f"cannot add object of type {type(node_edge)}")

        if index == -1:
            index = len(self.edges)

        before = self.edges[:index]
        after = self.edges[index:]
        return self.replace(edges=before + (edge,) + after)

    def extend(
        self,
        items: Iterable[Self | Edge[NodeData, EdgeData]],
    ) -> Self:
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

        if not (0 <= index < len(self.edges)):
            raise IndexError("pop index out of range")

        before = self.edges[:index]
        after = self.edges[index + 1 :]
        return self.replace(edges=before + after)

    def unzip(self) -> Zipper:
        """Make a zipper for this subtree pointing on its root."""
        return Zipper(self)

    def _str(
        self,
        seen: Set[Self],
        prefix: str,
        chars: Mapping[str, str],
        highlight: Self | None,
    ) -> str:
        if self.data is None:
            result = [chars["root"]] if self.edges and not self == highlight else [""]
        elif isinstance(self.data, Mapping):
            result = [str(dict(self.data))]
        else:
            result = [str(self.data)]

        if self is highlight:
            result[0] = chars["highlight"] + result[0]

        if self in seen and self.edges:
            result[0] = result[0] + chars["repeat"]
        else:
            seen.add(self)
            init = chars["init"]
            cont = chars["cont"]

            for index, edge in enumerate(self.edges):
                if isinstance(edge.data, Mapping):
                    branch = str(dict(edge.data))
                elif edge.data is not None:
                    branch = str(edge.data)
                else:
                    branch = ""

                if branch:
                    result.append(prefix + cont + chars["branch"] + branch)

                if index + 1 == len(self.edges):
                    init = chars["init_last"]
                    cont = chars["cont_last"]

                subtree = edge.node._str(
                    prefix=prefix + cont,
                    seen=seen,
                    chars=chars,
                    highlight=highlight,
                )
                result.append(prefix + init + subtree)

        return "\n".join(result)

    def __str__(
        self,
        prefix: str = "",
        chars: Mapping[str, str] = {},
        highlight: Self | None = None,
    ) -> str:
        """Create a human-readable representation of this subtree."""
        return self._str(
            seen=set(),
            prefix=prefix,
            chars=(
                {
                    "root": "┐",
                    "branch": "╭",
                    "init": "├──",
                    "cont": "│  ",
                    "init_last": "└──",
                    "cont_last": "   ",
                    "highlight": "○ ",
                    "repeat": " (…)",
                }
                | chars
            ),
            highlight=highlight,
        )
