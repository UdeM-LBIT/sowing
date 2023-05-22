from sowing.net import Net
from sowing import newick


def test_topology():
    assert newick.write(Net("")) == ";"
    assert newick.write(Net("").add(Net("")).add(Net(""))) == "(,);"
    assert newick.write(
        Net("")
        .add(Net("").add(Net("")))
        .add(Net("").add(Net("")).add(Net("")).add(Net("")))
        .add(Net(""))
    ) == "((),(,,),);"


def test_name():
    assert newick.write(Net("label")) == "label;"
    assert newick.write(Net("a b c")) == "a_b_c;"
    assert newick.write(Net("a\tb\tc")) == "'a\tb\tc';"
    assert newick.write(Net("quote'quote")) == "'quote''quote';"
    assert newick.write(
        Net("root")
        .add(Net("left")).add(Net("right"))
    ) == "(left,right)root;"


def test_length():
    assert newick.write(
        Net("root")
        .add(Net("left"), 42).add(Net("right"), 24)
    ) == "(left:42,right:24)root;"
    assert newick.write(
        Net("root")
        .add(Net("left"), 1.23).add(Net("right"), 3.21)
    ) == "(left:1.23,right:3.21)root;"


def test_phylip():
    # Newick example trees, taken from Phylip
    # <https://evolution.genetics.washington.edu/phylip/newicktree.html>

    assert newick.write(
        Net("")
        .add(Net("B"), 6)
        .add(Net("").add(Net("A"), 5).add(Net("C"), 3).add(Net("E"), 4), 5)
        .add(Net("D"), 11)
    ) == "(B:6,(A:5,C:3,E:4):5,D:11);"

    assert newick.write(
        Net("")
        .add(Net("")
            .add(Net("raccoon"), 19.19959)
            .add(Net("bear"), 6.80041),
            0.84600
        )
        .add(Net("")
             .add(Net("")
                  .add(Net("sea lion"), 11.99700)
                  .add(Net("seal"), 12.00300),
                  7.52973
             )
             .add(Net("")
                  .add(Net("")
                       .add(Net("monkey"), 100.85930)
                       .add(Net("cat"), 47.14069),
                       20.59201
                  )
                  .add(Net("weasel"), 18.87953),
                  2.09460
             ),
             3.87382
        )
        .add(Net("dog"), 25.46154)
    ) == (
        "((raccoon:19.19959,bear:6.80041):0.846,((sea_lion:11.997,seal:12.003)"
        ":7.52973,((monkey:100.8593,cat:47.14069):20.59201,weasel:18.87953)"
        ":2.0946):3.87382,dog:25.46154);"
    )
