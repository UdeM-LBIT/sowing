from typing import Hashable, Self, Optional
from dataclasses import dataclass, replace
from .util.dataclasses import repr_default


@repr_default
@dataclass(frozen=True, slots=True)
class Zipper:
    # Currently pointed node
    node: Optional["Node"] = None

    # Data attached to the incoming edge
    data: Hashable | None = None

    # Child index into the parent node
    index: int = -1

    # Parent pointer, or None if at root
    parent: Self | None = None

    def replace(self, **kwargs) -> Self:
        return replace(self, **kwargs)

    def is_empty(self) -> bool:
        """Test whether there is a pointed node."""
        return self.node is None

    def is_leaf(self) -> bool:
        """Test whether the pointed node is a leaf node."""
        return not self.is_empty() and self.node.edges == ()

    def down(self, index: int = 0) -> Self:
        """
        Move to a child of the pointed node.

        :param index: index of the child to move to;
            negative indices are supported (default: first child)
        :returns: updated zipper
        """
        if self.is_empty() or index >= len(self.node.edges):
            raise IndexError("child index out of range")

        edges = self.node.edges
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

        if self.is_empty():
            return self.parent

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
            zero for self, positive for right, negative for left, wrapping
            around the child list if needed (default: sibling to the right)
        :returns: updated zipper
        """
        if self.is_root():
            return self

        if self.is_empty():
            if offset == 0:
                raise IndexError("cannot go to self for empty node")
            elif offset > 0:
                offset -= 1

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
        if preorder:
            return self._preorder(flip=False)
        else:
            return self._postorder(flip=False)

    def prev(self, preorder: bool = False) -> Self:
        """
        Move to the previous node in preorder or postorder.

        :param preorder: pass True to move in preorder (default is postorder)
        :returns: updated zipper
        """
        if preorder:
            return self._postorder(flip=True)
        else:
            return self._preorder(flip=True)

    def zip(self) -> "Node":
        """Zip up to the root and return it."""
        bubble = self

        while not bubble.is_root():
            bubble = bubble.up()

        return bubble.node
