from sowing.node import Node
from sowing.zipper import Zipper
import pytest


def test_zip_unzip():
    root = Node("a").add(Node("b").add(Node("d").add(Node("e")))).add(Node("c"))

    zipper = root.unzip()
    assert zipper.node == root
    assert zipper.is_root()
    assert not zipper.is_empty()
    assert not zipper.is_leaf()
    assert zipper.is_last_sibling()
    assert zipper.is_last_sibling(-1)
    assert zipper.parent is None
    assert zipper.index == -1
    assert zipper.zip() == root


def test_invalid():
    with pytest.raises(
        ValueError, match="zipper child index must be in the range of its parent"
    ):
        Zipper(parent=Zipper(Node("a")))

    with pytest.raises(ValueError, match="root zipper child index must be -1"):
        Zipper(index=0)

    with pytest.raises(ValueError, match="parent of a zipper cannot be empty"):
        Zipper(Node("a"), parent=Zipper())


def test_empty():
    zipper = Zipper()
    assert zipper.is_root()
    assert zipper.is_empty()
    assert zipper.is_leaf()

    zipper = Node("a").add(Node("b")).unzip().down().replace(node=None)
    assert not zipper.is_root()
    assert zipper.is_empty()
    assert zipper.is_last_sibling()
    assert zipper.is_last_sibling(-1)

    root = Node("a").add(Node("b")).add(Node("c")).add(Node("d"))
    zipper = root.unzip().down(1).replace(node=None)
    assert not zipper.is_root()
    assert zipper.is_empty()
    assert not zipper.is_last_sibling()
    assert not zipper.is_last_sibling(-1)
    assert zipper.zip() == Node("a").add(Node("b")).add(Node("d"))


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


def test_up_down_sibling():
    root = (
        Node("a")
        .add(Node("b").add(Node("d").add(Node("e"))))
        .add(Node("c"))
        .add(Node("f").add(Node("g")).add(Node("h")))
    )

    zipper = root.unzip()

    assert zipper.is_root()
    assert zipper.depth == 0
    assert not zipper.down(0).is_root()
    assert zipper.down(0).depth == 1
    assert not zipper.is_leaf()
    assert zipper.down().down().down().is_leaf()
    assert zipper.down().down().depth == 2
    assert zipper.down().down().down().depth == 3

    assert zipper.down().up() == zipper
    assert zipper.down().up().depth == 0
    assert zipper.down().down().up().depth == 1
    assert zipper.down().down().up().up() == zipper
    assert zipper.down().down().up().up().depth == 0

    with pytest.raises(IndexError, match="cannot go up"):
        zipper.up()

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
    assert zipper.down().sibling().depth == 1

    assert zipper.is_last_sibling()
    assert not zipper.down(0).is_last_sibling()
    assert zipper.down(0).is_last_sibling(-1)
    assert not zipper.down(0).sibling().is_last_sibling()
    assert not zipper.down(0).sibling().is_last_sibling(-1)
    assert zipper.down(0).sibling(2).is_last_sibling()
    assert not zipper.down(0).sibling(2).is_last_sibling(-1)


def test_children():
    root = (
        Node("a")
        .add(Node("b").add(Node("d").add(Node("e"))))
        .add(Node("c"))
        .add(Node("f").add(Node("g")).add(Node("h")))
    )

    zipper = root.unzip()

    assert list(zipper.children()) == [
        zipper.down(0),
        zipper.down(1),
        zipper.down(2),
    ]

    assert list(zipper.down(0).children()) == [
        zipper.down(0).down(0),
    ]

    assert list(zipper.down(0).down(0).down(0).children()) == []
    assert list(Zipper().children()) == []


def test_root():
    root = (
        Node()
        .add(
            Node()
            .add(Node("a"), data="2")
            .add(Node("b"), data="3")
            .add(Node("c"), data="4"),
            data="1",
        )
        .add(
            Node()
            .add(Node("d"), data="6")
            .add(
                Node()
                .add(Node("e"), data="8")
                .add(
                    Node().add(Node("f"), data="10").add(Node("g"), data="11"),
                    data="9",
                ),
                data="7",
            )
            .add(
                Node().add(Node("h"), data="13").add(Node("i"), data="14"),
                data="12",
            ),
            data="5",
        )
    )
    root_789 = (
        Node()
        .add(Node("e"), data="8")
        .add(
            Node().add(Node("f"), data="10").add(Node("g"), data="11"),
            data="9",
        )
        .add(
            Node()
            .add(
                Node().add(Node("h"), data="13").add(Node("i"), data="14"),
                data="12",
            )
            .add(
                Node().add(
                    Node()
                    .add(Node("a"), data="2")
                    .add(Node("b"), data="3")
                    .add(Node("c"), data="4"),
                    data="1",
                ),
                data="5",
            )
            .add(Node("d"), data="6"),
            data="7",
        )
    )

    assert root.unzip().root() == root.unzip()
    assert root.unzip().down(1).down(1).root() == root_789.unzip()
    assert root_789.unzip().down(2).down(1).root() == root.unzip()


def test_edit():
    left = Node("b").add(Node("d").add(Node("e")))
    right = Node("c")
    root = Node("a").add(left).add(right)

    zipper = root.unzip().down(1).replace(node=lambda x: x.replace(data="w"))
    assert zipper.node.data == "w"

    root = zipper.zip()
    assert root == Node("a").add(left).add(Node("w"))

    zipper = root.unzip().down(0)
    zipper = zipper.replace(node=zipper.node.pop(0).add(Node("z"), index=0))
    assert zipper.node.edges[0].node == Node("z")

    root = zipper.zip()
    assert root == Node("a").add(Node("b").add(Node("z"))).add(Node("w"))


def test_next_prev():
    root = Node("a")
    zipper = root.unzip()

    assert zipper.next() == zipper
    assert zipper.prev() == zipper
    assert zipper.next(preorder=True) == zipper
    assert zipper.prev(preorder=True) == zipper

    root = (
        Node("a")
        .add(Node("b").add(Node("c")))
        .add(
            Node("d").add(
                Node("e").add(Node("f")).add(Node("g")).add(Node("h").add(Node("i")))
            )
        )
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


def test_str():
    ascii_chars = {
        "root": ".",
        "branch": "/",
        "init": "+--",
        "cont": "|  ",
        "init_last": "\\--",
        "cont_last": "   ",
        "highlight": "x ",
    }

    root = Node(1).add(Node(2).add(Node(3)).add(Node(4))).add(Node(5).add(Node(6)))
    cursor = root.unzip()

    assert str(cursor) == "○ 1\n├──2\n│  ├──3\n│  └──4\n└──5\n   └──6"
    assert str(cursor.down()) == "1\n├──○ 2\n│  ├──3\n│  └──4\n└──5\n   └──6"
    assert str(cursor.down(1)) == "1\n├──2\n│  ├──3\n│  └──4\n└──○ 5\n   └──6"
    assert (
        cursor.__str__(chars=ascii_chars)
        == "x 1\n+--2\n|  +--3\n|  \\--4\n\\--5\n   \\--6"
    )
