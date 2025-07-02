from sowing.node import Node, Edge
from immutables import Map
from itertools import product
import pytest
import sys


def test_add_node():
    data_a = object()
    data_b = object()
    data_c = object()
    data_d = object()
    data_e = object()

    left = Node(data_b).add(Node(data_d).add(Node(data_e)))
    right = Node(data_c)
    root = Node(data_a).add(left).add(right)

    assert root.data is data_a
    assert len(root.edges) == 2
    assert root.edges[0].data is None
    assert root.edges[0].node is left
    assert root.edges[1].data is None
    assert root.edges[1].node is right

    root = Node(data_a).add(left, data=data_b).add(right, data=data_c)
    assert len(root.edges) == 2
    assert root.edges[0].data is data_b
    assert root.edges[0].node is left
    assert root.edges[1].data is data_c
    assert root.edges[1].node is right

    root = Node(data_a).add(left, data=data_b).add(right, data=data_c, index=0)
    assert len(root.edges) == 2
    assert root.edges[0].data is data_c
    assert root.edges[0].node is right
    assert root.edges[1].data is data_b
    assert root.edges[1].node is left

    with pytest.raises(TypeError) as err:
        root.add(Map())

    assert f"cannot add object of type {type(Map())}" in str(err.value)


def test_add_edge():
    data_a = object()
    data_b = object()
    data_c = object()
    data_d = object()
    data_e = object()

    left = Node(data_b).add(Edge(Node(data_d).add(Edge(Node(data_e)))))
    right = Node(data_c)
    root = Node(data_a).add(Edge(left)).add(Edge(right))

    assert root.data is data_a
    assert len(root.edges) == 2
    assert root.edges[0].data is None
    assert root.edges[0].node is left
    assert root.edges[1].data is None
    assert root.edges[1].node is right

    root = Node(data_a).add(Edge(left, data_b)).add(Edge(right, data_c))
    assert len(root.edges) == 2
    assert root.edges[0].data is data_b
    assert root.edges[0].node is left
    assert root.edges[1].data is data_c
    assert root.edges[1].node is right

    root = Node(data_a).add(Edge(left, data_b)).add(Edge(right, data_c), index=0)
    assert len(root.edges) == 2
    assert root.edges[0].data is data_c
    assert root.edges[0].node is right
    assert root.edges[1].data is data_b
    assert root.edges[1].node is left


def test_add_repeat():
    left = Node()
    right = Node()
    root = Node().add(left).add(right)

    assert len(root.edges) == 2
    assert root.edges[0].data is None
    assert root.edges[0].node is left
    assert root.edges[1].data is None
    assert root.edges[1].node is right


def test_replace():
    node_a = Node("a")
    node_b = Node("b")

    node_a.replace(data="w")
    assert node_a.data == "a"

    assert node_a.replace(data="w").data == "w"
    assert node_a.replace(data=lambda x: x + "u").data == "au"

    assert Edge(node_a).replace(node=node_b).node is node_b
    assert Edge(node_a).replace(node=lambda _: node_b).node is node_b


def test_pop():
    node_b = Node("b")
    node_c = Node("c")
    node_d = Node("d")
    root = Node("a").add(node_b).add(node_c).add(node_d)

    root = root.pop(0)
    assert len(root.edges) == 2
    assert root.edges[0].node is node_c
    assert root.edges[1].node is node_d

    root = root.pop()
    assert len(root.edges) == 1
    assert root.edges[0].node is node_c

    root = root.add(node_b, index=0)
    assert len(root.edges) == 2
    assert root.edges[0].node is node_b
    assert root.edges[1].node is node_c

    root = root.add(node_d)
    assert len(root.edges) == 3
    assert root.edges[0].node is node_b
    assert root.edges[1].node is node_c
    assert root.edges[2].node is node_d

    with pytest.raises(IndexError, match="pop index out of range"):
        root.pop(3)


def test_extend():
    node_b = Node("b")
    node_c = Node("c")
    node_d = Node("d")
    node_a = Node("a").add(node_b, data="x").add(node_c, data="y").add(node_d)
    copy = Node("a").extend(node_a.edges)

    assert len(copy.edges) == 3
    assert copy.edges[0].node is node_b
    assert copy.edges[0].data == "x"
    assert copy.edges[1].node is node_c
    assert copy.edges[1].data == "y"
    assert copy.edges[2].node is node_d
    assert copy.edges[2].data is None


def test_eq_hash():
    assert Node("a") == Node("a")
    assert hash(Node("a")) == hash(Node("a"))

    assert Node("b") != Node("a")
    assert hash(Node("b")) != hash(Node("a"))

    root1 = Node("a").add(Node("b").add(Node("d").add(Node("e")))).add(Node("c"))
    root2 = Node("a").add(Node("b").add(Node("d").add(Node("e")))).add(Node("c"))
    root3 = Node("a").add(Node("c")).add(Node("b").add(Node("d").add(Node("e"))))

    assert root1 == root2
    assert hash(root1) == hash(root2)
    assert root1 != root3
    assert hash(root1) != hash(root3)
    assert root2 != root3
    assert hash(root2) != hash(root3)

    subtree1 = Node().add(Node()).add(Node())
    subtree2 = Node().add(Node())

    assert subtree1 != subtree2
    assert hash(subtree1) != hash(subtree2)

    assert Node("a").add(Node("b")).add(Node("c")) == Node("a").add(Node("b")).add(
        Node("c")
    )
    assert hash(Node("a").add(Node("b")).add(Node("c"))) == hash(
        Node("a").add(Node("b")).add(Node("c"))
    )

    assert Node("a").add(Node("b")).add(Node("c")) != Node("a").add(Node("b")).add(
        Node("d")
    )
    assert hash(Node("a").add(Node("b")).add(Node("c"))) != hash(
        Node("a").add(Node("b")).add(Node("d"))
    )

    assert Node("a").add(Node("b")).add(Node("c")) != Node("a").add(
        Node("b").add(Node("c"))
    )
    assert hash(Node("a").add(Node("b")).add(Node("c"))) != hash(
        Node("a").add(Node("b").add(Node("c")))
    )

    assert Node("a").add(Node("b"), data="l").add(Node("c"), data="r") == Node("a").add(
        Node("b"), data="l"
    ).add(Node("c"), data="r")
    assert hash(Node("a").add(Node("b"), data="l").add(Node("c"), data="r")) == hash(
        Node("a").add(Node("b"), data="l").add(Node("c"), data="r")
    )

    assert Node("a").add(Node("b"), data="l").add(Node("c"), data="r") != Node("a").add(
        Node("b"), data="l"
    ).add(Node("c"), data="w")
    assert hash(Node("a").add(Node("b"), data="l").add(Node("c"), data="r")) != hash(
        Node("a").add(Node("b"), data="l").add(Node("c"), data="w")
    )

    node_b_first = Node("b")
    tree0_first = (
        Node("a").add(node_b_first).add(Node("b")).add(node_b_first).add(node_b_first)
    )

    node_b_second = Node("b")
    tree0_second = (
        Node("a")
        .add(Node("b"))
        .add(node_b_second)
        .add(node_b_second)
        .add(node_b_second)
    )

    assert tree0_first == tree0_second
    assert hash(tree0_first) == hash(tree0_second)

    tree1 = (
        Node("a")
        .add(Node("b").add(Node("c").add(Node("d")).add(Node("e"))).add(Node("f")))
        .add(Node("c").add(Node("d")).add(Node("e")))
    )

    tree2 = Node("a").add(
        Node("b").add(Node("c").add(Node("d")).add(Node("e"))).add(Node("f"))
    )

    assert tree1 != tree2
    assert hash(tree1) != hash(tree2)

    subtree1 = Node("c").add(Node("d")).add(Node("e"))
    tree1_repeat = Node("a").add(Node("b").add(subtree1).add(Node("f"))).add(subtree1)

    assert tree1 == tree1_repeat
    assert hash(tree1) == hash(tree1_repeat)

    assert tree2 != tree1_repeat
    assert hash(tree2) != hash(tree1_repeat)


def _make_rec(depth):
    nodes = [None] * depth

    for i in range(depth):
        if i == 0:
            nodes[i] = Node(0)
        else:
            nodes[i] = Node(i).add(nodes[i - 1])

    return nodes[depth - 1]


def test_eq_hash_rec():
    rec_limit = sys.getrecursionlimit()
    root1 = _make_rec(rec_limit * 2)
    root2 = _make_rec(rec_limit * 2)
    root3 = _make_rec(rec_limit * 3)

    assert root1 != root3
    assert hash(root1) != hash(root3)

    assert root1 == root1
    assert hash(root1) == hash(root1)

    assert root1 == root2
    assert hash(root1) == hash(root2)


def _make_grid(size, corner_data=None):
    grid = [[None] * size for _ in range(size)]

    for i, j in product(range(size), range(size)):
        if i == size - 1 and j == 0 and corner_data is not None:
            # The last node that will be visited in depth-first order
            data = corner_data
        else:
            data = (i, j)

        if i == 0 and j == 0:
            grid[i][j] = Node(data)
        elif i == 0:
            grid[i][j] = Node(data).add(grid[i][j - 1])
        elif j == 0:
            grid[i][j] = Node(data).add(grid[i - 1][j])
        else:
            grid[i][j] = Node(data).add(grid[i - 1][j]).add(grid[i][j - 1])

    return grid[size - 1][size - 1]


def test_eq_hash_exp():
    # Check equality and hash on DAGs containing a very large number of paths
    # (for size=30, 118 264 581 564 861 424 paths)
    # No naive implementation would pass this test in a reasonable time
    root1 = _make_grid(size=30, corner_data=(29, 0))
    root2 = _make_grid(size=30, corner_data=(29, 0))
    root3 = _make_grid(size=30, corner_data="test")

    assert root1 != root3
    assert hash(root1) != hash(root3)

    assert root1 == root1
    assert hash(root1) == hash(root1)

    assert root1 == root2
    assert hash(root1) == hash(root2)


def test_hash_collisions():
    seen = set()
    repeats = 10_000

    for index in range(repeats):
        seen.add(hash(Node(index)))

    assert len(seen) == repeats


def test_str():
    ascii_chars = {
        "root": ".",
        "branch": "/",
        "init": "+--",
        "cont": "|  ",
        "init_last": "\\--",
        "cont_last": "   ",
        "highlight": "x ",
        "repeat": " (repeat)",
    }

    assert str(Node()) == ""
    assert str(Node(1)) == "1"
    assert str(Node(Map({"x": 42}))) == "{'x': 42}"
    assert str(Node().add(Node()).add(Node())) == (
        "\n".join(
            (
                "┐",
                "├──",
                "└──",
            )
        )
    )
    assert Node().add(Node()).add(Node()).__str__(chars=ascii_chars) == (
        "\n".join(
            (
                r".",
                r"+--",
                r"\--",
            )
        )
    )
    assert str(
        Node(1).add(Node(2).add(Node(3)).add(Node(4))).add(Node(5).add(Node(6)))
    ) == "\n".join(
        (
            "1",
            "├──2",
            "│  ├──3",
            "│  └──4",
            "└──5",
            "   └──6",
        )
    )
    assert Node(1).add(Node(2).add(Node(3)).add(Node(4))).add(
        Node(5).add(Node(6))
    ).__str__(chars=ascii_chars) == "\n".join(
        (
            r"1",
            r"+--2",
            r"|  +--3",
            r"|  \--4",
            r"\--5",
            r"   \--6",
        )
    )

    assert str(
        Node(1)
        .add(Node(2).add(Node(3)).add(Node(4)), data="st")
        .add(Node(5).add(Node(6), data="ab"), data="xy")
    ) == "\n".join(
        (
            "1",
            "│  ╭st",
            "├──2",
            "│  ├──3",
            "│  └──4",
            "│  ╭xy",
            "└──5",
            "   │  ╭ab",
            "   └──6",
        )
    )
    assert Node(1).add(Node(2).add(Node(3)).add(Node(4)), data="st").add(
        Node(5).add(Node(6), data="ab"), data="xy"
    ).__str__(chars=ascii_chars) == "\n".join(
        (
            r"1",
            r"|  /st",
            r"+--2",
            r"|  +--3",
            r"|  \--4",
            r"|  /xy",
            r"\--5",
            r"   |  /ab",
            r"   \--6",
        )
    )

    assert str(_make_grid(3)) == "\n".join(
        (
            "(2, 2)",
            "├──(1, 2)",
            "│  ├──(0, 2)",
            "│  │  └──(0, 1)",
            "│  │     └──(0, 0)",
            "│  └──(1, 1)",
            "│     ├──(0, 1) (…)",
            "│     └──(1, 0)",
            "│        └──(0, 0)",
            "└──(2, 1)",
            "   ├──(1, 1) (…)",
            "   └──(2, 0)",
            "      └──(1, 0) (…)",
        )
    )
