from typing import Callable, Generator
from enum import Enum, auto
from .net import Net, Zipper


class Order(Enum):
    """Network traversal orders."""

    # Visit nodes before their children, in depth-first order
    Pre = auto()

    # Visit nodes after their children, in depth-first order
    Post = auto()

    # Visit nodes along an eulerian tour
    Euler = auto()


def _none_else(left, right):
    return left if left is not None else right


Traversal = Generator[Zipper, Zipper, Net]


def _traverse_pre_post(node: Net, preorder: bool, reverse: bool) -> Traversal:
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


def _traverse_euler(node: Net, reverse: bool) -> Traversal:
    child = -1 if reverse else 0
    sibling = -1 if reverse else 1
    cursor = node.unzip()

    while True:
        next_cursor = yield cursor
        cursor = _none_else(next_cursor, cursor)

        if not cursor.is_leaf():
            cursor = cursor.down(child)
        else:
            while not cursor.has_sibling(sibling) and not cursor.is_root():
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
    node: Net,
    order: Order = Order.Post,
    reverse: bool = False,
) -> Traversal:
    """
    Make a generator that traverses a network in a given order.

    :param node: root node to start from
    :param order: traversal order
    :param reverse: pass True to reverse the order
    :returns: generator that yields nodes in the specified order
    """
    match order:
        case Order.Post:
            return _traverse_pre_post(node, preorder=False, reverse=reverse)

        case Order.Pre:
            return _traverse_pre_post(node, preorder=True, reverse=reverse)

        case Order.Euler:
            return _traverse_euler(node, reverse=reverse)

        case _:
            raise ValueError(order)


def transform(
    func: Callable[[Net, tuple[Zipper.Bead]], tuple[Net, tuple[Zipper.Bead]]],
    traversal: Traversal,
) -> Net:
    """
    Transform a network along a given traversal.

    :param func: transformer callback that visits each node and its
        thread and returns the updated pair
    :param traversal: network traversal generator
    :returns: transformed network
    """
    cursor = next(traversal)

    try:
        while True:
            cursor = Zipper(*func(cursor.node, cursor.thread))
            cursor = traversal.send(cursor)
    except StopIteration as end:
        return end.value
