from typing import Callable, Generator, Hashable, Iterator
from enum import Enum, auto
from functools import wraps
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

    if reverse:

        def advance():
            return cursor.prev(preorder=preorder)

    else:

        def advance():
            return cursor.next(preorder=preorder)

    root_start = not preorder == reverse

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
                pos = cursor.index
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


def maptree(func: Callable[[Zipper], Zipper], traversal: Traversal) -> Node | None:
    """
    Transform positions on a tree along a given traversal.

    :param func: callback receiving zipper values along the traversal
        and returning an updated zipper
    :param traversal: tree traversal generator
    :returns: transformed tree
    """
    cursor = next(traversal)

    try:
        while True:
            cursor = traversal.send(func(cursor))
    except StopIteration as end:
        return end.value


def mapnodes(
    func: Callable[[Node], Node] | Callable[[Node, Hashable], tuple[Node, Hashable]],
    traversal: Traversal,
) -> Node:
    """
    Transform the nodes of a tree along a given traversal.

    :param func: callback receiving each node of the tree (and optionally data
        of the incoming edge), and returning an updated node (and edge data), or
        None to remove the node and its subtree
    :param traversal: tree traversal generator
    :returns: transformed tree, or None if the root was removed
    """
    params = signature(func).parameters

    @wraps(func)
    def wrapper(zipper: Zipper):
        node = zipper.node
        data = zipper.data

        if len(params) == 2:
            node, data = func(node, data)
        else:
            node = func(node)

        return zipper.replace(node=node, data=data)

    return maptree(wrapper, traversal)


def leaves(root: Node) -> Iterator[Node]:
    """Retrieve all leaves below a node."""
    return (zipper.node for zipper in traverse(root) if zipper.is_leaf())
