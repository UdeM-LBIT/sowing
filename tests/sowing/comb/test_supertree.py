from sowing.node import Node
from sowing.comb.supertree import Triple, Fan, breakup, build, supertree, display


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
    assert list(build([Node("a")], [], [])) == [Node("a")]

    assert list(build([Node("a"), Node("b")], [], [])) == [
        (Node().add(Node("a")).add(Node("b")))
    ]

    assert list(build([Node("a"), Node("b"), Node("c")], [], [])) == [
        Node().add(Node("a")).add(Node("b")).add(Node("c")),
        Node().add(Node("a")).add(Node().add(Node("b")).add(Node("c"))),
        Node().add(Node().add(Node("a")).add(Node("b"))).add(Node("c")),
        Node().add(Node().add(Node("a")).add(Node("c"))).add(Node("b")),
    ]

    assert list(build([Node("a"), Node("b"), Node("c")], [], [], arity=2)) == [
        Node().add(Node("a")).add(Node().add(Node("b")).add(Node("c"))),
        Node().add(Node().add(Node("a")).add(Node("b"))).add(Node("c")),
        Node().add(Node().add(Node("a")).add(Node("c"))).add(Node("b")),
    ]

    assert list(
        build(
            [Node("a"), Node("b"), Node("c")],
            [
                Triple((Node("b"), Node("c")), Node("a")),
            ],
            [],
        )
    ) == [Node().add(Node("a")).add(Node().add(Node("b")).add(Node("c")))]

    assert (
        list(
            build(
                [Node("a"), Node("b"), Node("c")],
                [
                    Triple((Node("b"), Node("c")), Node("a")),
                    Triple((Node("b"), Node("a")), Node("c")),
                ],
                [],
            )
        )
        == []
    )

    assert list(
        build(
            [Node("a"), Node("b"), Node("c"), Node("d")],
            [
                Triple((Node("a"), Node("b")), Node("c")),
                Triple((Node("c"), Node("d")), Node("a")),
            ],
            [],
        )
    ) == [
        Node()
        .add(Node().add(Node("a")).add(Node("b")))
        .add(Node().add(Node("c")).add(Node("d")))
    ]

    assert (
        list(
            build(
                [Node("a"), Node("b"), Node("c"), Node("d")],
                [
                    Triple((Node("a"), Node("b")), Node("c")),
                    Triple((Node("c"), Node("d")), Node("a")),
                ],
                [Fan((Node("a"), Node("b"), Node("c")))],
            )
        )
        == []
    )

    assert list(
        build(
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
    ) == [
        Node()
        .add(Node().add(Node("b")).add(Node("c")).add(Node("d")))
        .add(Node().add(Node("e")).add(Node("f")))
        .add(Node("z")),
    ]


def test_supertree():
    assert list(
        supertree(
            Node()
            .add(Node().add(Node("a")).add(Node("b")))
            .add(Node().add(Node("c")).add(Node("d"))),
        )
    ) == [
        Node()
        .add(Node().add(Node("a")).add(Node("b")))
        .add(Node().add(Node("c")).add(Node("d")))
    ]

    assert list(
        supertree(
            Node()
            .add(Node().add(Node("a")), data="data left")
            .add(Node().add(Node("b")), data="data right"),
        )
    ) == [Node().add(Node("a")).add(Node("b"))]

    assert list(
        supertree(
            Node()
            .add(Node().add(Node("a")).add(Node("b")))
            .add(Node().add(Node("c")).add(Node("d"))),
            Node()
            .add(Node().add(Node("a")).add(Node("b")))
            .add(Node().add(Node("c")).add(Node("e"))),
        )
    ) == [
        Node()
        .add(Node().add(Node("a")).add(Node("b")))
        .add(Node().add(Node("c")).add(Node("d")).add(Node("e"))),
        Node()
        .add(Node().add(Node("a")).add(Node("b")))
        .add(Node().add(Node("c")).add(Node().add(Node("d")).add(Node("e")))),
        Node()
        .add(Node().add(Node("a")).add(Node("b")))
        .add(Node().add(Node().add(Node("c")).add(Node("d"))).add(Node("e"))),
        Node()
        .add(Node().add(Node("a")).add(Node("b")))
        .add(Node().add(Node().add(Node("c")).add(Node("e"))).add(Node("d"))),
    ]

    assert list(
        supertree(
            Node()
            .add(Node().add(Node("a")).add(Node("b")))
            .add(Node().add(Node("c")).add(Node("d"))),
            Node()
            .add(Node().add(Node("a")).add(Node("b")))
            .add(Node().add(Node("c")).add(Node("e"))),
            Node().add(Node().add(Node("c")).add(Node("e"))).add(Node("d")),
        )
    ) == [
        Node()
        .add(Node().add(Node("a")).add(Node("b")))
        .add(Node().add(Node().add(Node("c")).add(Node("e"))).add(Node("d")))
    ]

    assert list(
        supertree(
            Node().add(Node("a")).add(Node("b")),
            Node().add(Node("a")).add(Node().add(Node("c")).add(Node("d"))),
        )
    ) == [
        Node().add(Node("a")).add(Node("b")).add(Node().add(Node("c")).add(Node("d"))),
        Node().add(Node("a")).add(Node().add(Node("b")).add(Node("c")).add(Node("d"))),
        Node()
        .add(Node("a"))
        .add(Node().add(Node("b")).add(Node().add(Node("c")).add(Node("d")))),
        Node()
        .add(Node("a"))
        .add(Node().add(Node().add(Node("b")).add(Node("c"))).add(Node("d"))),
        Node()
        .add(Node("a"))
        .add(Node().add(Node().add(Node("b")).add(Node("d"))).add(Node("c"))),
        Node()
        .add(Node().add(Node("a")).add(Node("b")))
        .add(Node().add(Node("c")).add(Node("d"))),
        Node()
        .add(Node("b"))
        .add(Node().add(Node("a")).add(Node().add(Node("c")).add(Node("d")))),
    ]

    assert list(
        supertree(
            Node().add(Node("a")).add(Node("b")),
            Node().add(Node("a")).add(Node().add(Node("c")).add(Node("d"))),
            arity=2,
        )
    ) == [
        Node()
        .add(Node("a"))
        .add(Node().add(Node("b")).add(Node().add(Node("c")).add(Node("d")))),
        Node()
        .add(Node("a"))
        .add(Node().add(Node().add(Node("b")).add(Node("c"))).add(Node("d"))),
        Node()
        .add(Node("a"))
        .add(Node().add(Node().add(Node("b")).add(Node("d"))).add(Node("c"))),
        Node()
        .add(Node().add(Node("a")).add(Node("b")))
        .add(Node().add(Node("c")).add(Node("d"))),
        Node()
        .add(Node("b"))
        .add(Node().add(Node("a")).add(Node().add(Node("c")).add(Node("d")))),
    ]


def test_display():
    assert display(
        Node()
        .add(Node().add(Node("a")).add(Node("b")))
        .add(Node().add(Node("c")).add(Node("d")).add(Node("e"))),
        {Node("a"), Node("b"), Node("c"), Node("d")},
    ) == (
        Node()
        .add(Node().add(Node("a")).add(Node("b")))
        .add(Node().add(Node("c")).add(Node("d")))
    )

    assert display(
        Node()
        .add(Node().add(Node("a")).add(Node("b")))
        .add(Node().add(Node("c")).add(Node("d")).add(Node("e"))),
        {Node("a"), Node("b"), Node("c"), Node("e")},
    ) == (
        Node()
        .add(Node().add(Node("a")).add(Node("b")))
        .add(Node().add(Node("c")).add(Node("e")))
    )

    assert display(
        Node()
        .add(Node().add(Node("a")).add(Node("b")))
        .add(Node().add(Node().add(Node("c")).add(Node("e"))).add(Node("d"))),
        {Node("a"), Node("b"), Node("c"), Node("d")},
    ) == (
        Node()
        .add(Node().add(Node("a")).add(Node("b")))
        .add(Node().add(Node("c")).add(Node("d")))
    )

    assert display(
        Node()
        .add(Node().add(Node("a")).add(Node("b")))
        .add(Node().add(Node().add(Node("c")).add(Node("e"))).add(Node("d"))),
        {Node("a"), Node("b"), Node("c"), Node("e")},
    ) == (
        Node()
        .add(Node().add(Node("a")).add(Node("b")))
        .add(Node().add(Node("c")).add(Node("e")))
    )

    assert display(
        Node()
        .add(Node().add(Node("a")).add(Node("b")))
        .add(Node().add(Node().add(Node("c")).add(Node("e"))).add(Node("d"))),
        {Node("d"), Node("c"), Node("e")},
    ) == Node().add(Node().add(Node("c")).add(Node("e"))).add(Node("d"))
