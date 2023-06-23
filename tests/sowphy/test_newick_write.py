from sowing.node import Node
from sowphy import newick
from immutables import Map


def test_topology():
    assert newick.write(Node()) == ";"
    assert newick.write(Node().add(Node()).add(Node())) == "(,);"
    assert (
        newick.write(
            Node()
            .add(Node().add(Node()))
            .add(Node().add(Node()).add(Node()).add(Node()))
            .add(Node())
        )
        == "((),(,,),);"
    )


def test_name():
    assert newick.write(Node(Map({"name": "label"}))) == "label;"
    assert newick.write(Node(Map({"name": "a b c"}))) == "a_b_c;"
    assert newick.write(Node(Map({"name": "a\tb\tc"}))) == "'a\tb\tc';"
    assert newick.write(Node(Map({"name": "quote'quote"}))) == "'quote''quote';"
    assert (
        newick.write(
            Node(Map({"name": "root"}))
            .add(Node(Map({"name": "left"})))
            .add(Node(Map({"name": "right"})))
        )
        == "(left,right)root;"
    )


def test_length():
    assert newick.write(Node(Map({"name": ""}))) == ";"
    assert (
        newick.write(
            Node(Map({"name": "root"}))
            .add(Node(Map({"name": "left"})), data=Map({"length": 42}))
            .add(Node(Map({"name": "right"})), data=Map({"length": 24}))
        )
        == "(left:42,right:24)root;"
    )
    assert (
        newick.write(
            Node(Map({"name": "root"}))
            .add(Node(Map({"name": "left"})), data=Map({"length": 1.23}))
            .add(Node(Map({"name": "right"})), data=Map({"length": 3.21}))
        )
        == "(left:1.23,right:3.21)root;"
    )


def test_props_clade():
    assert newick.write(Node(Map({"name": "test"}))) == "test;"
    assert (
        newick.write(
            Node(
                Map(
                    {
                        "name": "test",
                        "key": "value",
                        "bool": True,
                        "number": 42,
                    }
                )
            )
        )
        == "test[&bool=True,key=value,number=42];"
    )
    assert (
        newick.write(
            Node(
                Map(
                    {
                        "name": "test",
                        "key": "va=lue",
                        "bo,ol": True,
                        "number": 42,
                    }
                ),
            )
        )
        == "test[&'bo,ol'=True,key='va=lue',number=42];"
    )


def test_props_branch():
    assert (
        newick.write(
            Node().add(
                Node(
                    Map(
                        {
                            "name": "test",
                            "key": "value",
                            "bool": True,
                            "number": 42,
                        }
                    ),
                ),
                data=Map({"length": 12}),
            )
        )
        == "(test[&bool=True,key=value,number=42]:12);"
    )
    assert (
        newick.write(
            Node().add(
                Node(Map({"name": "test"})),
                data=Map(
                    {
                        "length": 12,
                        "key": "value",
                        "bool": True,
                        "number": 42,
                    }
                ),
            )
        )
        == "(test:12[&bool=True,key=value,number=42]);"
    )


def test_phylip():
    # Newick example trees, taken from Phylip
    # <https://evolution.genetics.washington.edu/phylip/newicktree.html>

    assert (
        newick.write(
            Node(Map({"name": ""}))
            .add(Node(Map({"name": "B"})), data=Map({"length": 6}))
            .add(
                Node(Map({"name": ""}))
                .add(Node(Map({"name": "A"})), data=Map({"length": 5}))
                .add(Node(Map({"name": "C"})), data=Map({"length": 3}))
                .add(Node(Map({"name": "E"})), data=Map({"length": 4})),
                data=Map({"length": 5}),
            )
            .add(Node(Map({"name": "D"})), data=Map({"length": 11}))
        )
        == "(B:6,(A:5,C:3,E:4):5,D:11);"
    )

    assert newick.write(
        Node(Map({"name": ""}))
        .add(
            Node(Map({"name": ""}))
            .add(Node(Map({"name": "raccoon"})), data=Map({"length": 19.19959}))
            .add(Node(Map({"name": "bear"})), data=Map({"length": 6.80041})),
            data=Map({"length": 0.84600}),
        )
        .add(
            Node(Map({"name": ""}))
            .add(
                Node(Map({"name": ""}))
                .add(Node(Map({"name": "sea lion"})), data=Map({"length": 11.99700}))
                .add(Node(Map({"name": "seal"})), data=Map({"length": 12.00300})),
                data=Map({"length": 7.52973}),
            )
            .add(
                Node(Map({"name": ""}))
                .add(
                    Node(Map({"name": ""}))
                    .add(Node(Map({"name": "monkey"})), data=Map({"length": 100.85930}))
                    .add(Node(Map({"name": "cat"})), data=Map({"length": 47.14069})),
                    data=Map({"length": 20.59201}),
                )
                .add(Node(Map({"name": "weasel"})), data=Map({"length": 18.87953})),
                data=Map({"length": 2.09460}),
            ),
            data=Map({"length": 3.87382}),
        )
        .add(Node(Map({"name": "dog"})), data=Map({"length": 25.46154}))
    ) == (
        "((raccoon:19.19959,bear:6.80041):0.846,((sea_lion:11.997,seal:12.003)"
        ":7.52973,((monkey:100.8593,cat:47.14069):20.59201,weasel:18.87953)"
        ":2.0946):3.87382,dog:25.46154);"
    )
