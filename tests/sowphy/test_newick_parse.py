from sowing.node import Node
from sowphy import newick
from sowphy.clade import Clade, Branch
from immutables import Map
import pytest


def test_topology():
    empty = Node(Clade())
    empty_branch = (empty, Branch())
    assert newick.parse(";") == empty
    assert newick.parse("(,);") == empty.add(*empty_branch).add(*empty_branch)
    assert newick.parse("((),(,,),);") == (
        empty.add(empty.add(*empty_branch), Branch())
        .add(empty.add(*empty_branch).add(*empty_branch).add(*empty_branch), Branch())
        .add(*empty_branch)
    )


def test_name():
    assert newick.parse("label;") == Node(Clade("label"))
    assert newick.parse("a_b_c;") == Node(Clade("a b c"))
    assert newick.parse("'a b c';") == Node(Clade("a b c"))
    assert newick.parse("'quote''quote';") == Node(Clade("quote'quote"))
    assert newick.parse("(left,right)root;") == (
        Node(Clade("root"))
        .add(Node(Clade("left")), Branch())
        .add(Node(Clade("right")), Branch())
    )


def test_length():
    assert newick.parse(":42;") == Node(Clade(""))
    assert newick.parse("(left:42,right:24)root;") == (
        Node(Clade("root"))
        .add(Node(Clade("left")), Branch(42))
        .add(Node(Clade("right")), Branch(24))
    )
    assert newick.parse("(left:1.23,right:3.21)root;") == (
        Node(Clade("root"))
        .add(Node(Clade("left")), Branch(1.23))
        .add(Node(Clade("right")), Branch(3.21))
    )


def test_comments():
    assert newick.parse("(left[comment1],right[comment2])root[comment3];") == (
        Node(Clade("root"))
        .add(Node(Clade("left")), Branch())
        .add(Node(Clade("right")), Branch())
    )
    assert newick.parse("root[abc[nested[third]]];") == Node(Clade("root"))


def test_props_nhx():
    assert newick.parse("a[&&NHX];") == (Node(Clade("a", Map({}))))
    assert newick.parse("a[&&NHX:S=human:E=1.1.1.1];") == (
        Node(Clade("a", Map({"S": "human", "E": "1.1.1.1"})))
    )
    assert newick.parse("a[&&NHX:S={}:E=()];") == (
        Node(Clade("a", Map({"S": "{}", "E": "()"})))
    )
    assert newick.parse("a[&&NHX:S=[abc]:E=];") == (
        Node(Clade("a", Map({"S": "", "E": ""})))
    )
    assert newick.parse("(a[&&NHX:S=:E=]:12);") == (
        Node(Clade()).add(
            node=Node(Clade("a", Map({"S": "", "E": ""}))),
            data=Branch(12),
        )
    )
    assert newick.parse("(a:12[&&NHX:S=:E=]);") == (
        Node(Clade()).add(
            node=Node(Clade("a")),
            data=Branch(12, Map({"S": "", "E": ""})),
        )
    )
    assert newick.parse("(a:[&&NHX:S=:E=]);") == (
        Node(Clade()).add(
            node=Node(Clade("a")),
            data=Branch(props=Map({"S": "", "E": ""})),
        )
    )
    assert newick.parse("a[&&NHX:'quote'':=arg'='quote=:''value'];") == (
        Node(Clade("a", Map({"quote':=arg": "quote=:'value"})))
    )


def test_props_beast():
    assert newick.parse("a[&];") == (Node(Clade("a", Map({}))))
    assert newick.parse("a[&height=100.0,colour={red}];") == (
        Node(Clade("a", Map({"height": "100.0", "colour": "{red}"})))
    )
    assert newick.parse("a[&height=100.0,colour={red},];") == (
        Node(Clade("a", Map({"height": "100.0", "colour": "{red}"})))
    )
    assert newick.parse("a[&height=[],colour=];") == (
        Node(Clade("a", Map({"height": "", "colour": ""})))
    )
    assert newick.parse("a[&height=[],colour=,];") == (
        Node(Clade("a", Map({"height": "", "colour": ""})))
    )
    assert newick.parse("a[&height={},colour=(),test=[]];") == (
        Node(Clade("a", Map({"height": "{}", "colour": "()", "test": ""})))
    )
    assert newick.parse("(a[&s=,e=]:12);") == (
        Node(Clade()).add(
            node=Node(Clade("a", Map({"s": "", "e": ""}))),
            data=Branch(12),
        )
    )
    assert newick.parse("(a:12[&s=,e=]);") == (
        Node(Clade()).add(
            node=Node(Clade("a")),
            data=Branch(12, Map({"s": "", "e": ""})),
        )
    )
    assert newick.parse("(a:[&s=,e=]);") == (
        Node(Clade()).add(
            node=Node(Clade("a")),
            data=Branch(props=Map({"s": "", "e": ""})),
        )
    )
    assert newick.parse("a[&'quote'':=arg'='quote=:''value',];") == (
        Node(Clade("a", Map({"quote':=arg": "quote=:'value"})))
    )


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

    with pytest.raises(newick.ParseError) as error:
        newick.parse("()][];")

    assert "unexpected ']'" in str(error.value)
    assert error.value.start == 2
    assert error.value.end == 3


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
        newick.parse(":abcd;")

    assert "invalid branch length value 'abcd'" in str(error.value)
    assert error.value.start == 1
    assert error.value.end == 5

    with pytest.raises(newick.ParseError) as error:
        newick.parse("(abcd());")

    assert "unexpected token '(' after node" in str(error.value)
    assert error.value.start == 5
    assert error.value.end == 6

    with pytest.raises(newick.ParseError) as error:
        newick.parse("(node[&&NHX:=value]")

    assert "expected 'string', not '='" in str(error.value)
    assert error.value.start == 12
    assert error.value.end == 13

    with pytest.raises(newick.ParseError) as error:
        newick.parse("(node[&test,=]")

    assert "expected '=', not ','" in str(error.value)
    assert error.value.start == 11
    assert error.value.end == 12

    with pytest.raises(newick.ParseError) as error:
        newick.parse("(node[&test=,=]")

    assert "expected ']', not '='" in str(error.value)
    assert error.value.start == 13
    assert error.value.end == 14


def test_phylip():
    # Newick example trees, taken from Phylip
    # <https://evolution.genetics.washington.edu/phylip/newicktree.html>

    assert newick.parse("(B:6.0,(A:5.0,C:3.0,E:4.0):5.0,D:11.0);") == (
        Node(Clade(""))
        .add(Node(Clade("B")), Branch(6))
        .add(
            data=Branch(5),
            node=Node(Clade(""))
            .add(Node(Clade("A")), Branch(5))
            .add(Node(Clade("C")), Branch(3))
            .add(Node(Clade("E")), Branch(4)),
        )
        .add(Node(Clade("D")), Branch(11))
    )

    assert (
        newick.parse(
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
        )
        == (
            Node(Clade(""))
            .add(
                data=Branch(0.84600),
                node=Node(Clade(""))
                .add(Node(Clade("raccoon")), Branch(19.19959))
                .add(Node(Clade("bear")), Branch(6.80041)),
            )
            .add(
                data=Branch(3.87382),
                node=Node(Clade(""))
                .add(
                    data=Branch(7.52973),
                    node=Node(Clade(""))
                    .add(Node(Clade("sea lion")), Branch(11.99700))
                    .add(Node(Clade("seal")), Branch(12.00300)),
                )
                .add(
                    data=Branch(2.09460),
                    node=Node(Clade(""))
                    .add(
                        data=Branch(20.59201),
                        node=Node(Clade(""))
                        .add(Node(Clade("monkey")), Branch(100.85930))
                        .add(Node(Clade("cat")), Branch(47.14069)),
                    )
                    .add(Node(Clade("weasel")), Branch(18.87953)),
                ),
            )
            .add(Node(Clade("dog")), Branch(25.46154))
        )
    )
