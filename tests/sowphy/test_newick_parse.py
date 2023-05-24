from sowing.node import Node
from sowphy import newick
from sowphy.clade import Clade
import pytest


def test_topology():
    empty = Node(Clade())
    assert newick.parse(";") == empty
    assert newick.parse("(,);") == empty.add(empty).add(empty)
    assert newick.parse("((),(,,),);") == (
        empty
        .add(empty.add(empty))
        .add(empty.add(empty).add(empty).add(empty))
        .add(empty)
    )


def test_name():
    assert newick.parse("label;") == Node(Clade("label"))
    assert newick.parse("a_b_c;") == Node(Clade("a b c"))
    assert newick.parse("'a b c';") == Node(Clade("a b c"))
    assert newick.parse("'quote''quote';") == Node(Clade("quote'quote"))
    assert newick.parse("(left,right)root;") == (
        Node(Clade("root"))
        .add(Node(Clade("left"))).add(Node(Clade("right")))
    )


def test_length():
    assert newick.parse(":42;") == Node(Clade("", 42))
    assert newick.parse("(left:42,right:24)root;") == (
        Node(Clade("root"))
        .add(Node(Clade("left", 42))).add(Node(Clade("right", 24)))
    )
    assert newick.parse("(left:1.23,right:3.21)root;") == (
        Node(Clade("root"))
        .add(Node(Clade("left", 1.23))).add(Node(Clade("right", 3.21)))
    )


def test_comments():
    assert newick.parse("(left[comment1],right[comment2])root[comment3];") == \
        Node(Clade("root")).add(Node(Clade("left"))).add(Node(Clade("right")))
    assert newick.parse("root[abc[nested[third]]];") == Node(Clade("root"))


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
        Node(Clade(""))
        .add(Node(Clade("B", 6)))
        .add(Node(Clade("", 5))
             .add(Node(Clade("A", 5)))
             .add(Node(Clade("C", 3)))
             .add(Node(Clade("E", 4)))
        )
        .add(Node(Clade("D", 11)))
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
    )
