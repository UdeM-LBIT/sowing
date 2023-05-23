from sowing.node import Node
from sowphy import newick
import pytest


def test_topology():
    assert newick.parse(";") == Node("")
    assert newick.parse("(,);") == Node("").add(Node("")).add(Node(""))
    assert newick.parse("((),(,,),);") == (
        Node("")
        .add(Node("").add(Node("")))
        .add(Node("").add(Node("")).add(Node("")).add(Node("")))
        .add(Node(""))
    )


def test_name():
    assert newick.parse("label;") == Node("label")
    assert newick.parse("a_b_c;") == Node("a b c")
    assert newick.parse("'a b c';") == Node("a b c")
    assert newick.parse("'quote''quote';") == Node("quote'quote")
    assert newick.parse("(left,right)root;") == (
        Node("root")
        .add(Node("left")).add(Node("right"))
    )


def test_length():
    assert newick.parse(":42;") == Node("")
    assert newick.parse("(left:42,right:24)root;") == (
        Node("root")
        .add(Node("left"), 42).add(Node("right"), 24)
    )
    assert newick.parse("(left:1.23,right:3.21)root;") == (
        Node("root")
        .add(Node("left"), 1.23).add(Node("right"), 3.21)
    )


def test_comments():
    assert newick.parse("(left[comment1],right[comment2])root[comment3];") == \
        Node("root").add(Node("left")).add(Node("right"))
    assert newick.parse("root[abc[nested[third]]];") == Node("root")


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
        Node("")
        .add(Node("B"), 6)
        .add(Node("").add(Node("A"), 5).add(Node("C"), 3).add(Node("E"), 4), 5)
        .add(Node("D"), 11)
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
    )
