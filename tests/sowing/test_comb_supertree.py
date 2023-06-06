from sowing.node import Node
from sowing.comb.supertree import Triple, Fan, breakup, build, supertree


def test_breakup():
    assert breakup(Node("a")) == ([Node("a")], [], [])

    assert breakup(Node().add(Node("b")).add(Node("c"))) == (
        [Node("b"), Node("c")],
        [],
        [],
    )

    assert breakup(Node().add(Node().add(Node("b")).add(Node("c")))) == (
        [Node("b"), Node("c")],
        [],
        [],
    )

    assert breakup(Node().add(Node("e")).add(Node().add(Node("c")).add(Node("d")))) == (
        [
            Node("e"),
            Node("c"),
            Node("d"),
        ],
        [
            Triple((Node("c"), Node("d")), Node("e")),
        ],
        [],
    )

    assert breakup(
        Node()
        .add(Node().add(Node("a")).add(Node("b")))
        .add(Node().add(Node("c")).add(Node("d")))
    ) == (
        [Node("a"), Node("b"), Node("c"), Node("d")],
        [
            Triple((Node("a"), Node("b")), Node("c")),
            Triple((Node("c"), Node("d")), Node("a")),
        ],
        [],
    )

    assert breakup(
        Node()
        .add(Node().add(Node().add(Node("d")).add(Node("e"))).add(Node("f")))
        .add(Node().add(Node("h")).add(Node("i")))
    ) == (
        [Node("d"), Node("e"), Node("f"), Node("h"), Node("i")],
        [
            Triple((Node("d"), Node("e")), Node("f")),
            Triple((Node("d"), Node("f")), Node("h")),
            Triple((Node("h"), Node("i")), Node("d")),
        ],
        [],
    )

    assert breakup(
        Node().add(Node().add(Node().add(Node("b")).add(Node("c")))).add(Node("a"))
    ) == (
        [Node("b"), Node("c"), Node("a")],
        [
            Triple((Node("b"), Node("c")), Node("a")),
        ],
        [],
    )

    assert breakup(Node().add(Node("b")).add(Node("c")).add(Node("d"))) == (
        [Node("b"), Node("c"), Node("d")],
        [],
        [
            Fan((Node("b"), Node("c"), Node("d"))),
        ],
    )

    assert breakup(
        Node()
        .add(Node().add(Node("b")).add(Node("c")).add(Node("d")))
        .add(Node().add(Node("e")).add(Node("f")))
        .add(Node("z"))
    ) == (
        [Node("b"), Node("c"), Node("d"), Node("e"), Node("f"), Node("z")],
        [
            Triple((Node("b"), Node("c")), Node("e")),
            Triple((Node("e"), Node("f")), Node("z")),
        ],
        [
            Fan((Node("b"), Node("c"), Node("d"))),
            Fan((Node("b"), Node("e"), Node("z"))),
        ],
    )


def test_build():
    assert build([Node("a")], [], []) == Node("a")

    assert build([Node("a"), Node("b")], [], []) == (
        Node().add(Node("a")).add(Node("b"))
    )

    assert build([Node("a"), Node("b"), Node("c")], [], []) == (
        Node().add(Node("a")).add(Node("b")).add(Node("c"))
    )

    assert build(
        [Node("a"), Node("b"), Node("c")],
        [
            Triple((Node("b"), Node("c")), Node("a")),
        ],
        [],
    ) == (Node().add(Node("a")).add(Node().add(Node("b")).add(Node("c"))))

    assert (
        build(
            [Node("a"), Node("b"), Node("c")],
            [
                Triple((Node("b"), Node("c")), Node("a")),
                Triple((Node("b"), Node("a")), Node("c")),
            ],
            [],
        )
        is None
    )

    assert build(
        [Node("a"), Node("b"), Node("c"), Node("d")],
        [
            Triple((Node("a"), Node("b")), Node("c")),
            Triple((Node("c"), Node("d")), Node("a")),
        ],
        [],
    ) == (
        Node()
        .add(Node().add(Node("a")).add(Node("b")))
        .add(Node().add(Node("c")).add(Node("d")))
    )

    assert (
        build(
            [Node("a"), Node("b"), Node("c"), Node("d")],
            [
                Triple((Node("a"), Node("b")), Node("c")),
                Triple((Node("c"), Node("d")), Node("a")),
            ],
            [Fan((Node("a"), Node("b"), Node("c")))],
        )
        is None
    )

    assert build(
        [Node("b"), Node("c"), Node("d"), Node("e"), Node("f"), Node("z")],
        [
            Triple((Node("b"), Node("c")), Node("e")),
            Triple((Node("e"), Node("f")), Node("z")),
        ],
        [
            Fan((Node("b"), Node("c"), Node("d"))),
            Fan((Node("b"), Node("e"), Node("z"))),
        ],
    ) == (
        Node()
        .add(Node().add(Node("b")).add(Node("c")).add(Node("d")))
        .add(Node().add(Node("e")).add(Node("f")))
        .add(Node("z"))
    )


def test_supertree():
    assert supertree(
        Node()
        .add(Node().add(Node("a")).add(Node("b")))
        .add(Node().add(Node("c")).add(Node("d"))),
    ) == (
        Node()
        .add(Node().add(Node("a")).add(Node("b")))
        .add(Node().add(Node("c")).add(Node("d")))
    )

    assert supertree(
        Node()
        .add(Node().add(Node("a")), "data left")
        .add(Node().add(Node("b")), "data right"),
    ) == (Node().add(Node("a")).add(Node("b")))

    assert supertree(
        Node()
        .add(Node().add(Node("a")).add(Node("b")))
        .add(Node().add(Node("c")).add(Node("d"))),
        Node()
        .add(Node().add(Node("a")).add(Node("b")))
        .add(Node().add(Node("c")).add(Node("e"))),
    ) == (
        Node()
        .add(Node().add(Node("a")).add(Node("b")))
        .add(Node().add(Node("c")).add(Node("d")).add(Node("e")))
    )

    assert supertree(
        Node()
        .add(Node().add(Node("a")).add(Node("b")))
        .add(Node().add(Node("c")).add(Node("d"))),
        Node()
        .add(Node().add(Node("a")).add(Node("b")))
        .add(Node().add(Node("c")).add(Node("e"))),
        Node().add(Node("d")).add(Node().add(Node("c")).add(Node("e"))),
    ) == (
        Node()
        .add(Node().add(Node("a")).add(Node("b")))
        .add(Node().add(Node().add(Node("c")).add(Node("e"))).add(Node("d")))
    )
