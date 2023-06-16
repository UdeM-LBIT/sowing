from sowing.node import Node as N
from sowing.indexed import IndexedTree
from sowing import traversal
import pytest


tree = (
    N("0")
    .add(N("1").add(N("2")).add(N("3").add(N("4")).add(N("5"))))
    .add(N("6").add(N("7")).add(N("8")).add(N("9").add(N("10"))))
)
nodes = {cursor.node.data: cursor.node for cursor in traversal.depth(tree)}


def test_build():
    lookup = IndexedTree(tree)
    assert lookup.root == tree

    for key, node in nodes.items():
        assert lookup(key) == node

    with pytest.raises(KeyError) as err:
        lookup("11")

    assert "11" in str(err)

    with pytest.raises(RuntimeError) as err:
        IndexedTree(N("0").add(N("0")))

    assert "duplicate key '0' in tree" in str(err)


def test_lca():
    lookup = IndexedTree(tree)

    assert lookup("1") == nodes["1"]
    assert lookup("1", "8") == nodes["0"]
    assert lookup("4", "5") == nodes["3"]
    assert lookup("5", "4") == nodes["3"]
    assert lookup("4", "4") == nodes["4"]
    assert lookup("4", "9") == nodes["0"]
    assert lookup("9", "4") == nodes["0"]
    assert lookup("2", "4", "5") == nodes["1"]
    assert lookup("7", "8", "9") == nodes["6"]

    with pytest.raises(TypeError) as err:
        lookup()

    assert "at least one node is needed" in str(err)


def test_ancestor_relation():
    lookup = IndexedTree(tree)

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
    lookup = IndexedTree(tree)

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
