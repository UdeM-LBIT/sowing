from sowing.node import Node
from sowphy import newick
from sowphy.clade import Clade


def test_topology():
    empty = Node(Clade())
    assert newick.write(empty) == ";"
    assert newick.write(empty.add(empty).add(empty)) == "(,);"
    assert newick.write(
        empty
        .add(empty.add(empty))
        .add(empty.add(empty).add(empty).add(empty))
        .add(empty)
    ) == "((),(,,),);"


def test_name():
    assert newick.write(Node(Clade("label"))) == "label;"
    assert newick.write(Node(Clade("a b c"))) == "a_b_c;"
    assert newick.write(Node(Clade("a\tb\tc"))) == "'a\tb\tc';"
    assert newick.write(Node(Clade("quote'quote"))) == "'quote''quote';"
    assert newick.write(
        Node(Clade("root"))
        .add(Node(Clade("left"))).add(Node(Clade("right")))
    ) == "(left,right)root;"


def test_length():
    assert newick.write(Node(Clade("", 42))) == ":42;"
    assert newick.write(
        Node(Clade("root"))
        .add(Node(Clade("left", 42))).add(Node(Clade("right", 24)))
    ) == "(left:42,right:24)root;"
    assert newick.write(
        Node(Clade("root"))
        .add(Node(Clade("left", 1.23))).add(Node(Clade("right", 3.21)))
    ) == "(left:1.23,right:3.21)root;"


def test_phylip():
    # Newick example trees, taken from Phylip
    # <https://evolution.genetics.washington.edu/phylip/newicktree.html>

    assert newick.write(
        Node(Clade(""))
        .add(Node(Clade("B", 6)))
        .add(Node(Clade("", 5))
             .add(Node(Clade("A", 5)))
             .add(Node(Clade("C", 3)))
             .add(Node(Clade("E", 4)))
        )
        .add(Node(Clade("D", 11)))
    ) == "(B:6,(A:5,C:3,E:4):5,D:11);"

    assert newick.write(
        Node(Clade(""))
        .add(Node(Clade("", 0.84600))
            .add(Node(Clade("raccoon", 19.19959)))
            .add(Node(Clade("bear", 6.80041))),
        )
        .add(Node(Clade("", 3.87382))
             .add(Node(Clade("", 7.52973))
                  .add(Node(Clade("sea lion", 11.99700)))
                  .add(Node(Clade("seal", 12.00300)))
             )
             .add(Node(Clade("", 2.09460))
                  .add(Node(Clade("", 20.59201))
                       .add(Node(Clade("monkey", 100.85930)))
                       .add(Node(Clade("cat", 47.14069)))
                  )
                  .add(Node(Clade("weasel", 18.87953))),
             ),
        )
        .add(Node(Clade("dog", 25.46154)))
    ) == (
        "((raccoon:19.19959,bear:6.80041):0.846,((sea_lion:11.997,seal:12.003)"
        ":7.52973,((monkey:100.8593,cat:47.14069):20.59201,weasel:18.87953)"
        ":2.0946):3.87382,dog:25.46154);"
    )
