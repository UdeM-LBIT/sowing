from sowing.net import Net, Zipper


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

    root.label("w")
    assert root.data == "a"

    root = root.label("w")
    assert root.data == "w"
    root = root.label("a")

    root.add(left)
    assert root == Net("a")

    root = root.add(left)
    assert root == Net("a").add(Net("b"))

    root = root.add(left, "data")
    assert root == Net("a").add(Net("b")).add(Net("b"), "data")

    root.pop(0)
    assert root == Net("a").add(Net("b")).add(Net("b"), "data")

    root = root.pop(0)
    assert root == Net("a").add(Net("b"), "data")

    root = root.pop()
    assert root == Net("a")

    root = root.add(left, "before")
    root = root.add(left, "after")
    assert root == Net("a").add(Net("b"), "before").add(Net("b"), "after")

    root = root.replace(0, data="replaced")
    assert root == Net("a").add(Net("b"), "replaced").add(Net("b"), "after")

    root = root.replace(1, child=Net("w"))
    assert root == Net("a").add(Net("b"), "replaced").add(Net("w"), "after")


def test_hashable():
    assert hash(Net(42)) != hash(Net(1337))
    assert hash(Net(1337)) == hash(Net(1337))

    seen = set()
    seen.add(Net("a").add(Net("b")).add(Net("c")))

    assert Net("a").add(Net("b")).add(Net("c")) in seen
    assert Net("a") not in seen

    seen.add(Net("a"))
    assert len(seen) == 2

    seen.add(Net("a").add(Net("b"), "edge b").add(Net("c"), "edge c"))
    assert len(seen) == 3


def test_hash_collisions():
    seen = set()
    repeats = 10_000

    for index in range(repeats):
        seen.add(hash(Net(index)))

    assert len(seen) == repeats


def test_zipper_navigate():
    left = Net("b").add(Net("d").add(Net("e"), "4"), "3")
    right = Net("c")
    root = Net("a").add(left, "1").add(right, "2")

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
        origin=Net("a").add(right, "2"),
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
    left = Net("b").add(Net("d").add(Net("e"), "4"), "3")
    right = Net("c")
    root = Net("a").add(left, "1").add(right, "2")

    zipper = root.unzip().down(1)
    zipper = zipper.replace(zipper.node.label("w"))
    assert zipper.node.data == "w"

    root = zipper.zip()
    assert root == Net("a").add(left, "1").add(Net("w"), "2")

    zipper = root.unzip().down(0)
    zipper = zipper.replace(zipper.node.replace(0, data="8"))
    assert zipper.node.data == "b"
    assert zipper.node.children[0][1] == "8"

    root = zipper.zip()
    assert root == (
        Net("a")
        .add(Net("b").add(Net("d").add(Net("e"), "4"), "8"), "1")
        .add(Net("w"), "2")
    )


def test_zipper_next_prev():
    root = Net("a")
    zipper = root.unzip()

    assert zipper.next() == zipper
    assert zipper.prev() == zipper
    assert zipper.next(preorder=True) == zipper
    assert zipper.prev(preorder=True) == zipper

    root = (
        Net("a")
        .add(Net("b").add(Net("c")))
        .add(Net("d").add(
            Net("e")
            .add(Net("f"))
            .add(Net("g"))
            .add(Net("h").add(Net("i")))
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
