from typing import Callable, Generator, Iterator
from enum import Enum, auto
from inspect import signature
from .node import Node, Zipper


class Order(Enum):
    """Tree traversal orders."""

    # Visit nodes before their children, in depth-first order
    Pre = auto()

    # Visit nodes after their children, in depth-first order
    Post = auto()

    # Visit nodes along an eulerian tour
    Euler = auto()


def _none_else(left, right):
    return left if left is not None else right


Traversal = Generator[Zipper, Zipper, Node]


def _traverse_pre_post(node: Node, preorder: bool, reverse: bool) -> Traversal:
    cursor = node.unzip()

    if reverse: advance = lambda: cursor.prev(preorder=preorder)
    else: advance = lambda: cursor.next(preorder=preorder)

    root_start = (not preorder == reverse)

    if not root_start:
        cursor = advance()

    while True:
        next_cursor = yield cursor
        cursor = _none_else(next_cursor, cursor)

        if not root_start and cursor.is_root():
            return cursor.zip()

        cursor = advance()

        if root_start and cursor.is_root():
            return cursor.zip()


def _traverse_euler(node: Node, reverse: bool) -> Traversal:
    child = -1 if reverse else 0
    sibling = -1 if reverse else 1
    cursor = node.unzip()

    while True:
        next_cursor = yield cursor
        cursor = _none_else(next_cursor, cursor)

        if not cursor.is_leaf():
            cursor = cursor.down(child)
        else:
            while cursor.is_last_sibling(sibling) and not cursor.is_root():
                cursor = cursor.up()
                next_cursor = yield cursor
                cursor = _none_else(next_cursor, cursor)

            if cursor.is_root():
                return cursor.zip()
            else:
                pos = cursor.thread[-1].index
                cursor = cursor.up()
                next_cursor = yield cursor
                cursor = _none_else(next_cursor, cursor)
                cursor = cursor.down(pos + sibling)


def traverse(
    root: Node,
    order: Order = Order.Post,
    reverse: bool = False,
) -> Traversal:
    """
    Make a generator that traverses a tree in a given order.

    :param root: root node to start from
    :param order: traversal order
    :param reverse: pass True to reverse the order
    :returns: generator that yields nodes in the specified order
    """
    match order:
        case Order.Post:
            return _traverse_pre_post(root, preorder=False, reverse=reverse)

        case Order.Pre:
            return _traverse_pre_post(root, preorder=True, reverse=reverse)

        case Order.Euler:
            return _traverse_euler(root, reverse=reverse)

        case _:
            raise ValueError(order)


def maptree(
    func: Callable[[Node], Node] | Callable[[Node, tuple[Zipper.Bead]], Node],
    traversal: Traversal,
) -> Node:
    """
    Transform a tree along a given traversal.

    :param func: transformer callback that visits each node and returns a node
        to replace it. The first argument is the visited node, and the second
        (optional) argument is the thread that leads to that node.
    :param traversal: tree traversal generator
    :returns: transformed tree
    """
    cursor = next(traversal)
    needs_thread = len(signature(func).parameters) == 2

    try:
        while True:
            if needs_thread:
                cursor = cursor.replace(func(cursor.node, cursor.thread))
            else:
                cursor = cursor.replace(func(cursor.node))

            cursor = traversal.send(cursor)
    except StopIteration as end:
        return end.value


def leaves(root: Node) -> Iterator[Node]:
    """Retrieve all leaves below a node."""
    return (zipper.node for zipper in traverse(root) if zipper.is_leaf())
