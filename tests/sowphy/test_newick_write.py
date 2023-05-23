from sowing.node import Node
from sowphy import newick


def test_topology():
    assert newick.write(Node("")) == ";"
    assert newick.write(Node("").add(Node("")).add(Node(""))) == "(,);"
    assert newick.write(
        Node("")
        .add(Node("").add(Node("")))
        .add(Node("").add(Node("")).add(Node("")).add(Node("")))
        .add(Node(""))
    ) == "((),(,,),);"


def test_name():
    assert newick.write(Node("label")) == "label;"
    assert newick.write(Node("a b c")) == "a_b_c;"
    assert newick.write(Node("a\tb\tc")) == "'a\tb\tc';"
    assert newick.write(Node("quote'quote")) == "'quote''quote';"
    assert newick.write(
        Node("root")
        .add(Node("left")).add(Node("right"))
    ) == "(left,right)root;"


def test_length():
    assert newick.write(
        Node("root")
        .add(Node("left"), 42).add(Node("right"), 24)
    ) == "(left:42,right:24)root;"
    assert newick.write(
        Node("root")
        .add(Node("left"), 1.23).add(Node("right"), 3.21)
    ) == "(left:1.23,right:3.21)root;"


def test_phylip():
    # Newick example trees, taken from Phylip
    # <https://evolution.genetics.washington.edu/phylip/newicktree.html>

    assert newick.write(
        Node("")
        .add(Node("B"), 6)
        .add(Node("").add(Node("A"), 5).add(Node("C"), 3).add(Node("E"), 4), 5)
        .add(Node("D"), 11)
    ) == "(B:6,(A:5,C:3,E:4):5,D:11);"

    assert newick.write(
        Node("")
        .add(Node("")
            .add(Node("raccoon"), 19.19959)
            .add(Node("bear"), 6.80041),
            0.84600
        )
        .add(Node("")
             .add(Node("")
                  .add(Node("sea lion"), 11.99700)
                  .add(Node("seal"), 12.00300),
                  7.52973
             )
             .add(Node("")
                  .add(Node("")
                       .add(Node("monkey"), 100.85930)
                       .add(Node("cat"), 47.14069),
                       20.59201
                  )
                  .add(Node("weasel"), 18.87953),
                  2.09460
             ),
             3.87382
        )
        .add(Node("dog"), 25.46154)
    ) == (
        "((raccoon:19.19959,bear:6.80041):0.846,((sea_lion:11.997,seal:12.003)"
        ":7.52973,((monkey:100.8593,cat:47.14069):20.59201,weasel:18.87953)"
        ":2.0946):3.87382,dog:25.46154);"
    )
