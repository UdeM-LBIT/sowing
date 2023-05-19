import pytest
from sowing.net import Net


def test_build():
    left = Net("b").add(Net("d").add(Net("e")))
    right = Net("c")
    root = Net("a").add(left).add(right)

    assert root.data == "a"
    assert len(root.children) == 2
    assert (left, None) in root.children
    assert (right, None) in root.children


def test_edges():
    end = Net("e")
    mid = Net("d").add(end, "last edge")
    left = Net("b").add(mid)
    right = Net("c")
    root = Net("a").add(left, "edge 1").add(right, "edge 2")

    assert (left, "edge 1") in root.children
    assert (right, "edge 2") in root.children
    assert (mid, None) in left.children
    assert (end, "last edge") in mid.children


def test_repeat():
    root = Net().add(Net()).add(Net())

    assert len(root.children) == 2
    assert root.children[0] == (Net(), None)
    assert root.children[1] == (Net(), None)


def test_eq():
    root1 = Net("a") \
        .add(Net("b").add(Net("d").add(Net("e")))) \
        .add(Net("c"))

    root2 = Net("a") \
        .add(Net("b").add(Net("d").add(Net("e")))) \
        .add(Net("c"))

    root3 = Net("a") \
        .add(Net("c")) \
        .add(Net("b").add(Net("d").add(Net("e"))))

    assert root1 == root2
    assert root1 != root3
    assert root2 != root3

    subtree1 = Net().add(Net()).add(Net())
    subtree2 = Net().add(Net())
    repeat1 = Net().add(subtree1).add(subtree1)
    repeat2 = Net().add(subtree1).add(subtree1)

    assert subtree1 != subtree2
    assert repeat1 == repeat2


def test_modify():
    root = Net("a")
    left = Net("b")

    root.attach("w")
    assert root.data == "a"

    root = root.attach("w")
    assert root.data == "w"
    root = root.attach("a")

    root.add(left)
    assert root == Net("a")

    root = root.add(left)
    assert root == Net("a").add(Net("b"))

    root = root.add(left, "data")
    assert root == Net("a").add(Net("b")).add(Net("b"), "data")

    root.remove(left)
    assert root == Net("a").add(Net("b")).add(Net("b"), "data")

    root = root.remove(left)
    assert root == Net("a")


def test_hashable():
    seen = set()
    seen.add(Net("a").add(Net("b")).add(Net("c")))

    assert Net("a").add(Net("b")).add(Net("c")) in seen
    assert Net("a") not in seen

    seen.add(Net("a"))
    assert len(seen) == 2

    seen.add(Net("a").add(Net("b"), "edge b").add(Net("c"), "edge c"))
    assert len(seen) == 3
