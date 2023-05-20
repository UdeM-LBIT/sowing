from typing import Callable, Hashable, Optional, Self
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
        """Make a zipper for traversing and manipulating this network."""
        return Zipper(self)

    def map_pre(self, func: Callable[[Self], Self]) -> Self:
        """
        Transform the nodes of this network in preorder.

        :param func: transformation function
        :returns: updated network
        """
        zipper = self.unzip()

        while True:
            zipper = zipper.replace(func(zipper.node))
            zipper = zipper.next_pre()

            if zipper.is_root():
                return zipper.zip()

    def map_post(self, func: Callable[[Self], Self]) -> Self:
        """
        Transform the nodes of this network in postorder.

        :param func: transformation function
        :returns: updated network
        """
        zipper = self.unzip().next_post()

        while True:
            zipper = zipper.replace(func(zipper.node))

            if zipper.is_root():
                return zipper.zip()

            zipper = zipper.next_post()


@dataclass(frozen=True, slots=True)
class Zipper:
    @dataclass(frozen=True, slots=True)
    class Bead:
        origin: Net
        data: Hashable
        index: int

    node: Net
    thread: tuple[Bead] = ()

    def replace(self, node: Net) -> Self:
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

    def is_root(self) -> bool:
        """Test whether the pointed node is a root node."""
        return self.thread == ()

    def up(self) -> Self:
        """Move to the parent of the pointed node."""
        if self.is_root():
            raise IndexError("cannot go up")

        bead = self.thread[-1]
        return Zipper(
            node=bead.origin.add(self.node, bead.data, bead.index),
            thread=self.thread[:-1],
        )

    def has_sibling(self) -> bool:
        """Test whether the pointed node has a next sibling."""
        return (
            not self.is_root()
            and self.thread[-1].index < len(self.thread[-1].origin.children)
        )

    def sibling(self, index: int = 1) -> Self:
        """
        Move to a sibling of the pointed node.

        :param index: sibling offset relative to the current node
            (default: go to the sibling on the right)
        :returns: updated zipper
        """
        return self.up().down(self.thread[-1].index + index)

    def next_pre(self) -> Optional[Self]:
        """Move to the next node in preorder."""
        if not self.is_leaf():
            return self.down()

        while not self.has_sibling():
            self = self.up()

            if self.is_root():
                return self

        return self.sibling()

    def next_post(self) -> Optional[Self]:
        """Move to the next node in postorder."""
        if self.is_root():
            while not self.is_leaf():
                self = self.down()

            return self

        if not self.has_sibling():
            return self.up()

        self = self.sibling()

        while not self.is_leaf():
            self = self.down()

        return self

    def zip(self) -> Net:
        """Zip the network up to its root and return it."""
        bubble = self

        while not bubble.is_root():
            bubble = bubble.up()

        return bubble.node
