from sowing.node import Node, Edge, Zipper
import pytest


def test_add_node():
    left = Node("b").add(Node("d").add(Node("e")))
    right = Node("c")
    root = Node("a").add(left).add(right)

    assert root.data == "a"
    assert root.edges == (Edge(left), Edge(right))

    root = Node("a").add(left, "b").add(right, "c")

    assert root.edges == (Edge(left, "b"), Edge(right, "c"))


def test_add_edge():
    left = Node("b").add(Edge(Node("d").add(Edge(Node("e")))))
    right = Node("c")
    root = Node("a").add(Edge(left)).add(Edge(right))

    assert root.data == "a"
    assert root.edges == (Edge(left), Edge(right))

    root = Node("a").add(Edge(left, "b")).add(Edge(right, "c"))

    assert root.edges == (Edge(left, "b"), Edge(right, "c"))


def test_repeat():
    root = Node().add(Node()).add(Node())
    assert root.edges == (Edge(Node()), Edge(Node()))


def test_eq():
    root1 = Node("a") \
        .add(Node("b").add(Node("d").add(Node("e")))) \
        .add(Node("c"))

    root2 = Node("a") \
        .add(Node("b").add(Node("d").add(Node("e")))) \
        .add(Node("c"))

    root3 = Node("a") \
        .add(Node("c")) \
        .add(Node("b").add(Node("d").add(Node("e"))))

    assert root1 == root2
    assert root1 != root3
    assert root2 != root3

    subtree1 = Node().add(Node()).add(Node())
    subtree2 = Node().add(Node())
    repeat1 = Node().add(subtree1).add(subtree1)
    repeat2 = Node().add(subtree1).add(subtree1)

    assert subtree1 != subtree2
    assert repeat1 == repeat2


def test_pop_replace():
    root = Node("a")
    child1 = Node("b")
    child2 = Node("c")

    root.replace(data="w")
    assert root.data == "a"

    root = root.replace(data="w")
    assert root.data == "w"
    root = root.replace(data="a")

    root.add(child1)
    assert root == Node("a")

    root = root.add(child1)
    assert root == Node("a").add(Node("b"))

    root = root.add(child1)
    assert root == Node("a").add(Node("b")).add(Node("b"))

    root = root.add(child2)
    assert root == Node("a").add(Node("b")).add(Node("b")).add(Node("c"))

    root.pop(0)
    assert root == Node("a").add(Node("b")).add(Node("b")).add(Node("c"))

    root = root.pop(0)
    assert root == Node("a").add(Node("b")).add(Node("c"))

    root = root.pop()
    assert root == Node("a").add(Node("b"))

    root = root.add(child2, index=0)
    assert root == Node("a").add(Node("c")).add(Node("b"))

    root = root.pop(0).add(child1, index=0)
    assert root == Node("a").add(Node("b")).add(Node("b"))

    root = root.pop(1).add(child2, index=1)
    assert root == Node("a").add(Node("b")).add(Node("c"))


def test_extend():
    root = Node("a").add(Node("b"), "x").add(Node("c"), "y")
    copy = Node("a").extend(root.edges)

    assert root == copy

    root = Node(-1).extend(map(Node, range(4)))
    assert root == Node(-1).add(Node(0)).add(Node(1)).add(Node(2)).add(Node(3))


def test_hashable():
    assert hash(Node(42)) != hash(Node(1337))
    assert hash(Node(1337)) == hash(Node(1337))

    seen = set()
    seen.add(Node("a").add(Node("b")).add(Node("c")))

    assert Node("a").add(Node("b")).add(Node("c")) in seen
    assert Node("a") not in seen

    seen.add(Node("a"))
    assert len(seen) == 2

    seen.add(Node("a").add(Node("c")).add(Node("b")))
    assert len(seen) == 3

    seen.add(Node("a").add(Node("b")).add(Node("c")).add(Node("c")))
    assert len(seen) == 4


def test_hash_collisions():
    seen = set()
    repeats = 10_000

    for index in range(repeats):
        seen.add(hash(Node(index)))

    assert len(seen) == repeats


def test_zip_unzip():
    root = (
        Node("a")
        .add(Node("b").add(Node("d").add(Node("e"))))
        .add(Node("c"))
    )

    zipper = root.unzip()
    assert zipper.node == root
    assert zipper.is_root()
    assert zipper.parent is None
    assert zipper.index == -1
    assert zipper.zip() == root


def test_zipper_thread():
    left = Node("b").add(Node("d").add(Node("e")))
    right = Node("c")
    root = Node("a").add(left).add(right)

    zipper = root.unzip()

    zipper.down(0)
    assert zipper == root.unzip()

    zipper = zipper.down(0)
    assert zipper.node == left
    assert zipper.parent is not None
    assert zipper.parent.node == Node("a").add(right)
    assert zipper.parent.parent is None
    assert zipper.index == 0

    assert root.unzip().down().down().zip() == root


def test_zipper_up_down_sibling():
    root = (
        Node("a")
        .add(Node("b").add(Node("d").add(Node("e"))))
        .add(Node("c"))
        .add(Node("f").add(Node("g")).add(Node("h")))
    )

    zipper = root.unzip()

    assert zipper.is_root()
    assert not zipper.down(0).is_root()
    assert not zipper.is_leaf()
    assert zipper.down().down().down().is_leaf()

    assert zipper.down().up() == zipper
    assert zipper.down().down().up().up() == zipper

    with pytest.raises(IndexError) as error:
        zipper.up()

    assert "cannot go up" in str(error)

    assert zipper.down(0).sibling(0) == zipper.down(0)
    assert zipper.down(1).sibling(-1) == zipper.down(0)
    assert zipper.down(0).sibling(1) == zipper.down(1)
    assert zipper.down(1).sibling(0) == zipper.down(1)
    assert zipper.down(0).sibling(1).sibling(-1) == zipper.down(0)
    assert zipper.down(0).sibling(-1).sibling(1) == zipper.down(0)
    assert zipper.down(0).sibling() == zipper.down(1)
    assert zipper.down(0).sibling().sibling() == zipper.down(2)
    assert zipper.down(0).sibling().sibling().sibling() == zipper.down(0)
    assert zipper.down(0).sibling(-1) == zipper.down(2)
    assert zipper.down(0).sibling(-1).sibling(-1) == zipper.down(1)
    assert zipper.down(0).sibling(-1).sibling(-1).sibling(-1) == zipper.down(0)
    assert zipper.down(0).down(0).sibling() == zipper.down(0).down(0)
    assert zipper.sibling() == zipper

    assert zipper.is_last_sibling()
    assert not zipper.down(0).is_last_sibling()
    assert zipper.down(0).is_last_sibling(-1)
    assert not zipper.down(0).sibling().is_last_sibling()
    assert not zipper.down(0).sibling().is_last_sibling(-1)
    assert zipper.down(0).sibling(2).is_last_sibling()
    assert not zipper.down(0).sibling(2).is_last_sibling(-1)


def test_zipper_edit():
    left = Node("b").add(Node("d").add(Node("e")))
    right = Node("c")
    root = Node("a").add(left).add(right)

    zipper = root.unzip().down(1)
    zipper = zipper.replace(node=zipper.node.replace(data="w"))
    assert zipper.node.data == "w"

    root = zipper.zip()
    assert root == Node("a").add(left).add(Node("w"))

    zipper = root.unzip().down(0)
    zipper = zipper.replace(node=zipper.node.pop(0).add(Node("z"), index=0))
    assert zipper.node.edges[0].node == Node("z")

    root = zipper.zip()
    assert root == Node("a").add(Node("b").add(Node("z"))).add(Node("w"))


def test_zipper_next_prev():
    root = Node("a")
    zipper = root.unzip()

    assert zipper.next() == zipper
    assert zipper.prev() == zipper
    assert zipper.next(preorder=True) == zipper
    assert zipper.prev(preorder=True) == zipper

    root = (
        Node("a")
        .add(Node("b").add(Node("c")))
        .add(Node("d").add(
            Node("e")
            .add(Node("f"))
            .add(Node("g"))
            .add(Node("h").add(Node("i")))
        ))
    )
    zipper = root.unzip()
    assert zipper.node == root

    assert (zipper := zipper.next()).node.data == "c"
    assert (zipper := zipper.next()).node.data == "b"
    assert (zipper := zipper.next()).node.data == "f"
    assert (zipper := zipper.next()).node.data == "g"
    assert (zipper := zipper.next()).node.data == "i"
    assert (zipper := zipper.next()).node.data == "h"
    assert (zipper := zipper.next()).node.data == "e"
    assert (zipper := zipper.next()).node.data == "d"
    assert (zipper := zipper.next()).node == root

    assert (zipper := zipper.prev()).node.data == "d"
    assert (zipper := zipper.prev()).node.data == "e"
    assert (zipper := zipper.prev()).node.data == "h"
    assert (zipper := zipper.prev()).node.data == "i"
    assert (zipper := zipper.prev()).node.data == "g"
    assert (zipper := zipper.prev()).node.data == "f"
    assert (zipper := zipper.prev()).node.data == "b"
    assert (zipper := zipper.prev()).node.data == "c"
    assert (zipper := zipper.prev()).node == root

    assert (zipper := zipper.next(preorder=True)).node.data == "b"
    assert (zipper := zipper.next(preorder=True)).node.data == "c"
    assert (zipper := zipper.next(preorder=True)).node.data == "d"
    assert (zipper := zipper.next(preorder=True)).node.data == "e"
    assert (zipper := zipper.next(preorder=True)).node.data == "f"
    assert (zipper := zipper.next(preorder=True)).node.data == "g"
    assert (zipper := zipper.next(preorder=True)).node.data == "h"
    assert (zipper := zipper.next(preorder=True)).node.data == "i"
    assert (zipper := zipper.next(preorder=True)).node == root

    assert (zipper := zipper.prev(preorder=True)).node.data == "i"
    assert (zipper := zipper.prev(preorder=True)).node.data == "h"
    assert (zipper := zipper.prev(preorder=True)).node.data == "g"
    assert (zipper := zipper.prev(preorder=True)).node.data == "f"
    assert (zipper := zipper.prev(preorder=True)).node.data == "e"
    assert (zipper := zipper.prev(preorder=True)).node.data == "d"
    assert (zipper := zipper.prev(preorder=True)).node.data == "c"
    assert (zipper := zipper.prev(preorder=True)).node.data == "b"
    assert (zipper := zipper.prev(preorder=True)).node == root
