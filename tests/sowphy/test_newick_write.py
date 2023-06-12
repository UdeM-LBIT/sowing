from sowing.node import Node
from sowphy import newick
from sowphy.clade import Clade, Branch, Map


def test_topology():
    empty = Node(Clade())
    assert newick.write(empty) == ";"
    assert newick.write(empty.add(empty).add(empty)) == "(,);"
    assert (
        newick.write(
            empty.add(empty.add(empty))
            .add(empty.add(empty).add(empty).add(empty))
            .add(empty)
        )
        == "((),(,,),);"
    )


def test_name():
    assert newick.write(Node(Clade("label"))) == "label;"
    assert newick.write(Node(Clade("a b c"))) == "a_b_c;"
    assert newick.write(Node(Clade("a\tb\tc"))) == "'a\tb\tc';"
    assert newick.write(Node(Clade("quote'quote"))) == "'quote''quote';"
    assert (
        newick.write(
            Node(Clade("root"))
            .add(Node(Clade("left")), data=Branch())
            .add(Node(Clade("right")), data=Branch())
        )
        == "(left,right)root;"
    )


def test_length():
    assert newick.write(Node(Clade(""))) == ";"
    assert (
        newick.write(
            Node(Clade("root"))
            .add(Node(Clade("left")), data=Branch(42))
            .add(Node(Clade("right")), data=Branch(24))
        )
        == "(left:42,right:24)root;"
    )
    assert (
        newick.write(
            Node(Clade("root"))
            .add(Node(Clade("left")), data=Branch(1.23))
            .add(Node(Clade("right")), data=Branch(3.21))
        )
        == "(left:1.23,right:3.21)root;"
    )


def test_props_clade():
    assert newick.write(Node(Clade("test", Map({})))) == "test;"
    assert (
        newick.write(
            Node(
                Clade(
                    "test",
                    Map(
                        {
                            "key": "value",
                            "bool": True,
                            "number": 42,
                        }
                    ),
                )
            )
        )
        == "test[&bool=True,key=value,number=42];"
    )
    assert (
        newick.write(
            Node(
                Clade(
                    "test",
                    Map(
                        {
                            "key": "va=lue",
                            "bo,ol": True,
                            "number": 42,
                        }
                    ),
                )
            )
        )
        == "test[&'bo,ol'=True,key='va=lue',number=42];"
    )


def test_props_branch():
    assert (
        newick.write(
            Node().add(
                Node(
                    Clade(
                        "test",
                        Map(
                            {
                                "key": "value",
                                "bool": True,
                                "number": 42,
                            }
                        ),
                    )
                ),
                data=Branch(12),
            )
        )
        == "(test[&bool=True,key=value,number=42]:12);"
    )
    assert (
        newick.write(
            Node().add(
                Node(Clade("test")),
                data=Branch(
                    12,
                    Map(
                        {
                            "key": "value",
                            "bool": True,
                            "number": 42,
                        }
                    ),
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
            Node(Clade(""))
            .add(Node(Clade("B")), data=Branch(6))
            .add(
                Node(Clade(""))
                .add(Node(Clade("A")), data=Branch(5))
                .add(Node(Clade("C")), data=Branch(3))
                .add(Node(Clade("E")), data=Branch(4)),
                data=Branch(5),
            )
            .add(Node(Clade("D")), data=Branch(11))
        )
        == "(B:6,(A:5,C:3,E:4):5,D:11);"
    )

    assert newick.write(
        Node(Clade(""))
        .add(
            Node(Clade(""))
            .add(Node(Clade("raccoon")), data=Branch(19.19959))
            .add(Node(Clade("bear")), data=Branch(6.80041)),
            data=Branch(0.84600),
        )
        .add(
            Node(Clade(""))
            .add(
                Node(Clade(""))
                .add(Node(Clade("sea lion")), data=Branch(11.99700))
                .add(Node(Clade("seal")), data=Branch(12.00300)),
                data=Branch(7.52973),
            )
            .add(
                Node(Clade(""))
                .add(
                    Node(Clade(""))
                    .add(Node(Clade("monkey")), data=Branch(100.85930))
                    .add(Node(Clade("cat")), data=Branch(47.14069)),
                    data=Branch(20.59201),
                )
                .add(Node(Clade("weasel")), data=Branch(18.87953)),
                data=Branch(2.09460),
            ),
            data=Branch(3.87382),
        )
        .add(Node(Clade("dog")), data=Branch(25.46154))
    ) == (
        "((raccoon:19.19959,bear:6.80041):0.846,((sea_lion:11.997,seal:12.003)"
        ":7.52973,((monkey:100.8593,cat:47.14069):20.59201,weasel:18.87953)"
        ":2.0946):3.87382,dog:25.46154);"
    )
