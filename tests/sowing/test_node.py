from sowing.node import Node, Edge
from immutables import Map


def test_add_node():
    left = Node("b").add(Node("d").add(Node("e")))
    right = Node("c")
    root = Node("a").add(left).add(right)

    assert root.data == "a"
    assert root.edges == (Edge(left), Edge(right))

    root = Node("a").add(left, data="b").add(right, data="c")
    assert root.edges == (Edge(left, "b"), Edge(right, "c"))

    root = Node("a").add(left, data="b").add(right, data="c", index=0)
    assert root.edges == (Edge(right, "c"), Edge(left, "b"))


def test_add_edge():
    left = Node("b").add(Edge(Node("d").add(Edge(Node("e")))))
    right = Node("c")
    root = Node("a").add(Edge(left)).add(Edge(right))

    assert root.data == "a"
    assert root.edges == (Edge(left), Edge(right))

    root = Node("a").add(Edge(left, "b")).add(Edge(right, "c"))
    assert root.edges == (Edge(left, "b"), Edge(right, "c"))

    root = Node("a").add(Edge(left, "b")).add(Edge(right, "c"), index=0)
    assert root.edges == (Edge(right, "c"), Edge(left, "b"))


def test_repeat():
    root = Node().add(Node()).add(Node())
    assert root.edges == (Edge(Node()), Edge(Node()))


def test_eq():
    root1 = Node("a").add(Node("b").add(Node("d").add(Node("e")))).add(Node("c"))
    root2 = Node("a").add(Node("b").add(Node("d").add(Node("e")))).add(Node("c"))
    root3 = Node("a").add(Node("c")).add(Node("b").add(Node("d").add(Node("e"))))

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
    root = Node("a").add(Node("b"), data="x").add(Node("c"), data="y")
    copy = Node("a").extend(root.edges)

    assert root == copy

    root = Node(-1).extend(map(Node, range(4)))
    assert root == Node(-1).add(Node(0)).add(Node(1)).add(Node(2)).add(Node(3))


def test_hashable():
    assert hash(Node(42)) != hash(Node(1337))
    assert hash(Node(1337)) == hash(Node(1337))
    assert hash(Node(42)) != hash(Node(42).add(Node(42)))
    assert hash(Node(42)) == hash(Node(1337).replace(data=42))
    assert hash(Node(42)) == hash(Node(42).add(Node(21)).replace(edges=()))

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


def test_str():
    ascii_chars = {
        "root": ".",
        "branch": "/",
        "init": "+--",
        "cont": "|  ",
        "init_last": "\\--",
        "cont_last": "   ",
    }

    assert str(Node()) == ""
    assert str(Node(1)) == "1"
    assert str(Node(Map({"x": 42}))) == "{'x': 42}"
    assert str(Node().add(Node()).add(Node())) == "┐\n├──\n└──"
    assert Node().add(Node()).add(Node()).__str__(chars=ascii_chars) == ".\n+--\n\\--"
    assert (
        str(Node(1).add(Node(2).add(Node(3)).add(Node(4))).add(Node(5).add(Node(6))))
        == "1\n├──2\n│  ├──3\n│  └──4\n└──5\n   └──6"
    )
    assert (
        Node(1)
        .add(Node(2).add(Node(3)).add(Node(4)))
        .add(Node(5).add(Node(6)))
        .__str__(chars=ascii_chars)
        == "1\n+--2\n|  +--3\n|  \\--4\n\\--5\n   \\--6"
    )

    assert (
        str(
            Node(1)
            .add(Node(2).add(Node(3)).add(Node(4)), data="st")
            .add(Node(5).add(Node(6), data="ab"), data="xy")
        )
        == "1\n│  ╭st\n├──2\n│  ├──3\n│  └──4\n│  ╭xy\n└──5\n   │  ╭ab\n   └──6"
    )
    assert (
        Node(1)
        .add(Node(2).add(Node(3)).add(Node(4)), data="st")
        .add(Node(5).add(Node(6), data="ab"), data="xy")
        .__str__(chars=ascii_chars)
        == "1\n|  /st\n+--2\n|  +--3\n|  \\--4\n|  /xy\n\\--5\n   |  /ab\n   \\--6"
    )
