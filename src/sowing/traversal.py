from typing import Callable, Generator, Hashable
from functools import wraps, partial
from inspect import signature
from .node import Node, Zipper


Traversal = Generator[Zipper, Zipper, None]


def _default(value):
    result = yield value
    return result if result is not None else value


def depth(node: Node, preorder: bool = False, reverse: bool = False) -> Traversal:
    """
    Traverse a tree in depth-first order.

    :param node: root node to start from
    :param preorder: pass True to visit parents before children (preorder),
        _defaults to children before parents (postorder)
    :param reverse: pass True to reverse the order
    :returns: generator that yields nodes in the specified order
    """
    cursor = node.unzip()
    advance = partial(
        Zipper.prev if reverse else Zipper.next,
        preorder=preorder,
    )

    root_start = not preorder == reverse

    if not root_start:
        cursor = advance(cursor)

    while True:
        cursor = yield from _default(cursor)

        if not root_start and cursor.is_root():
            return

        cursor = advance(cursor)

        if root_start and cursor.is_root():
            return


def euler(node: Node, reverse: bool = False) -> Traversal:
    """
    Traverse a tree along an eulerian tour.

    :param node: root node to start from
    :param reverse: pass True to reverse the order
    :returns: generator that yields nodes in the specified order
    """
    child = -1 if reverse else 0
    sibling = -1 if reverse else 1
    cursor = node.unzip()

    while True:
        cursor = yield from _default(cursor)

        if not cursor.is_leaf():
            cursor = cursor.down(child)
        else:
            while cursor.is_last_sibling(sibling) and not cursor.is_root():
                cursor = cursor.up()
                cursor = yield from _default(cursor)

            if cursor.is_root():
                return
            else:
                pos = cursor.index
                cursor = cursor.up()
                cursor = yield from _default(cursor)
                cursor = cursor.down(pos + sibling)


def leaves(root: Node, reverse: bool = False) -> Traversal:
    """
    Traverse the leaves of a tree.

    :param node: root node to start from
    :param reverse: pass True to reverse the order
    :returns: generator that yields leaves in the specified order
    """
    advance = Zipper.prev if reverse else Zipper.next
    cursor = advance(root.unzip())

    while True:
        if cursor.is_leaf():
            cursor = yield from _default(cursor)

        if cursor.is_root():
            return

        cursor = advance(cursor)


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
            cursor = func(cursor)
            cursor = traversal.send(cursor)
    except StopIteration:
        return cursor.zip()


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
