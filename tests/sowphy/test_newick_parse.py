from sowing.node import Node, Edge
from sowphy import newick
from immutables import Map
import pytest


def test_topology():
    assert newick.parse(";") == Node()
    assert newick.parse("(,);") == Node().add(Edge(Node())).add(Edge(Node()))
    assert newick.parse("((),(,,),);") == (
        Node()
        .add(Node().add(Edge(Node())))
        .add(Node().add(Edge(Node())).add(Edge(Node())).add(Edge(Node())))
        .add(Edge(Node()))
    )


def test_name():
    assert newick.parse("label;") == Node(Map({"name": "label"}))
    assert newick.parse("a_b_c;") == Node(Map({"name": "a b c"}))
    assert newick.parse("'a b c';") == Node(Map({"name": "a b c"}))
    assert newick.parse("'quote''quote';") == Node(Map({"name": "quote'quote"}))
    assert newick.parse("(left,right)root;") == (
        Node(Map({"name": "root"}))
        .add(Node(Map({"name": "left"})))
        .add(Node(Map({"name": "right"})))
    )


def test_length():
    assert newick.parse(":42;") == Node()
    assert newick.parse("(left:42,right:24)root;") == (
        Node(Map({"name": "root"}))
        .add(Node(Map({"name": "left"})), data=Map({"length": "42"}))
        .add(Node(Map({"name": "right"})), data=Map({"length": "24"}))
    )
    assert newick.parse("(left:1.23,right:3.21)root;") == (
        Node(Map({"name": "root"}))
        .add(Node(Map({"name": "left"})), data=Map({"length": "1.23"}))
        .add(Node(Map({"name": "right"})), data=Map({"length": "3.21"}))
    )


def test_comments():
    assert newick.parse("(left[comment1],right[comment2])root[comment3];") == (
        Node(Map({"name": "root"}))
        .add(Node(Map({"name": "left"})))
        .add(Node(Map({"name": "right"})))
    )
    assert newick.parse("root[abc[nested[third]]];") == Node(Map({"name": "root"}))


def test_props_nhx():
    assert newick.parse("a[&&NHX];") == (Node(Map({"name": "a"})))
    assert newick.parse("a[&&NHX:S=human:E=1.1.1.1];") == (
        Node(Map({"name": "a", "S": "human", "E": "1.1.1.1"}))
    )
    assert newick.parse("a[&&NHX:S={}:E=()];") == (
        Node(Map({"name": "a", "S": "{}", "E": "()"}))
    )
    assert newick.parse("a[&&NHX:S=[abc]:E=];") == (
        Node(Map({"name": "a", "S": "", "E": ""}))
    )
    assert newick.parse("(a[&&NHX:S=:E=]:12);") == (
        Node().add(
            Node(Map({"name": "a", "S": "", "E": ""})),
            data=Map({"length": "12"}),
        )
    )
    assert newick.parse("(a:12[&&NHX:S=:E=]);") == (
        Node().add(
            Node(Map({"name": "a"})),
            data=Map({"length": "12", "S": "", "E": ""}),
        )
    )
    assert newick.parse("(a:[&&NHX:S=:E=]);") == (
        Node().add(
            Node(Map({"name": "a"})),
            data=Map({"S": "", "E": ""}),
        )
    )
    assert newick.parse("a[&&NHX:'quote'':=arg'='quote=:''value'];") == (
        Node(Map({"name": "a", "quote':=arg": "quote=:'value"}))
    )


def test_props_beast():
    assert newick.parse("a[&];") == Node(Map({"name": "a"}))
    assert newick.parse("a[&height=100.0,colour={red}];") == (
        Node(Map({"name": "a", "height": "100.0", "colour": "{red}"}))
    )
    assert newick.parse("a[&height=100.0,colour={red},];") == (
        Node(Map({"name": "a", "height": "100.0", "colour": "{red}"}))
    )
    assert newick.parse("a[&height=[],colour=];") == (
        Node(Map({"name": "a", "height": "", "colour": ""}))
    )
    assert newick.parse("a[&height=[],colour=,];") == (
        Node(Map({"name": "a", "height": "", "colour": ""}))
    )
    assert newick.parse("a[&height={},colour=(),test=[]];") == (
        Node(Map({"name": "a", "height": "{}", "colour": "()", "test": ""}))
    )
    assert newick.parse("(a[&s=,e=]:12);") == (
        Node().add(
            Node(Map({"name": "a", "s": "", "e": ""})),
            data=Map({"length": "12"}),
        )
    )
    assert newick.parse("(a:12[&s=,e=]);") == (
        Node().add(
            Node(Map({"name": "a"})),
            data=Map({"length": "12", "s": "", "e": ""}),
        )
    )
    assert newick.parse("(a:[&s=,e=]);") == (
        Node().add(
            Node(Map({"name": "a"})),
            data=Map({"s": "", "e": ""}),
        )
    )
    assert newick.parse("a[&'quote'':=arg'='quote=:''value',];") == (
        Node(Map({"name": "a", "quote':=arg": "quote=:'value"}))
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
        Node()
        .add(Node(Map({"name": "B"})), data=Map({"length": "6.0"}))
        .add(
            Node()
            .add(Node(Map({"name": "A"})), data=Map({"length": "5.0"}))
            .add(Node(Map({"name": "C"})), data=Map({"length": "3.0"}))
            .add(Node(Map({"name": "E"})), data=Map({"length": "4.0"})),
            data=Map({"length": "5.0"}),
        )
        .add(Node(Map({"name": "D"})), data=Map({"length": "11.0"}))
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
            Node()
            .add(
                Node()
                .add(Node(Map({"name": "raccoon"})), data=Map({"length": "19.19959"}))
                .add(Node(Map({"name": "bear"})), data=Map({"length": "6.80041"})),
                data=Map({"length": "0.84600"}),
            )
            .add(
                Node()
                .add(
                    Node()
                    .add(
                        Node(Map({"name": "sea lion"})),
                        data=Map({"length": "11.99700"}),
                    )
                    .add(Node(Map({"name": "seal"})), data=Map({"length": "12.00300"})),
                    data=Map({"length": "7.52973"}),
                )
                .add(
                    Node()
                    .add(
                        Node()
                        .add(
                            Node(Map({"name": "monkey"})),
                            data=Map({"length": "100.85930"}),
                        )
                        .add(
                            Node(Map({"name": "cat"})), data=Map({"length": "47.14069"})
                        ),
                        data=Map({"length": "20.59201"}),
                    )
                    .add(
                        Node(Map({"name": "weasel"})), data=Map({"length": "18.87953"})
                    ),
                    data=Map({"length": "2.09460"}),
                ),
                data=Map({"length": "3.87382"}),
            )
            .add(Node(Map({"name": "dog"})), data=Map({"length": "25.46154"}))
        )
    )
