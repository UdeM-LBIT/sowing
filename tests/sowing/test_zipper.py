from sowing.node import Node
from sowing.zipper import Zipper
import pytest


def test_zip_unzip():
    root = Node("a").add(Node("b").add(Node("d").add(Node("e")))).add(Node("c"))

    zipper = root.unzip()
    assert zipper.node is root
    assert zipper.is_root()
    assert not zipper.is_empty()
    assert not zipper.is_leaf()
    assert zipper.is_last_sibling()
    assert zipper.is_last_sibling(-1)
    assert zipper.parent is None
    assert zipper.index == -1
    assert zipper.zip() is root


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
    assert zipper.node is left
    assert zipper.parent is not None
    assert zipper.parent.node is root
    assert zipper.parent.parent is None
    assert zipper.index == 0

    assert root.unzip().down().down().zip() is root
    assert root.unzip().down(1).zip() is root


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


def test_edit():
    left = Node("b").add(Node("d").add(Node("e")))
    right = Node("c")
    root = Node("a").add(left).add(right)

    zipper = root.unzip().down(1).replace(node=lambda x: x.replace(data="w"))
    assert zipper.node.data == "w"
    assert zipper.zip() == Node("a").add(left).add(Node("w"))

    zipper = root.unzip().down(0)
    zipper = zipper.replace(node=zipper.node.pop(0).add(Node("z"), index=0))
    assert zipper.node.edges[0].node == Node("z")
    assert zipper.zip() == Node("a").add(Node("b").add(Node("z"))).add(Node("c"))

    zipper = root.unzip().down(1)
    zipper = zipper.replace(data="right")
    assert zipper.zip() == Node("a").add(left).add(right, data="right")


def test_root():
    root = Node("c").add(Node("a"), data="left").add(Node("b"), data="right")
    root_left = Node("a").add(Node("c").add(Node("b"), data="right"), data="left")
    assert root.unzip().root().zip() is root
    assert root.unzip().down().root().zip() == root_left

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

    assert root.unzip().root().zip() is root
    assert root.unzip().down(1).down(1).root() == root_789.unzip()
    assert root_789.unzip().down(2).down(1).root() == root.unzip()


def test_next_prev():
    root = Node("a")
    zipper = root.unzip()

    assert zipper.next() == zipper
    assert zipper.prev() == zipper
    assert zipper.next(preorder=True) == zipper
    assert zipper.prev(preorder=True) == zipper

    c = Node("c")
    b = Node("b").add(c)
    f = Node("f")
    g = Node("g")
    i = Node("i")
    h = Node("h").add(i)
    e = Node("e").add(f).add(g).add(h)
    d = Node("d").add(e)
    a = Node("a").add(b).add(d)

    #   a
    #  / \
    # b   d
    # |   |
    # c   e
    #    /|\
    #   f g h
    #       |
    #       i

    zipper = a.unzip()
    assert (zipper := zipper.next()).node is c
    assert (zipper := zipper.next()).node is b
    assert (zipper := zipper.next()).node is f
    assert (zipper := zipper.next()).node is g
    assert (zipper := zipper.next()).node is i
    assert (zipper := zipper.next()).node is h
    assert (zipper := zipper.next()).node is e
    assert (zipper := zipper.next()).node is d
    assert (zipper := zipper.next()).node is a

    zipper = a.unzip()
    assert zipper.next(skip={a}).node is a
    assert zipper.next(skip={b}).node is b
    zipper = a.unzip().down()
    assert zipper.next(skip={d}).node is d
    zipper = a.unzip().down()
    assert zipper.next(skip={e}).node is e

    zipper = a.unzip()
    assert (zipper := zipper.prev()).node is d
    assert (zipper := zipper.prev()).node is e
    assert (zipper := zipper.prev()).node is h
    assert (zipper := zipper.prev()).node is i
    assert (zipper := zipper.prev()).node is g
    assert (zipper := zipper.prev()).node is f
    assert (zipper := zipper.prev()).node is b
    assert (zipper := zipper.prev()).node is c
    assert (zipper := zipper.prev()).node is a

    zipper = a.unzip()
    assert zipper.prev(skip={a}).node is a
    zipper = a.unzip().down()
    assert zipper.prev(skip={b}).node is a
    zipper = a.unzip().down(1).down()
    assert zipper.prev(skip={e}).node is b
    zipper = a.unzip().down(1).down().down(1)
    assert zipper.prev(skip={g}).node is f

    zipper = a.unzip()
    assert (zipper := zipper.next(preorder=True)).node is b
    assert (zipper := zipper.next(preorder=True)).node is c
    assert (zipper := zipper.next(preorder=True)).node is d
    assert (zipper := zipper.next(preorder=True)).node is e
    assert (zipper := zipper.next(preorder=True)).node is f
    assert (zipper := zipper.next(preorder=True)).node is g
    assert (zipper := zipper.next(preorder=True)).node is h
    assert (zipper := zipper.next(preorder=True)).node is i
    assert (zipper := zipper.next(preorder=True)).node is a

    zipper = a.unzip()
    assert zipper.next(preorder=True, skip={a}).node is a
    zipper = a.unzip().down()
    assert zipper.next(preorder=True, skip={b}).node is d
    zipper = a.unzip().down(1).down()
    assert zipper.next(preorder=True, skip={e}).node is a
    zipper = a.unzip().down(1).down().down(1)
    assert zipper.next(preorder=True, skip={g}).node is h

    zipper = a.unzip()
    assert (zipper := zipper.prev(preorder=True)).node is i
    assert (zipper := zipper.prev(preorder=True)).node is h
    assert (zipper := zipper.prev(preorder=True)).node is g
    assert (zipper := zipper.prev(preorder=True)).node is f
    assert (zipper := zipper.prev(preorder=True)).node is e
    assert (zipper := zipper.prev(preorder=True)).node is d
    assert (zipper := zipper.prev(preorder=True)).node is c
    assert (zipper := zipper.prev(preorder=True)).node is b
    assert (zipper := zipper.prev(preorder=True)).node is a

    zipper = a.unzip()
    assert zipper.prev(preorder=True, skip={a}).node is a
    zipper = a.unzip().down()
    assert zipper.prev(preorder=True, skip={b}).node is a
    zipper = a.unzip().down(1).down()
    assert zipper.prev(preorder=True, skip={e}).node is d
    zipper = a.unzip().down(1).down().down(1)
    assert zipper.prev(preorder=True, skip={g}).node is f


def test_str():
    root = (
        Node(1)
        .add(Node(2).add(Node(3)).add(Node(4).add(Node(5))))
        .add(Node(6).add(Node(4).add(Node(5))))
    )
    cursor = root.unzip()

    assert str(cursor) == "\n".join(
        (
            "○ 1",
            "├──2",
            "│  ├──3",
            "│  └──4",
            "│     └──5",
            "└──6",
            "   └──4 (…)",
        )
    )
    assert str(cursor.down()) == "\n".join(
        (
            "1",
            "├──○ 2",
            "│  ├──3",
            "│  └──4",
            "│     └──5",
            "└──6",
            "   └──4 (…)",
        )
    )
    assert cursor.__str__(
        chars={
            "root": ".",
            "branch": "/",
            "init": "+--",
            "cont": "|  ",
            "init_last": "\\--",
            "cont_last": "   ",
            "highlight": "x ",
            "repeat": " (repeat)",
        }
    ) == "\n".join(
        (
            r"x 1",
            r"+--2",
            r"|  +--3",
            r"|  \--4",
            r"|     \--5",
            r"\--6",
            r"   \--4 (repeat)",
        )
    )
