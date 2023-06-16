from typing import Generic, Hashable, TypeVar
from sowing import traversal
from sowing.node import Node
from .util.rangequery import RangeQuery


NodeKey = TypeVar("NodeData", bound=Hashable)
EdgeData = TypeVar("EdgeData", bound=Hashable)


class IndexedTree(Generic[NodeKey, EdgeData]):
    """Structure for fast lookup of tree nodes by key."""

    __slots__ = ["root", "_depths", "_index_by_key"]

    def __init__(self, root: Node[NodeKey, EdgeData]):
        """
        Initialize an indexed tree.

        Complexity: O(n log n), with n the number of nodes below :param:`root`.

        :param root: root of the input tree to index on
        :raises: if any two nodes share the same key
        """
        self.root = root
        self._index_by_key: dict[Node[NodeKey, EdgeData] | NodeKey, int] = {}

        keys = set()
        depths: list[tuple[int, Node[NodeKey, EdgeData]]] = []

        for cursor in traversal.depth(root):
            if cursor.node.data in keys:
                raise RuntimeError(
                    f"duplicate key {cursor.node.data!r} in tree {root!r}"
                )

            keys.add(cursor.node.data)

        for cursor in traversal.euler(root):
            self._index_by_key[cursor.node.data] = len(depths)
            self._index_by_key[cursor.node] = len(depths)
            depths.append((cursor.depth, cursor.node))

        self._depths = RangeQuery(depths, min)

    def __call__(self, *keys: Node[NodeKey, EdgeData] | NodeKey) -> Node:
        """
        Locate a node by a key or a collection of keys.

        Complexity: O(n), the number of arguments.

        :param keys: node key or collection of keys
        :raises TypeError: if no arguments are passed
        :returns: if a single key is passed, return the corresponding node;
            otherwise, return the lowest common ancestor of the collection
            of nodes
        """
        if not keys:
            raise TypeError("at least one node is needed")

        start = end = self._index_by_key[keys[0]]

        for key in keys[1:]:
            start = min(start, self._index_by_key[key])
            end = max(end, self._index_by_key[key])

        result = self._depths(start, end + 1)
        assert result is not None
        return result[1]

    def is_ancestor_of(
        self,
        key1: Node[NodeKey, EdgeData] | NodeKey,
        key2: Node[NodeKey, EdgeData] | NodeKey,
    ) -> bool:
        """
        Check whether a node is an ancestor of another.

        Complexity: O(1).

        :returns: True if and only if :param:`key2` is on the path from the tree
            root to :param:`key1`
        """
        return self(key1, key2) == self(key1)

    def is_strict_ancestor_of(
        self,
        key1: Node[NodeKey, EdgeData] | NodeKey,
        key2: Node[NodeKey, EdgeData] | NodeKey,
    ) -> bool:
        """
        Check whether a node is a strict an ancestor of another
        (i.e. is an ancestor distinct from the other node).

        Complexity: O(1).

        :returns: True if and only if :param:`key2` is on the path from the tree
            root to :param:`key1` and different from :param:`key1`
        """
        return self(key1, key2) == self(key1) and key1 != key2

    def is_comparable(
        self,
        key1: Node[NodeKey, EdgeData] | NodeKey,
        key2: Node[NodeKey, EdgeData] | NodeKey,
    ) -> bool:
        """
        Check whether two nodes are in the same subtree.

        Complexity: O(1).

        :returns: True if and only if either :param:`key1` is an ancestor or
            descendant of :param:`key2`
        """
        return self.is_ancestor_of(key1, key2) or self.is_ancestor_of(key2, key1)

    def depth(self, key: Node[NodeKey, EdgeData] | NodeKey) -> int:
        """
        Find the depth of a node.

        Complexity: O(1).
        """
        index = self._index_by_key[key]
        return self._depths(index, index + 1)[0]

    def distance(
        self,
        key1: Node[NodeKey, EdgeData] | NodeKey,
        key2: Node[NodeKey, EdgeData] | NodeKey,
    ) -> int:
        """
        Compute the number of edges on the shortest path between two nodes.

        Complexity: O(1).
        """
        return self.depth(key1) + self.depth(key2) - 2 * self.depth(self(key1, key2))
