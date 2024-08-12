from itertools import product
from sowing.node import Node
from sowing.util.partition import Partition


def test_partition_int():
def test_empty():
    uf = Partition()
    assert len(uf) == 0


    uf = Partition(range(13))
    assert len(uf) == 13

    for i, j in product(range(13), repeat=2):
        if i != j:
            assert uf.find(i) != uf.find(j)

    assert uf.union(4, 6)
    assert len(uf) == 12
    assert uf.find(4) == uf.find(6)

    assert uf.union(0, 2)
    assert len(uf) == 11
    assert uf.union(2, 4)
    assert len(uf) == 10
    assert uf.union(6, 8)
    assert len(uf) == 9
    assert uf.union(8, 10)
    assert len(uf) == 8
    assert uf.union(10, 12)
    assert len(uf) == 7

    assert uf.union(1, 3)
    assert len(uf) == 6
    assert uf.union(3, 5)
    assert len(uf) == 5
    assert uf.union(5, 7)
    assert len(uf) == 4
    assert uf.union(7, 9)
    assert len(uf) == 3
    assert uf.union(9, 11)
    assert len(uf) == 2

    assert all(uf.find(i) == uf.find(0) for i in range(0, 13, 2))
    assert all(uf.find(i) == uf.find(1) for i in range(1, 13, 2))

    assert not uf.union(1, 5)
    assert not uf.union(1, 1)
    assert uf.union(0, 1)
    assert len(uf) == 1


def test_partition_node():
    uf = Partition(map(Node, "abcdefg"))
    assert len(uf) == 7

    for i in "abcdefg":
        assert uf.find(Node(i)) == Node(i)

    assert uf.union(Node("a"), Node("b"))
    assert uf.union(Node("b"), Node("c"))
    assert uf.union(Node("c"), Node("d"))
    assert uf.union(Node("e"), Node("f"))
    assert uf.union(Node("f"), Node("g"))

    assert len(uf) == 2
    assert uf.find(Node("d")) == Node("a")
    assert uf.find(Node("g")) == Node("e")


def test_union_multiple():
    uf = Partition("abc")
    assert not uf.union("b")
    assert uf.union("b", "c")
    assert uf.union("a", "b", "c")
    assert len(uf) == 1


def test_copy():
    first = Partition(range(3))
    second = first.copy()

    first.union(0, 1)
    assert len(first) == 2
    assert len(second) == 3
    assert first.find(0) == first.find(1)
    assert second.find(0) != second.find(1)


def test_repr():
    uf = Partition(range(4))
    assert repr(uf) == "Partition([[0], [1], [2], [3]])"
    uf.union(0, 3)
    assert repr(uf) == "Partition([[0, 3], [1], [2]])"
    uf.union(1, 0)
    assert repr(uf) == "Partition([[0, 1, 3], [2]])"
    uf.union(2, 0)
    assert repr(uf) == "Partition([[0, 1, 2, 3]])"

    uf = Partition(map(Node, "abcd"))
    uf.union(Node("a"), Node("b"))
    uf.union(Node("c"), Node("d"))
    assert repr(uf) == (
        "Partition([[Node(data='a'), Node(data='b')], "
        "[Node(data='c'), Node(data='d')]])"
    )
