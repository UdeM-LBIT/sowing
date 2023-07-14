from collections.abc import Mapping
from typing import Generic, Hashable, Iterator, Iterable, TypeVar, get_args
from sowing import traversal
from sowing.node import Node
from sowing.zipper import Zipper
from .util.rangequery import RangeQuery
from dataclasses import field, Field
import inspect


NodeData = TypeVar("NodeData", bound=Hashable)
EdgeData = TypeVar("EdgeData", bound=Hashable)


TreeElement = Zipper[NodeData, EdgeData] | Node[NodeData, EdgeData] | str
TreeKey = str


def get_key(element: TreeElement) -> TreeKey:
    if isinstance(element, Zipper):
        data = element.node.data
    elif isinstance(element, Node):
        data = element.data
    else:
        data = element

    if isinstance(data, Mapping):
        return data.get("name", "")

    if hasattr(data, "name"):
        return getattr(data, "name")

    if isinstance(data, TreeKey):
        return data

    return ""


class IndexedTree(Generic[NodeData, EdgeData]):
    """Structure for fast querying of tree nodes by key."""

    __slots__ = ["root", "_depths", "_cursor_to_index", "_key_to_cursor"]

    def __init__(self, root: Node[NodeData, EdgeData]):
        """
        Initialize an indexed tree.

        Complexity: O(n log n), with n the number of nodes below :param:`root`.

        :param root: root of the input tree to index on
        :raises: if any two nodes share the same key
        """
        self.root = root

        depths: list[tuple[int, Zipper[NodeData, EdgeData]]] = []
        self._cursor_to_index: dict[Zipper[NodeData, EdgeData], int] = {}
        self._key_to_cursor: dict[str, Zipper[NodeData, EdgeData]] = {}

        for cursor in traversal.depth(root, preorder=True):
            key = get_key(cursor)

            if key in self._key_to_cursor:
                raise RuntimeError(f"duplicate key {key!r} in tree {root!r}")

            self._key_to_cursor[key] = cursor

        for cursor in traversal.euler(root):
            self._cursor_to_index[cursor] = len(depths)
            depths.append((cursor.depth, cursor))

        self._depths = RangeQuery(depths, min)

    def __call__(self, *keys: TreeElement) -> Zipper[NodeData, EdgeData]:
        """
        Locate a node by its key or a collection of keys.

        Complexity: O(n), the number of arguments.

        :param keys: node key or collection of keys
        :raises TypeError: if no arguments are passed
        :returns: if a single key is passed, return the corresponding node;
            otherwise, return the lowest common ancestor of the collection
            of nodes
        """
        if not keys:
            raise TypeError("at least one node is needed")

        start = end = self._cursor_to_index[self[keys[0]]]

        for key in keys[1:]:
            index = self._cursor_to_index[self[key]]
            start = min(start, index)
            end = max(end, index)

        result = self._depths(start, end + 1)
        assert result is not None
        return result[1]

    def __getitem__(self, key: TreeElement) -> Zipper[NodeData, EdgeData]:
        """Locate a tree position by its key."""
        return self._key_to_cursor[get_key(key)]

    def __contains__(self, key: TreeElement) -> bool:
        return get_key(key) in self._key_to_cursor

    def __len__(self) -> int:
        """Get the number of nodes in the tree."""
        return len(self._key_to_cursor)

    def __iter__(self) -> Iterator[NodeData]:
        """Iterate through the keys of all nodes in the tree."""
        return iter(self._key_to_cursor)

    def keys(self) -> Iterable[Node[NodeData, EdgeData]]:
        return self._key_to_node.keys()

    def values(self) -> Iterable[Node[NodeData, EdgeData]]:
        return self._key_to_node.values()

    def is_ancestor_of(self, key1: TreeElement, key2: TreeElement) -> bool:
        """
        Check whether a node is an ancestor of another.

        Complexity: O(1).

        :returns: True if and only if :param:`key2` is on the path from the tree
            root to :param:`key1`
        """
        return self(key1, key2) == self(key1)

    def is_strict_ancestor_of(self, key1: TreeElement, key2: TreeElement) -> bool:
        """
        Check whether a node is a strict an ancestor of another
        (i.e. is an ancestor distinct from the other node).

        Complexity: O(1).

        :returns: True if and only if :param:`key2` is on the path from the tree
            root to :param:`key1` and different from :param:`key1`
        """
        return self(key1, key2) == self(key1) and key1 != key2

    def is_comparable(self, key1: TreeElement, key2: TreeElement) -> bool:
        """
        Check whether two nodes are in the same subtree.

        Complexity: O(1).

        :returns: True if and only if either :param:`key1` is an ancestor or
            descendant of :param:`key2`
        """
        return self.is_ancestor_of(key1, key2) or self.is_ancestor_of(key2, key1)

    def depth(self, key: TreeElement) -> int:
        """
        Find the depth of a node.

        Complexity: O(1).
        """
        index = self._cursor_to_index[self[key]]
        return self._depths(index, index + 1)[0]

    def distance(self, key1: TreeElement, key2: TreeElement) -> int:
        """
        Compute the number of edges on the shortest path between two nodes.

        Complexity: O(1).
        """
        return self.depth(key1) + self.depth(key2) - 2 * self.depth(self(key1, key2))


def index_trees(cls):
    """
    Create index caches for selected tree fields in a dataclass.

    This is a decorator that should be invoked before dataclass(),
    i.e., placed after @dataclass() in the decorator list.

    All fields having the "index_tree" metadata key will be turned into index
    caches for the specified tree fields.
    """
    mapping = {}

    for name, decl in inspect.getmembers(cls):
        if isinstance(decl, Field) and "index_from_tree" in decl.metadata:
            target_field = decl.metadata["index_from_tree"]
            mapping[name] = target_field
            setattr(cls, name, field(init=False, repr=False, compare=False))

            target_type = cls.__annotations__[target_field]
            cls.__annotations__[name] = IndexedTree[*get_args(target_type)]

    if mapping:
        orig_postinit = getattr(cls, "__post_init__", lambda self: None)

        def cls_postinit(self):
            orig_postinit(self)

            for indexed, orig in mapping.items():
                object.__setattr__(self, indexed, IndexedTree(getattr(self, orig)))

        cls.__post_init__ = cls_postinit

    return cls
