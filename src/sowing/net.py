from typing import Hashable, Self
from dataclasses import dataclass, replace, field
from enum import Enum


class Empty(Enum):
    Marker = 0


@dataclass(frozen=True, slots=True)
class Net:
    data: Hashable = None
    children: tuple[tuple[Self, Hashable]] = ()
    _hash: int = field(init=False, repr=False, compare=False, default=0)

    def __post_init__(self):
        # Cache hash to avoid needlessly traversing the whole network
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

    def add(self, child: Self, data: Hashable = None, index: int = -1) -> Self:
        """
        Add a child to this node.

        :param child: node to link to
        :param data: data attached to the link
        :param index: index before which to insert the new child
            (default: insert at the end)
        :returns: updated node
        """
        if index == -1:
            index = len(self.children)

        return replace(
            self,
            children=self.children[:index] +
                ((child, data),) + self.children[index:],
        )

    def pop(self, index: int = -1) -> Self:
        """
        Remove a child from this node.

        :param index: index of the child to remove
            (default: remove the last one)
        :returns: updated node
        """
        if index == -1:
            index = len(self.children) - 1

        return replace(
            self,
            children=self.children[:index] + self.children[index + 1:],
        )

    def replace(
        self,
        index: int,
        child: Self|Empty = Empty.Marker,
        data: Hashable|Empty = Empty.Marker,
    ) -> Self:
        """
        Replace one of the children of this node.

        :param index: index of the child to replace
        :param child: new child node (default: leave unchanged)
        :param data: new link data (default: leave unchanged)
        :returns: updated node
        """
        if child == Empty.Marker:
            child = self.children[index][0]

        if data == Empty.Marker:
            data = self.children[index][1]

        return replace(
            self,
            children=self.children[:index] +
                ((child, data),) + self.children[index + 1:],
        )

    def unzip(self) -> "Zipper":
        return Zipper(self)


@dataclass(frozen=True, slots=True)
class Zipper:
    @dataclass(frozen=True, slots=True)
    class Bead:
        origin: Net
        data: Hashable
        index: int

    node: Net
    thread: tuple[Bead] = ()

    def is_root(self) -> bool:
        """Test whether the pointed node is a root node."""
        return self.thread == ()

    def replace(self, node: Net) -> Self:
        """
        Replace the pointed node.

        When travelling back up, the new node will get attached to
        the parent in place of the old pointed node.

        :param node: new node
        :returns: updated zipper
        """
        return replace(self, node=node)

    def down(self, index: int = 0) -> Self:
        """
        Move to a child of the pointed node.

        :param index: index of the child to move to (default: first child)
        :returns: updated zipper
        """
        if index >= len(self.node.children):
            raise IndexError("child index out of range")

        child, data = self.node.children[index]
        return Zipper(
            node=child,
            thread=self.thread + (self.Bead(
                origin=self.node.pop(index),
                data=data,
                index=index,
            ),),
        )

    def up(self) -> Self:
        """Move to the parent of the pointed node."""
        if not self.thread:
            raise IndexError("cannot go up")

        bead = self.thread[-1]
        return Zipper(
            node=bead.origin.add(self.node, bead.data, bead.index),
            thread=self.thread[:-1],
        )

    def sibling(self, index: int = 1) -> Self:
        """
        Move to a sibling of the pointed node.

        :param index: sibling offset relative to the current node
            (default: go to the sibling on the right)
        :returns: updated zipper
        """
        bead = self.thread[-1]
        return self.up().down(bead.index + index)

    def zip(self) -> Net:
        """Zip the network up to its root and return it."""
        bubble = self

        while not bubble.is_root():
            bubble = bubble.up()

        return bubble.node
