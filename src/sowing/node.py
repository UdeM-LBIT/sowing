from typing import Hashable, Iterable, Self, overload
from dataclasses import dataclass, replace, field
from enum import Enum, auto
from .util import repr_default


@repr_default
@dataclass(frozen=True, slots=True)
class Edge:
    # Node at end of edge
    node: "Node"

    # Arbitrary data attached to this edge
    data: Hashable = None


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


@repr_default
@dataclass(frozen=True, slots=True)
class Zipper:
    # Currently pointed node
    node: Node

    # Data attached to the incoming edge
    data: Hashable | None = None

    # Child index into the parent node
    index: int = -1

    # Parent pointer, or None if at root
    parent: Self | None = None

    def replace(self, **kwargs) -> Self:
        return replace(self, **kwargs)

    def is_leaf(self) -> bool:
        """Test whether the pointed node is a leaf node."""
        return self.node.edges == ()

    def down(self, index: int = 0) -> Self:
        """
        Move to a child of the pointed node.

        :param index: index of the child to move to;
            negative indices are supported (default: first child)
        :returns: updated zipper
        """
        edges = self.node.edges

        if index >= len(edges):
            raise IndexError("child index out of range")

        index %= len(edges)
        return Zipper(
            node=edges[index].node,
            data=edges[index].data,
            parent=self.replace(node=self.node.pop(index)),
            index=index,
        )

    def is_root(self) -> bool:
        """Test whether the pointed node is a root node."""
        return self.parent is None

    def up(self) -> Self:
        """Move to the parent of the pointed node."""
        if self.is_root():
            raise IndexError("cannot go up")

        return self.parent.replace(
            node=self.parent.node.add(self.node, self.data, self.index),
        )

    def is_last_sibling(self, direction: int = 1) -> bool:
        """
        Test whether the pointed node is the last sibling in a direction.

        :param direction: positive number to test in left to right order,
            negative number to test in right to left order
        """
        if self.is_root():
            return True

        if direction == 0:
            return False

        if direction < 0:
            return self.index == 0

        return self.index == len(self.parent.node.edges)

    def sibling(self, offset: int = 1) -> Self:
        """
        Move to a sibling of the pointed node.

        :param offset: sibling offset relative to the current node;
            positive for right, negative for left, wrapping around the
            child list if needed (default: next sibling from left to right)
        :returns: updated zipper
        """
        if self.is_root():
            return self

        index = self.index + offset
        index %= len(self.parent.node.edges) + 1
        return self.up().down(index)

    def _preorder(self, flip: bool) -> Self:
        child = -1 if flip else 0
        sibling = -1 if flip else 1

        if not self.is_leaf():
            return self.down(child)

        while self.is_last_sibling(sibling):
            if self.is_root():
                return self

            self = self.up()

        return self.sibling(sibling)

    def _postorder(self, flip: bool) -> Self:
        child = -1 if flip else 0
        sibling = -1 if flip else 1

        if self.is_root():
            while not self.is_leaf():
                self = self.down(child)

            return self

        if self.is_last_sibling(sibling):
            return self.up()

        self = self.sibling(sibling)

        while not self.is_leaf():
            self = self.down(child)

        return self

    def next(self, preorder: bool = False) -> Self:
        """
        Move to the next node in preorder or postorder.

        :param preorder: pass True to move in preorder (default is postorder)
        :returns: updated zipper
        """
        if preorder: return self._preorder(flip=False)
        else: return self._postorder(flip=False)

    def prev(self, preorder: bool = False) -> Self:
        """
        Move to the previous node in preorder or postorder.

        :param preorder: pass True to move in preorder (default is postorder)
        :returns: updated zipper
        """
        if preorder: return self._postorder(flip=True)
        else: return self._preorder(flip=True)

    def zip(self) -> Node:
        """Zip up to the root and return it."""
        bubble = self

        while not bubble.is_root():
            bubble = bubble.up()

        return bubble.node
