from dataclasses import dataclass
from .. import traversal
from ..node import Node
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

    def extract_parts(cursor):
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


def build(
    leaves: list[Node],
    triples: list[Triple] = [],
    fans: list[Fan] = [],
) -> Node | None:
    """
    Construct a phylogenetic tree satisfying the topology constraints given by
    a set of triples and fans.

    The returned tree is the smallest tree (in number of nodes) compatible with
    all the triples and fans given as input, if such a tree exists.

    This implements the OneTree algorithm from [Ng and Wormald, 1996].

    :param leaves: set of leaves
    :param triples: set of triples
    :param fans: set of fans
    :returns: constructed tree, or None if the constraints are inconsistent
    """
    if not leaves:
        return None

    if len(leaves) == 1:
        return leaves[0]

    if len(leaves) == 2:
        left, right = leaves
        return Node().add(left).add(right)

    partition = Partition(leaves)

    # Merge groups for triples
    for triple in triples:
        partition.union(*triple.ingroup)

    # Ensure fans are all in the same group or all in different groups
    merged = True

    while merged:
        merged = False

        for fan in fans:
            leaves = list(fan.group)
            roots = set(map(lambda leaf: partition.find(leaf), leaves))

            if len(roots) < len(leaves):
                merged = merged or partition.union(*leaves)

    if len(partition) <= 1:
        return None

    # Recursively build subtrees for each group
    root = Node()

    for group in partition.groups():
        subtriples = [triple for triple in triples if triple.is_in(group)]
        subfans = [fan for fan in fans if fan.is_in(group)]
        subtree = build(group, subtriples, subfans)

        if subtree is None:
            return None

        root = root.add(subtree)

    return root


def supertree(*trees: Node) -> Node | None:
    """
    Build a supertree from a set of phylogenetic trees.

    The returned tree is the smallest tree compatible with every tree of
    the input, if such a tree exists.

    :param tree: any number of tree to build a supertree from
    :returns: constructed tree, or None if input trees are incompatible
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

    return build(all_leaves.keys(), all_triples.keys(), all_fans.keys())
