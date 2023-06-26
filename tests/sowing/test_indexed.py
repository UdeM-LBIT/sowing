from sowing.node import Node as N
from sowing.indexed import IndexedTree, index_trees
from sowing import traversal
from dataclasses import dataclass, field
from immutables import Map
import pytest


tree_1 = (
    N("0")
    .add(N("1").add(N("2")).add(N("3").add(N("4")).add(N("5"))))
    .add(N("6").add(N("7")).add(N("8")).add(N("9").add(N("10"))))
)


nodes_1 = {cursor.node.data: cursor.node for cursor in traversal.depth(tree_1)}


tree_2 = (
    N(Map({"name": "0"}))
    .add(
        N(Map({"name": "1"}))
        .add(N(Map({"name": "2"})))
        .add(
            N(Map({"name": "3"})).add(N(Map({"name": "4"}))).add(N(Map({"name": "5"})))
        )
    )
    .add(
        N(Map({"name": "6"}))
        .add(N(Map({"name": "7"})))
        .add(N(Map({"name": "8"})))
        .add(N(Map({"name": "9"})).add(N(Map({"name": "10"}))))
    )
)


nodes_2 = {cursor.node.data["name"]: cursor.node for cursor in traversal.depth(tree_2)}


def test_build():
    for tree, nodes in ((tree_1, nodes_1), (tree_2, nodes_2)):
        lookup = IndexedTree(tree)
        assert lookup.root == tree

        for key, node in nodes.items():
            assert lookup(key) == node
            assert lookup[key] == node
            assert key in lookup
            assert node in lookup

        assert "11" not in lookup
        assert N("11") not in lookup

        with pytest.raises(KeyError) as err:
            lookup["11"]

        assert "11" in str(err.value)

        assert len(lookup) == 11
        assert list(lookup) == ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]

        with pytest.raises(RuntimeError) as err:
            IndexedTree(N("0").add(N("0")))

        assert "duplicate key '0' in tree" in str(err.value)

        with pytest.raises(RuntimeError) as err:
            IndexedTree(N(Map({"name": "0"})).add(N(Map({"name": "0"}))))

        assert "duplicate key '0' in tree" in str(err.value)

        empty = IndexedTree(None)
        assert len(empty) == 0
        assert list(empty) == []


def test_lca():
    lookup = IndexedTree(tree_1)

    assert lookup("1") == nodes_1["1"]
    assert lookup("1", "8") == nodes_1["0"]
    assert lookup("4", "5") == nodes_1["3"]
    assert lookup("5", "4") == nodes_1["3"]
    assert lookup("4", "4") == nodes_1["4"]
    assert lookup("4", "9") == nodes_1["0"]
    assert lookup("9", "4") == nodes_1["0"]
    assert lookup("2", "4", "5") == nodes_1["1"]
    assert lookup("7", "8", "9") == nodes_1["6"]

    with pytest.raises(TypeError) as err:
        lookup()

    assert "at least one node is needed" in str(err.value)


def test_ancestor_relation():
    lookup = IndexedTree(tree_1)

    assert lookup.is_ancestor_of("0", "0")
    assert not lookup.is_strict_ancestor_of("0", "0")
    assert lookup.is_ancestor_of("0", "1")
    assert lookup.is_strict_ancestor_of("0", "1")
    assert lookup.is_ancestor_of("0", "2")
    assert lookup.is_strict_ancestor_of("0", "2")
    assert lookup.is_ancestor_of("0", "3")
    assert lookup.is_strict_ancestor_of("0", "3")
    assert lookup.is_ancestor_of("0", "4")
    assert lookup.is_strict_ancestor_of("0", "4")
    assert not lookup.is_ancestor_of("1", "0")
    assert not lookup.is_ancestor_of("2", "0")
    assert not lookup.is_ancestor_of("3", "0")
    assert not lookup.is_ancestor_of("4", "0")
    assert lookup.is_comparable("0", "0")
    assert lookup.is_comparable("0", "1")
    assert lookup.is_comparable("0", "2")
    assert lookup.is_comparable("0", "3")
    assert lookup.is_comparable("0", "4")

    assert lookup.is_comparable("3", "4")
    assert lookup.is_comparable("3", "5")
    assert lookup.is_comparable("3", "1")
    assert lookup.is_comparable("3", "0")
    assert lookup.is_ancestor_of("3", "4")
    assert lookup.is_ancestor_of("3", "5")
    assert not lookup.is_ancestor_of("3", "1")
    assert not lookup.is_ancestor_of("3", "0")

    assert not lookup.is_ancestor_of("3", "8")
    assert not lookup.is_ancestor_of("8", "3")
    assert not lookup.is_comparable("8", "3")


def test_level_distance():
    lookup = IndexedTree(tree_1)

    assert lookup.depth("0") == 0
    assert lookup.depth("1") == 1
    assert lookup.depth("2") == 2
    assert lookup.depth("3") == 2
    assert lookup.depth("4") == 3

    assert lookup.distance("0", "0") == 0
    assert lookup.distance("0", "3") == 2
    assert lookup.distance("9", "10") == 1
    assert lookup.distance("4", "5") == 2
    assert lookup.distance("7", "10") == 3
    assert lookup.distance("9", "4") == 5


def test_index_dataclass():
    @dataclass
    @index_trees
    class TestIndex:
        tree1: N[int, None]
        tree1_index = field(metadata={"index_from_tree": "tree1"})

        tree2: N[str, None]
        index_tree2 = field(metadata={"index_from_tree": "tree2"})

    assert TestIndex.__annotations__["tree1_index"] == IndexedTree[int, None]
    assert TestIndex.__annotations__["index_tree2"] == IndexedTree[str, None]

    value = TestIndex(tree1=N("42"), tree2=tree_1)

    assert isinstance(value.tree1, N)
    assert isinstance(value.tree1_index, IndexedTree)
    assert isinstance(value.tree2, N)
    assert isinstance(value.index_tree2, IndexedTree)

    assert value.tree1_index.root == value.tree1
    assert value.index_tree2.root == value.tree2

    assert value.tree1_index("42") == value.tree1
    assert value.index_tree2("2") == nodes_1["2"]

    @dataclass
    @index_trees
    class TestNoop:
        tree1: N[str, None]

    assert TestNoop(N("test")).tree1 == N("test")
