import pytest
from sowing.net import Net


def test_build():
    left = Net("b").add(Net("d").add(Net("e")))
    right = Net("c")
    root = Net("a").add(left).add(right)

    assert root.data == "a"
    assert len(root.children) == 2

    assert left in root.children
    assert right in root.children

    assert root.children[left] is None
    assert root.children[right] is None


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

    merge1_sub = Net("x")
    merge1 = Net("a") \
        .add(Net("b").add(merge1_sub)) \
        .add(Net("c").add(merge1_sub))

    merge2_sub = Net("x")
    merge2 = Net("a") \
        .add(Net("b").add(merge2_sub)) \
        .add(Net("c").add(merge2_sub))

    assert merge1 == merge2


def test_edges():
    end = Net("e")
    mid = Net("d").add(end, "last edge")
    left = Net("b").add(mid)
    right = Net("c")
    root = Net("a").add(left, "edge 1").add(right, "edge 2")

    assert root.children[left] == "edge 1"
    assert root.children[right] == "edge 2"
    assert left.children[mid] is None
    assert mid.children[end] == "last edge"


def test_modify():
    root = Net("a")
    left = Net("b")

    root.add(left)
    assert root == Net("a")

    root = root.add(left)
    assert root == Net("a").add(Net("b"))

    root.add(left, "data")
    assert root.children[left] is None

    root = root.add(left, "data")
    assert root.children[left] == "data"

    root.discard(left)
    assert root.children[left] == "data"

    root = root.discard(left)
    assert left not in root.children

    with pytest.raises(KeyError):
        root.remove(left)


def test_hashable():
    seen = set()
    seen.add(Net("a").add(Net("b")).add(Net("c")))

    assert Net("a").add(Net("b")).add(Net("c")) in seen
    assert Net("a") not in seen

    seen.add(Net("a"))
    assert len(seen) == 2

    seen.add(Net("a").add(Net("b"), "edge b").add(Net("c"), "edge c"))
    assert len(seen) == 3
