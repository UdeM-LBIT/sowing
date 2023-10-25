from ..node import Node, Edge
from .. import traversal
from itertools import product, combinations_with_replacement
from collections import Counter
from typing import Iterable


def is_binary(root: Node) -> bool:
    return all(len(cursor.node.edges) in (0, 2) for cursor in traversal.depth(root))


def binarize_at(root: Node, default: Node = Node()) -> Iterable[Node]:
    """
    Generate all possible binarizations of a node.

    This only binarizes the first level below :param:`root`.
    Use :func:`binarize` to recursively binarize a complete tree.

    Unlabeled, labeled and multiply-labeled trees are supported. Outcomes that
    are isomorphic up to children reorderings are only generated once.

    :param root: original node
    :param default: value used for each new node (default: empty node)
    :returns: iterates through all possible binarizations
    """
    if len(root.edges) <= 2:
        yield root
        return

    head = root.replace(edges=())
    edges = Counter(root.edges)

    # Distribute children multiplicities between left and right subtrees
    for right_muls in product(*(range(count + 1) for count in edges.values())):
        left_muls = tuple(value - mul for mul, value in zip(right_muls, edges.values()))

        # Distribute lexicographically left to right
        if sum(right_muls) == 0 or left_muls < right_muls:
            continue

        left_fan = default
        right_fan = default

        for edge, left_mul, right_mul in zip(edges.keys(), left_muls, right_muls):
            left_fan = left_fan.extend((edge,) * left_mul)
            right_fan = right_fan.extend((edge,) * right_mul)

        left_bin = binarize_at(left_fan, default)
        right_bin = binarize_at(right_fan, default)

        if left_muls == right_muls:
            options = combinations_with_replacement(left_bin, r=2)
        else:
            options = product(left_bin, right_bin)

        for left, right in options:
            yield (
                head.add(left if len(left.edges) > 1 else left.edges[0]).add(
                    right if len(right.edges) > 1 else right.edges[0]
                )
            )


def binarize(root: Node, default: Node = Node()) -> Iterable[Node]:
    """
    Generate all possible binarizations of a tree.

    In the output trees, all internal nodes have at most two children.
    Nodes with three children and more are replaced with all possible
    binary sequences of nodes leading to their children.

    Data on nodes and edges is conserved. Additional nodes and edges
    bear no additional data. Outcomes that are isomorphic up to children
    reorderings are only generated once.

    :param root: original tree
    :param default: value used for each new node (default: empty node)
    :returns: iterates through all possible binarizations
    """
    head = root.replace(edges=())
    children = [edge.node for edge in root.edges]
    edge_data = [edge.data for edge in root.edges]

    for bin_children in product(*(binarize(child, default) for child in children)):
        yield from binarize_at(
            root=head.extend(
                (Edge(node, data) for node, data in zip(bin_children, edge_data))
            ),
            default=default,
        )
