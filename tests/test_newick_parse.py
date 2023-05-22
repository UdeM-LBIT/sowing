from sowing.net import Net
from sowing import newick
import pytest


def test_topology():
    assert newick.parse(";") == Net("")
    assert newick.parse("(,);") == Net("").add(Net("")).add(Net(""))
    assert newick.parse("((),(,,),);") == (
        Net("")
        .add(Net("").add(Net("")))
        .add(Net("").add(Net("")).add(Net("")).add(Net("")))
        .add(Net(""))
    )


def test_name():
    assert newick.parse("label;") == Net("label")
    assert newick.parse("a_b_c;") == Net("a b c")
    assert newick.parse("'a b c';") == Net("a b c")
    assert newick.parse("'quote''quote';") == Net("quote'quote")
    assert newick.parse("(left,right)root;") == (
        Net("root")
        .add(Net("left")).add(Net("right"))
    )


def test_length():
    assert newick.parse(":42;") == Net("")
    assert newick.parse("(left:42,right:24)root;") == (
        Net("root")
        .add(Net("left"), 42).add(Net("right"), 24)
    )
    assert newick.parse("(left:1.23,right:3.21)root;") == (
        Net("root")
        .add(Net("left"), 1.23).add(Net("right"), 3.21)
    )


def test_comments():
    assert newick.parse("(left[comment1],right[comment2])root[comment3];") == \
        Net("root").add(Net("left")).add(Net("right"))
    assert newick.parse("root[abc[nested[third]]];") == Net("root")


def test_tokenize_error():
    with pytest.raises(newick.ParseError) as error:
        newick.parse("()'unclosed;")

    assert "unclosed string" in str(error.value)
    assert error.value.start == 2
    assert error.value.end == 12

    with pytest.raises(newick.ParseError) as error:
        newick.parse("()[[];")

    assert "unclosed comment" in str(error.value)
    assert error.value.start == 2
    assert error.value.end == 6


def test_grammar_error():
    with pytest.raises(newick.ParseError) as error:
        newick.parse("")

    assert "expected ';' after end of tree, not 'end'" in str(error.value)
    assert error.value.start == 0
    assert error.value.end == 0

    with pytest.raises(newick.ParseError) as error:
        newick.parse(")")

    assert "expected ';' after end of tree, not ')'" in str(error.value)
    assert error.value.start == 0
    assert error.value.end == 1

    with pytest.raises(newick.ParseError) as error:
        newick.parse(";abcdef")

    assert "unexpected garbage after end of tree" in str(error.value)
    assert error.value.start == 1
    assert error.value.end == 7

    with pytest.raises(newick.ParseError) as error:
        newick.parse(":;")

    assert "expected branch length value after ':', not ';'" in str(error.value)
    assert error.value.start == 1
    assert error.value.end == 2

    with pytest.raises(newick.ParseError) as error:
        newick.parse(":abcd;")

    assert "invalid branch length value" in str(error.value)
    assert error.value.start == 1
    assert error.value.end == 5

    with pytest.raises(newick.ParseError) as error:
        newick.parse("(abcd());")

    assert "unexpected token '(' after node" in str(error.value)
    assert error.value.start == 5
    assert error.value.end == 6


def test_phylip():
    # Newick example trees, taken from Phylip
    # <https://evolution.genetics.washington.edu/phylip/newicktree.html>

    assert newick.parse(
        "(B:6.0,(A:5.0,C:3.0,E:4.0):5.0,D:11.0);"
    ) == (
        Net("")
        .add(Net("B"), 6)
        .add(Net("").add(Net("A"), 5).add(Net("C"), 3).add(Net("E"), 4), 5)
        .add(Net("D"), 11)
    )

    assert newick.parse(
        """(
            (raccoon:19.19959,bear:6.80041):0.84600,
            (
                (sea_lion:11.99700, seal:12.00300):7.52973,
                (
                    (monkey:100.85930,cat:47.14069):20.59201,
                    weasel:18.87953
                ):2.09460
            ):3.87382,
            dog:25.46154
        );"""
    ) == (
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
    )
