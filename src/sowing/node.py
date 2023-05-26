from typing import Hashable, Self
from dataclasses import dataclass, replace, field
from enum import Enum, auto
from .util import repr_default


@repr_default
@dataclass(frozen=True, slots=True)
class Node:
    data: Hashable = None
    children: tuple[Self] = ()
    _hash: int = field(init=False, repr=False, compare=False, default=0)

    def __post_init__(self):
        # Cache hash to avoid needlessly traversing the whole tree
        object.__setattr__(self, "_hash", hash((self.data, self.children)))

    def __hash__(self):
        return self._hash

    def label(self, data: Hashable) -> Self:
        """
        Label this node with arbitrary data.

        :param data: data to attach to this node
        :returns: updated node
        """
        return replace(self, data=data)

    def add(self, child: Self, index: int = -1) -> Self:
        """
        Add a child to this node.

        :param child: node to link to
        :param index: index before which to insert the new child
            (default: insert at the end)
        :returns: updated node
        """
        if index == -1:
            index = len(self.children)

        before = self.children[:index]
        after = self.children[index:]
        return replace(self, children=before + (child,) + after)

    def pop(self, index: int = -1) -> Self:
        """
        Remove a child from this node.

        :param index: index of the child to remove
            (default: remove the last one)
        :returns: updated node
        """
        if index == -1:
            index = len(self.children) - 1

        before = self.children[:index]
        after = self.children[index + 1:]
        return replace(self, children=before + after)

    def replace(self, index: int, child: Self) -> Self:
        """
        Replace one of the children of this node.

        :param index: index of the child to replace
        :param child: new child node
        :returns: updated node
        """
        before = self.children[:index]
        after = self.children[index + 1:]
        return replace(self, children=before + (child,) + after)

    def unzip(self) -> "Zipper":
        """Make a zipper for this subtree pointing on its root."""
        return Zipper(self)


@dataclass(frozen=True, slots=True)
class Zipper:
    @dataclass(frozen=True, slots=True)
    class Bead:
        origin: Node
        index: int

    node: Node
    thread: tuple[Bead] = ()

    def replace(self, node: Node) -> Self:
        """
        Replace the pointed node.

        When travelling back up, the new node will get attached to
        the parent in place of the old pointed node.

        :param node: new node
        :returns: updated zipper
        """
        return replace(self, node=node)

    def is_leaf(self) -> bool:
        """Test whether the pointed node is a leaf node."""
        return self.node.children == ()

    def down(self, index: int = 0) -> Self:
        """
        Move to a child of the pointed node.

        :param index: index of the child to move to;
            negative indices are supported (default: first child)
        :returns: updated zipper
        """
        children = self.node.children

        if index >= len(children):
            raise IndexError("child index out of range")

        index %= len(children)
        child = children[index]

        bead = self.Bead(origin=self.node.pop(index), index=index)
        return Zipper(node=child, thread=self.thread + (bead,))

    def is_root(self) -> bool:
        """Test whether the pointed node is a root node."""
        return self.thread == ()

    def up(self) -> Self:
        """Move to the parent of the pointed node."""
        if self.is_root():
            raise IndexError("cannot go up")

        bead = self.thread[-1]
        return Zipper(
            node=bead.origin.add(self.node, bead.index),
            thread=self.thread[:-1],
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

        bead = self.thread[-1]

        if direction < 0:
            return bead.index == 0

        return bead.index == len(bead.origin.children)

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

        bead = self.thread[-1]
        index = bead.index + offset
        index %= len(bead.origin.children) + 1

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
