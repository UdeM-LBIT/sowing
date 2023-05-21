from typing import Callable, Hashable, Self
from dataclasses import dataclass, replace, field
from enum import Enum, auto


class _Empty(Enum):
    Marker = auto()


class Order(Enum):
    """Network traversal order."""

    # Visit nodes before their children, in depth-first order
    Pre = auto()

    # Visit nodes after their children, in depth-first order
    Post = auto()


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
        child: Self|_Empty = _Empty.Marker,
        data: Hashable|_Empty = _Empty.Marker,
    ) -> Self:
        """
        Replace one of the children of this node.

        :param index: index of the child to replace
        :param child: new child node (default: leave unchanged)
        :param data: new link data (default: leave unchanged)
        :returns: updated node
        """
        if child == _Empty.Marker:
            child = self.children[index][0]

        if data == _Empty.Marker:
            data = self.children[index][1]

        return replace(
            self,
            children=self.children[:index] +
                ((child, data),) + self.children[index + 1:],
        )

    def unzip(self) -> "Zipper":
        """Make a zipper for traversing and manipulating this network."""
        return Zipper(self)

    def traverse(self, order: Order, reverse: bool = False) -> "Iterator":
        """
        Make an interator to traverse the network.

        :param order: traversal order
        :param reverse: pass true to reverse the order
        :returns: iterator
        """
        return Iterator(self, order, reverse)

    def __iter__(self) -> "Iterator":
        """Traverse the network in depth-first postorder."""
        return self.traverse(Order.Post)

    def __reversed__(self) -> "Iterator":
        """Traverse the network in reverse depth-first postorder."""
        return self.traverse(Order.Post, reverse=True)

    def map(
        self,
        func: Callable[[Self], Self],
        order: Order = Order.Post,
        reverse: bool = False,
    ) -> Self:
        """
        Transform the nodes of this network along a given traversal order.

        :param func: transformation function
        :param order: traversal order (default: depth-first postorder)
        :param reverse: pass true to reverse the traversal order
        :returns: updated network
        """
        it = Iterator(self, order, reverse)

        while not it.ended:
            it.zipper = it.zipper.replace(func(it.zipper.node))
            next(it)

        return it.zipper.zip()


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

        :param index: index of the child to move to;
            negative indices are supported (default: first child)
        :returns: updated zipper
        """
        children = self.node.children

        if index >= len(children):
            raise IndexError("child index out of range")

        index %= len(children)
        child, data = children[index]

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

    def has_sibling(self, index: int = 1) -> bool:
        """
        Test whether a sibling exists for the pointed node.

        :param index: sibling offset relative to the current node;
            positive for right, negative for left
            (default: test for the next sibling to the right)
        """
        if self.is_root():
            return False

        if index == 0:
            return True

        bead = self.thread[-1]
        return 0 <= bead.index + index < len(bead.origin.children) + 1

    def sibling(self, index: int = 1) -> Self:
        """
        Move to a sibling of the pointed node.

        :param index: sibling offset relative to the current node;
            positive for right, negative for left
            (default: next sibling to the right)
        :returns: updated zipper
        """
        if not self.has_sibling(index):
            raise IndexError("sibling index out of range")

        return self.up().down(self.thread[-1].index + index)

    def _pre(self, reverse: bool) -> Self:
        child = -1 if reverse else 0
        sibling = -1 if reverse else 1

        if not self.is_leaf():
            return self.down(child)

        while not self.has_sibling(sibling):
            if self.is_root():
                return self

            self = self.up()

        return self.sibling(sibling)

    def _post(self, reverse: bool) -> Self:
        child = -1 if reverse else 0
        sibling = -1 if reverse else 1

        if self.is_root():
            while not self.is_leaf():
                self = self.down(child)

            return self

        if not self.has_sibling(sibling):
            return self.up()

        self = self.sibling(sibling)

        while not self.is_leaf():
            self = self.down(child)

        return self

    def next(self, order: Order = Order.Post) -> Self:
        """
        Move to the next node along a given traversal order.

        :param order: traversal order (default: depth-first postorder)
        :returns: updated zipper
        """
        match order:
            case Order.Pre: return self._pre(reverse=False)
            case Order.Post: return self._post(reverse=False)
            case _: raise NotImplementedError

    def prev(self, order: Order = Order.Post) -> Self:
        """
        Move to the previous node along a given traversal order.

        :param order: traversal order (default: depth-first postorder)
        :returns: updated zipper
        """
        match order:
            case Order.Pre: return self._post(reverse=True)
            case Order.Post: return self._pre(reverse=True)
            case _: raise NotImplementedError()

    def zip(self) -> Net:
        """Zip the network up to its root and return it."""
        bubble = self

        while not bubble.is_root():
            bubble = bubble.up()

        return bubble.node


class Iterator:
    def __init__(self, root: Net, order: Order, reverse: bool):
        self.zipper = root.unzip()

        if reverse:
            self.step = lambda: self.zipper.prev(order)
        else:
            self.step = lambda: self.zipper.next(order)

        if (order == Order.Pre) == reverse:
            self.zipper = self.step()
            self.stop_before_root = False
        else:
            self.stop_before_root = True

        self.ended = False

    def __iter__(self) -> Self:
        return self

    def __next__(self) -> Net:
        node = self.zipper.node

        if self.ended:
            raise StopIteration

        after = self.step()

        if self.stop_before_root and after.is_root():
            self.ended = True

        if not self.stop_before_root and self.zipper.is_root():
            self.ended = True

        self.zipper = after
        return node
