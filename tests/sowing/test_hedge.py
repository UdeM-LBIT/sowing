from sowing.hedge import Hedge
from sowing.node import Node
import pytest


def test_hedge_of():
    empty = Hedge.of()
    assert empty == Hedge()
    assert empty.breadth == 0
    assert len(empty) == empty.breadth

    tree1 = Node("a").add(Node("b")).add(Node("c"))
    single = Hedge.of(tree1)
    assert single.cursor.node == tree1
    assert single.breadth == 1
    assert len(single) == single.breadth

    tree2 = Node("d").add(Node("e")).add(Node("f"))
    double = Hedge.of(tree1, tree2)
    assert double.cursor.node == tree1
    assert double.cursor.sibling().node == tree2
    assert double.breadth == 2
    assert len(double) == double.breadth


def test_hedge_eq():
    tree = (
        Node("x")
        .add(Node("a").add(Node("b")).add(Node("c")))
        .add(Node("d").add(Node("e")).add(Node("f")))
        .add(Node("g").add(Node("h")).add(Node("i")))
        .add(Node("j").add(Node("k")).add(Node("l")))
        .add(Node("m").add(Node("n")).add(Node("o")))
    )

    assert Hedge() == Hedge()
    assert Hedge(tree.unzip().down(1), breadth=0) == Hedge()
    assert Hedge(tree.unzip().down(1), breadth=1) != Hedge()
    assert Hedge(tree.unzip().down(1), breadth=0) == Hedge(
        tree.unzip().down(2), breadth=0
    )
    assert Hedge(tree.unzip().down(1), breadth=1) != Hedge(
        tree.unzip().down(2), breadth=1
    )


def test_hedge_get():
    tree = (
        Node("x")
        .add(Node("a").add(Node("b")).add(Node("c")))
        .add(Node("d").add(Node("e")).add(Node("f")))
        .add(Node("g").add(Node("h")).add(Node("i")))
        .add(Node("j").add(Node("k")).add(Node("l")))
        .add(Node("m").add(Node("n")).add(Node("o")))
    )

    hedge = Hedge(cursor=tree.unzip().down(1), breadth=3)

    assert hedge[0].node == tree.edges[1].node
    assert hedge[1].node == tree.edges[2].node
    assert hedge[2].node == tree.edges[3].node

    with pytest.raises(IndexError):
        hedge[-1]

    with pytest.raises(IndexError):
        hedge[3]


def test_hedge_slice():
    tree = (
        Node("x")
        .add(Node("a").add(Node("b")).add(Node("c")))
        .add(Node("d").add(Node("e")).add(Node("f")))
        .add(Node("g").add(Node("h")).add(Node("i")))
        .add(Node("j").add(Node("k")).add(Node("l")))
        .add(Node("m").add(Node("n")).add(Node("o")))
    )

    hedge = Hedge(cursor=tree.unzip().down(1), breadth=3)

    firsttwo = hedge[:2]
    assert len(firsttwo) == 2
    assert firsttwo[0] == hedge[0]
    assert firsttwo[1] == hedge[1]

    lasttwo = hedge[1:]
    assert len(lasttwo) == 2
    assert lasttwo[0] == hedge[1]
    assert lasttwo[1] == hedge[2]

    center = hedge[1:2]
    assert len(center) == 1
    assert center[0] == hedge[1]

    empty = hedge[0:0]
    assert len(empty) == 0

    with pytest.raises(IndexError):
        hedge[1:0]

    with pytest.raises(IndexError):
        hedge[-1:0]

    with pytest.raises(IndexError):
        hedge[::2]

    with pytest.raises(IndexError):
        hedge[1:4]
