from typing import cast, Any, Callable, Generator, Hashable, TypeVar, overload, Literal
from functools import partial
from inspect import signature
from .node import Node
from .zipper import Zipper

T = TypeVar("T")
U = TypeVar("U")

NodeData = TypeVar("NodeData", bound=Hashable)
EdgeData = TypeVar("EdgeData", bound=Hashable)
OutNodeData = TypeVar("OutNodeData", bound=Hashable)
OutEdgeData = TypeVar("OutEdgeData", bound=Hashable)


Traversal = Generator[
    Zipper[NodeData, EdgeData], Zipper[OutNodeData, OutEdgeData], None
]


def _default(value: T) -> Generator[T, U | None, U | T]:
    result = yield value
    return result if result is not None else value


UnicityCheck = Literal[False, "id", "eq"]


def depth(
    node: Node[NodeData, EdgeData] | None,
    preorder: bool = False,
    reverse: bool = False,
    unique: UnicityCheck = False,
) -> Traversal[NodeData, EdgeData, OutNodeData, OutEdgeData]:
    """
    Traverse a tree in depth-first order.

    :param node: root node to start from
    :param preorder: pass True to visit parents before children (preorder),
        defaults to children before parents (postorder)
    :param reverse: pass True to reverse the order
    :param unique: how to behave with repeated subtrees, either:
        - False (default): if the tree contains repeated subtrees then those
          subtrees are traversed as many times as they are repeated;
        - "eq": if multiple equivalent subtrees appear in the tree (i.e., with equal
          labels and topology), then only the first occurrence is traversed
        - "id": if the same subtree object is the child of multiple parents (like in a
          DAG), then only the first occurrence is traversed
    :returns: generator that yields nodes in the specified order
    """
    if node is None:
        return

    seen_ids = set()
    seen_nodes = set()
    cursor = node.unzip()

    advance = partial(
        Zipper.prev if reverse else Zipper.next,
        preorder=preorder,
    )
    root_start = not preorder == reverse

    if not root_start:
        cursor = advance(cursor)

    while True:
        node = cursor.node

        if (
            unique is False
            or (unique == "id" and id(node) not in seen_ids)
            or (unique == "eq" and node not in seen_nodes)
        ):
            cursor = yield from _default(cursor)

        if not root_start and cursor.is_root():
            return

        cursor = advance(cursor, skip_ids=seen_ids, skip_nodes=seen_nodes)

        if unique == "id":
            seen_ids.add(id(node))
        elif unique == "eq":
            seen_nodes.add(node)

        if root_start and cursor.is_root():
            return


def euler(
    node: Node[NodeData, EdgeData] | None,
    reverse: bool = False,
) -> Traversal[NodeData, EdgeData, OutNodeData, OutEdgeData]:
    """
    Traverse a tree along an eulerian tour.

    :param node: root node to start from
    :param reverse: pass True to reverse the order
    :returns: generator that yields nodes in the specified order
    """
    if node is None:
        return

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


def leaves(
    node: Node[NodeData, EdgeData] | None,
    reverse: bool = False,
) -> Traversal[NodeData, EdgeData, OutNodeData, OutEdgeData]:
    """
    Traverse the leaves of a tree.

    :param node: root node to start from
    :param reverse: pass True to reverse the order
    :returns: generator that yields leaves in the specified order
    """
    if node is None:
        return

    advance = Zipper.prev if reverse else Zipper.next
    cursor = advance(node.unzip())

    while True:
        if cursor.is_leaf():
            cursor = yield from _default(cursor)

        if cursor.is_root():
            return

        cursor = advance(cursor)


def fold(
    func: Callable[[Zipper[NodeData, EdgeData]], Zipper[OutNodeData, OutEdgeData]],
    traversal: Traversal[NodeData, EdgeData, OutNodeData, OutEdgeData],
) -> Node[OutNodeData, OutEdgeData] | None:
    """
    Transform a tree along a given traversal.

    For each node along the traversal, the folding callback is invoked with
    a cursor pointing on this node. The callback can transform this cursor in
    any way (including changing the tree structure) and returns the updated
    cursor, which is used as a starting point to continue the traversal.

    :param func: callback receiving zipper values along the traversal
        and returning an updated zipper
    :param traversal: tree traversal generator
    :returns: transformed tree
    """
    try:
        in_cursor = next(traversal)
    except StopIteration:
        return None

    cursor = cast(Zipper[Any, Any], in_cursor)

    try:
        while True:
            cursor = func(cursor)
            cursor = traversal.send(cursor)
    except StopIteration:
        out_cursor = cast(Zipper[OutNodeData, OutEdgeData], cursor)
        return out_cursor.zip()


@overload
def map(
    func: Callable[[NodeData], OutNodeData],
    traversal: Traversal,
) -> Node[OutNodeData, OutEdgeData] | None: ...


@overload
def map(
    func: Callable[[NodeData, EdgeData], tuple[OutNodeData, OutEdgeData]],
    traversal: Traversal,
) -> Node[OutNodeData, OutEdgeData] | None: ...


@overload
def map(
    func: Callable[[NodeData, EdgeData, int], tuple[OutNodeData, OutEdgeData]],
    traversal: Traversal,
) -> Node[OutNodeData, OutEdgeData] | None: ...


def map(
    func: Callable[[NodeData, EdgeData, int, int], tuple[OutNodeData, OutEdgeData]],
    traversal: Traversal,
) -> Node[OutNodeData, OutEdgeData] | None:
    """
    Map values attached to nodes and edges along a given tree traversal.

    For each node along the traversal, the mapping callback is invoked with

    (1) the data object attached to the node,
    (2) the data object attached to its parent edge,
    (3) the node’s sibling index relative to its parent, and
    (4) its depth in the tree.

    The mapping callback returns a tuple of two values, the updated data object
    for the node and for the parent edge.

    :param func: mapping callback
    :param traversal: tree traversal
    :returns: transformed tree
    """
    sig = signature(func)

    match len(sig.parameters):
        case 1:

            def wrapper(
                zipper: Zipper[NodeData, EdgeData],
            ) -> Zipper[OutNodeData, OutEdgeData]:
                node = func(zipper.node.data)
                return zipper.replace(node=zipper.node.replace(data=node))

        case 2:

            def wrapper(
                zipper: Zipper[NodeData, EdgeData],
            ) -> Zipper[OutNodeData, OutEdgeData]:
                node, edge = func(zipper.node.data, zipper.data)
                return zipper.replace(node=zipper.node.replace(data=node), data=edge)

        case 3:

            def wrapper(
                zipper: Zipper[NodeData, EdgeData],
            ) -> Zipper[OutNodeData, OutEdgeData]:
                node, edge = func(zipper.node.data, zipper.data, zipper.index)
                return zipper.replace(node=zipper.node.replace(data=node), data=edge)

        case 4:

            def wrapper(
                zipper: Zipper[NodeData, EdgeData],
            ) -> Zipper[OutNodeData, OutEdgeData]:
                node, edge = func(
                    zipper.node.data, zipper.data, zipper.index, zipper.depth
                )
                return zipper.replace(node=zipper.node.replace(data=node), data=edge)

        case _:
            raise TypeError("map: 'func' must accept between 1 and 4 arguments")

    return fold(wrapper, traversal)
