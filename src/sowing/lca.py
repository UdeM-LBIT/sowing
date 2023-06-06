from sowing.traversal import traverse, Order
from sowing.node import Node
from .util.rangequery import RangeQuery


class LowestCommonAncestor:
    """Structure for fast computation of lowest common ancestors."""

    __slots__ = ["tree", "traversal", "rangequery", "traversal_index"]

    def __init__(self, tree: Node):
        """
        Pre-compute the sparse table for lowest common ancestor queries.

        Complexity: O(V × log(V)), with V the number of nodes in `tree`.

        :param tree: input tree to make requests on
        """
        self.tree = tree
        self.traversal = []
        self.traversal_index: dict[Node, int] = {}

        for cursor in traverse(tree, Order.Euler):
            if cursor.node not in self.traversal_index:
                self.traversal_index[cursor.node] = len(self.traversal)

            self.traversal.append((cursor.depth, cursor.node))

        self.rangequery = RangeQuery(self.traversal, min)

    def __call__(self, *nodes: Node) -> Node:
        """
        Find the lowest common ancestor of a collection of nodes.

        Complexity: O(n), the number of nodes in the collection.

        :param nodes: nodes of the collection
        :raises TypeError: if an empty set of nodes is passed
        :returns: the ancestor of all input nodes that is most distant
            from the tree root
        """
        if not nodes:
            raise TypeError("at least one node is needed")

        start = end = self.traversal_index[nodes[0]]

        for node in nodes[1:]:
            start = min(start, self.traversal_index[node])
            end = max(end, self.traversal_index[node])

        result = self.rangequery(start, end + 1)
        assert result is not None
        return result[1]

    def is_ancestor_of(self, first: Node, second: Node) -> bool:
        """
        Check whether a node is an ancestor of another.

        Complexity: O(1).

        :param first: ancestor node
        :param second: descendant node
        :returns: True if and only if `second` is on the path from the tree
            root to `first`
        """
        return self(first, second) == first

    def is_strict_ancestor_of(self, first: Node, second: Node) -> bool:
        """
        Check whether a node is a strict an ancestor of another
        (i.e. is an ancestor distinct from the other node).

        Complexity: O(1).

        :param first: ancestor node
        :param second: descendant node
        :returns: True if and only if `second` is on the path from the tree
            root to `first` and different from `second`
        """
        return self(first, second) == first and first != second

    def is_comparable(self, first: Node, second: Node) -> bool:
        """
        Check whether two nodes are in the same subtree.

        Complexity: O(1).

        :returns: True if and only if either `first` is an ancestor or
            descendant of `second`
        """
        return self.is_ancestor_of(first, second) or self.is_ancestor_of(second, first)

    def depth(self, node: Node) -> int:
        """
        Find the depth of a node.

        Complexity: O(1).
        """
        return self.traversal[self.traversal_index[node]][0]

    def distance(self, first: Node, second: Node) -> int:
        """
        Compute the number of edges on the shortest path between two nodes.

        Complexity: O(1).
        """
        return (
            self.depth(first) + self.depth(second) - 2 * self.depth(self(first, second))
        )
