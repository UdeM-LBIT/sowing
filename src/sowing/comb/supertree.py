from dataclasses import dataclass
from typing import Set, Generator
from itertools import product
from .. import traversal
from ..node import Node
from ..zipper import Zipper
from ..util.partition import Partition


@dataclass(frozen=True, slots=True)
class Triple:
    ingroup: tuple[Node, Node]
    outgroup: Node

    def is_in(self, nodes) -> bool:
        return (set(self.ingroup) | set((self.outgroup,))) <= set(nodes)


@dataclass(frozen=True, slots=True)
class Fan:
    group: tuple[Node, ...]

    def is_in(self, nodes) -> bool:
        return set(self.group) <= set(nodes)


def breakup(root: Node) -> tuple[list[Node], list[Triple], list[Fan]]:
    """
    Break up a phylogenetic tree into triples and fans that encode its topology.

    This implements the BreakUp algorithm from [Ng and Wormald, 1996].

    The output representation uniquely determines the input tree, disregarding
    unary nodes, repeated leaves, child order, data in internal nodes, and
    data on edges.

    The input tree can be reconstructed using the :func:`build` function.

    :param root: input tree to be broken up
    :returns: a tuple containing the list of leaves in the tree, a list of
        extracted triples, and a list of extracted fans
    """
    triples = []
    fans = []

    def extract_parts(cursor: Zipper) -> Zipper:
        children = tuple(edge.node for edge in cursor.node.edges)

        if cursor.is_leaf() or not all(
            cursor.down(i).is_leaf() for i in range(len(children))
        ):
            return cursor

        if len(children) >= 3:
            # Break up fan
            fans.append(Fan(children))
            children = children[:2]

        # Break up triple
        base = cursor

        while base.sibling() == base and not base.is_root():
            base = base.up()

        if base.is_root():
            return cursor

        outgroup = next(traversal.leaves(base.sibling().node)).node
        triples.append(Triple(children, outgroup))
        return base.replace(node=children[0])

    traversal.fold(extract_parts, traversal.depth(root))
    leaves = [cursor.node for cursor in traversal.leaves(root)]
    return leaves, triples, fans


def _build_merge_fans(partition, fans):
    """Ensure fans are either all in the same group or all in different groups."""
    merged = True

    while merged:
        merged = False

        for fan in fans:
            leaves = list(fan.group)
            roots = {partition.find(leaf) for leaf in leaves}

            if len(roots) < len(leaves):
                merged = merged or partition.union(*leaves)


def build(
    leaves: list[Node],
    triples: list[Triple] = [],
    fans: list[Fan] = [],
    arity: int = 0,
) -> Generator[Node, None, None]:
    """
    Enumerate phylogenetic trees satisfying the topology constraints given by
    a set of triples and fans.

    The first returned tree is the smallest tree (in number of nodes) compatible
    with all the triples and fans given as input, if such a tree exists.

    This implements the AllTrees algorithm from [Ng and Wormald, 1996].

    :param leaves: set of leaves
    :param triples: set of triples
    :param fans: set of fans
    :param arity: arity of the generated trees, or 0 to generate trees of arbitrary arity
    :yields: possible trees, if any
    """
    if not leaves:
        return

    if len(leaves) == 1:
        yield leaves[0]
        return

    if len(leaves) == 2:
        left, right = leaves
        yield Node().add(left).add(right)
        return

    partition = Partition(leaves)

    # Merge groups for triples
    for triple in triples:
        partition.union(*triple.ingroup)

    _build_merge_fans(partition, fans)

    # Try all possible mergings of the partition that fit the requested arity
    for subpartition in partition.merge(size=arity):
        _build_merge_fans(subpartition, fans)

        if len(subpartition) <= 1:
            return

        # Recursively build subtrees for each group
        for descendants in product(
            *(
                build(
                    group,
                    [triple for triple in triples if triple.is_in(group)],
                    [fan for fan in fans if fan.is_in(group)],
                    arity=arity,
                )
                for group in subpartition.values()
            )
        ):
            yield Node().extend(descendants)


def supertree(*trees: Node, arity: int = 0) -> Generator[Node, None, None]:
    """
    Build a supertree from a set of phylogenetic trees.

    The first returned tree is the smallest tree compatible with every tree of
    the input, if such a tree exists.

    :param tree: any number of tree to build a supertree from
    :param arity: arity of the generated supertrees, or 0 to generate
        supertrees of arbitrary arity
    :yields: possible supertrees, if any
    """
    # Use dictionaries as sets to merge parts while preserving ordering
    all_leaves = {}
    all_triples = {}
    all_fans = {}

    for tree in trees:
        leaves, triples, fans = breakup(tree)
        all_leaves.update(dict.fromkeys(leaves))
        all_triples.update(dict.fromkeys(triples))
        all_fans.update(dict.fromkeys(fans))

    yield from build(
        all_leaves.keys(), all_triples.keys(), all_fans.keys(), arity=arity
    )


def display(root: Node, leaves: Set[Node]) -> Node | None:
    """
    Extract the smallest minor containing the given leaves of a tree.

    :param root: input tree to be filtered
    :param leaves: set of leaves to keep
    :returns: filtered tree
    """

    def filter_tree(cursor: Zipper) -> Zipper:
        node = cursor.node

        if cursor.is_leaf() and node not in leaves:
            return cursor.replace(node=None)

        if len(node.edges) == 1:
            return cursor.replace(node=node.edges[0].node)

        return cursor

    return traversal.fold(filter_tree, traversal.depth(root))
