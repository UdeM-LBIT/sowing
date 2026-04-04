from sowing.node import Node
from sowing.repr.graphviz import write


def test_tree():
    tree = (
        Node("a")
        .add(Node("b").add(Node("c")).add(Node("d")), data="y")
        .add(Node().add(Node("f"), data="x"))
    )

    assert write(tree) == """\
digraph {
0 [shape="box", style="rounded", label="a"]
0 -> 1 [label="y"]
0 -> 2
1 [shape="box", style="rounded", label="b"]
1 -> 3
1 -> 4
3 [shape="box", style="rounded", label="c"]
4 [shape="box", style="rounded", label="d"]
2 [shape="box", style="rounded", label=""]
2 -> 5 [label="x"]
5 [shape="box", style="rounded", label="f"]
}\
"""

    assert (
        write(
            tree,
            node_style=lambda _: {"shape": "circle"},
            edge_style=lambda _: {"decorate": "true"},
            graph_style={"rankdir": "RL"},
        )
        == """\
digraph {
rankdir="RL";
0 [shape="circle"]
0 -> 1 [decorate="true"]
0 -> 2 [decorate="true"]
1 [shape="circle"]
1 -> 3 [decorate="true"]
1 -> 4 [decorate="true"]
3 [shape="circle"]
4 [shape="circle"]
2 [shape="circle"]
2 -> 5 [decorate="true"]
5 [shape="circle"]
}\
"""
    )


def test_dag():
    c = Node("c")
    b1 = Node("b").add(c, data="c1")
    b2 = Node("b").add(c, data="c2")
    a = Node("a").add(b1, data="b1").add(b2, data="b2")

    assert write(a) == """\
digraph {
0 [shape="box", style="rounded", label="a"]
0 -> 1 [label="b1"]
0 -> 2 [label="b2"]
1 [shape="box", style="rounded", label="b"]
1 -> 3 [label="c1"]
3 [shape="box", style="rounded", label="c"]
2 [shape="box", style="rounded", label="b"]
2 -> 3 [label="c2"]
}\
"""
