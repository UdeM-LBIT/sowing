from sowing.node import Node as N
from sowing.lca import LowestCommonAncestor
from sowing import traversal
import pytest


tree = (
    N("0")
    .add(N("1").add(N("2")).add(N("3").add(N("4")).add(N("5"))))
    .add(N("6").add(N("7")).add(N("8")).add(N("9").add(N("10"))))
)
nodes = {cursor.node.data: cursor.node for cursor in traversal.depth(tree)}
lca = LowestCommonAncestor(tree)


def test_lca():
    assert lca(nodes["1"]) == nodes["1"]
    assert lca(nodes["1"], nodes["8"]) == nodes["0"]
    assert lca(nodes["4"], nodes["5"]) == nodes["3"]
    assert lca(nodes["4"], nodes["4"]) == nodes["4"]
    assert lca(nodes["4"], nodes["9"]) == nodes["0"]
    assert lca(nodes["2"], nodes["4"], nodes["5"]) == nodes["1"]
    assert lca(nodes["7"], nodes["8"], nodes["9"]) == nodes["6"]

    with pytest.raises(TypeError) as err:
        lca()

    assert "at least one node is needed" in str(err)


def test_ancestor_relation():
    assert lca.is_ancestor_of(nodes["0"], nodes["0"])
    assert not lca.is_strict_ancestor_of(nodes["0"], nodes["0"])
    assert lca.is_ancestor_of(nodes["0"], nodes["1"])
    assert lca.is_strict_ancestor_of(nodes["0"], nodes["1"])
    assert lca.is_ancestor_of(nodes["0"], nodes["2"])
    assert lca.is_strict_ancestor_of(nodes["0"], nodes["2"])
    assert lca.is_ancestor_of(nodes["0"], nodes["3"])
    assert lca.is_strict_ancestor_of(nodes["0"], nodes["3"])
    assert lca.is_ancestor_of(nodes["0"], nodes["4"])
    assert lca.is_strict_ancestor_of(nodes["0"], nodes["4"])
    assert not lca.is_ancestor_of(nodes["1"], nodes["0"])
    assert not lca.is_ancestor_of(nodes["2"], nodes["0"])
    assert not lca.is_ancestor_of(nodes["3"], nodes["0"])
    assert not lca.is_ancestor_of(nodes["4"], nodes["0"])
    assert lca.is_comparable(nodes["0"], nodes["0"])
    assert lca.is_comparable(nodes["0"], nodes["1"])
    assert lca.is_comparable(nodes["0"], nodes["2"])
    assert lca.is_comparable(nodes["0"], nodes["3"])
    assert lca.is_comparable(nodes["0"], nodes["4"])

    assert lca.is_comparable(nodes["3"], nodes["4"])
    assert lca.is_comparable(nodes["3"], nodes["5"])
    assert lca.is_comparable(nodes["3"], nodes["1"])
    assert lca.is_comparable(nodes["3"], nodes["0"])
    assert lca.is_ancestor_of(nodes["3"], nodes["4"])
    assert lca.is_ancestor_of(nodes["3"], nodes["5"])
    assert not lca.is_ancestor_of(nodes["3"], nodes["1"])
    assert not lca.is_ancestor_of(nodes["3"], nodes["0"])

    assert not lca.is_ancestor_of(nodes["3"], nodes["8"])
    assert not lca.is_ancestor_of(nodes["8"], nodes["3"])
    assert not lca.is_comparable(nodes["8"], nodes["3"])


def test_level_distance():
    assert lca.depth(tree) == 0
    assert lca.depth(nodes["1"]) == 1
    assert lca.depth(nodes["2"]) == 2
    assert lca.depth(nodes["3"]) == 2
    assert lca.depth(nodes["4"]) == 3

    assert lca.distance(tree, tree) == 0
    assert lca.distance(tree, nodes["3"]) == 2
    assert lca.distance(nodes["9"], nodes["10"]) == 1
    assert lca.distance(nodes["4"], nodes["5"]) == 2
    assert lca.distance(nodes["7"], nodes["10"]) == 3
    assert lca.distance(nodes["9"], nodes["4"]) == 5
