from sowing.node import Node, Zipper


def test_build():
    left = Node("b").add(Node("d").add(Node("e")))
    right = Node("c")
    root = Node("a").add(left).add(right)

    assert root.data == "a"
    assert len(root.children) == 2
    assert (left, None) in root.children
    assert (right, None) in root.children


def test_edges():
    end = Node("e")
    mid = Node("d").add(end, "last edge")
    left = Node("b").add(mid)
    right = Node("c")
    root = Node("a").add(left, "edge 1").add(right, "edge 2")

    assert (left, "edge 1") in root.children
    assert (right, "edge 2") in root.children
    assert (mid, None) in left.children
    assert (end, "last edge") in mid.children


def test_repeat():
    root = Node().add(Node()).add(Node())

    assert len(root.children) == 2
    assert root.children[0] == (Node(), None)
    assert root.children[1] == (Node(), None)


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


def test_modify():
    root = Node("a")
    left = Node("b")

    root.label("w")
    assert root.data == "a"

    root = root.label("w")
    assert root.data == "w"
    root = root.label("a")

    root.add(left)
    assert root == Node("a")

    root = root.add(left)
    assert root == Node("a").add(Node("b"))

    root = root.add(left, "data")
    assert root == Node("a").add(Node("b")).add(Node("b"), "data")

    root.pop(0)
    assert root == Node("a").add(Node("b")).add(Node("b"), "data")

    root = root.pop(0)
    assert root == Node("a").add(Node("b"), "data")

    root = root.pop()
    assert root == Node("a")

    root = root.add(left, "before")
    root = root.add(left, "after")
    assert root == Node("a").add(Node("b"), "before").add(Node("b"), "after")

    root = root.replace(0, data="replaced")
    assert root == Node("a").add(Node("b"), "replaced").add(Node("b"), "after")

    root = root.replace(1, child=Node("w"))
    assert root == Node("a").add(Node("b"), "replaced").add(Node("w"), "after")


def test_hashable():
    assert hash(Node(42)) != hash(Node(1337))
    assert hash(Node(1337)) == hash(Node(1337))

    seen = set()
    seen.add(Node("a").add(Node("b")).add(Node("c")))

    assert Node("a").add(Node("b")).add(Node("c")) in seen
    assert Node("a") not in seen

    seen.add(Node("a"))
    assert len(seen) == 2

    seen.add(Node("a").add(Node("b"), "edge b").add(Node("c"), "edge c"))
    assert len(seen) == 3


def test_hash_collisions():
    seen = set()
    repeats = 10_000

    for index in range(repeats):
        seen.add(hash(Node(index)))

    assert len(seen) == repeats


def test_zipper_navigate():
    left = Node("b").add(Node("d").add(Node("e"), "4"), "3")
    right = Node("c")
    root = Node("a").add(left, "1").add(right, "2")

    zipper = root.unzip()

    assert zipper.node == root
    assert zipper.is_root()
    assert zipper.thread == ()

    zipper.down(0)
    assert zipper == root.unzip()

    zipper = zipper.down(0)
    assert zipper.node == left
    assert not zipper.is_root()
    assert zipper.thread == (Zipper.Bead(
        origin=Node("a").add(right, "2"),
        data="1",
        index=0,
    ),)

    zipper = zipper.up()
    assert zipper.node == root
    assert zipper.is_root()
    assert zipper.thread == ()

    assert zipper.down(0).sibling(0) == zipper.down(0)
    assert zipper.down(1).sibling(-1) == zipper.down(0)
    assert zipper.down(0).sibling(1) == zipper.down(1)
    assert zipper.down(1).sibling(0) == zipper.down(1)
    assert zipper.down().up() == zipper
    assert zipper.down().down().up().up() == zipper
    assert zipper.down(0).sibling(1).sibling(-1) == zipper.down(0)

    assert root == root.unzip().zip()
    assert root == root.unzip().down().down().zip()


def test_zipper_edit():
    left = Node("b").add(Node("d").add(Node("e"), "4"), "3")
    right = Node("c")
    root = Node("a").add(left, "1").add(right, "2")

    zipper = root.unzip().down(1)
    zipper = zipper.replace(zipper.node.label("w"))
    assert zipper.node.data == "w"

    root = zipper.zip()
    assert root == Node("a").add(left, "1").add(Node("w"), "2")

    zipper = root.unzip().down(0)
    zipper = zipper.replace(zipper.node.replace(0, data="8"))
    assert zipper.node.data == "b"
    assert zipper.node.children[0][1] == "8"

    root = zipper.zip()
    assert root == (
        Node("a")
        .add(Node("b").add(Node("d").add(Node("e"), "4"), "8"), "1")
        .add(Node("w"), "2")
    )


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
