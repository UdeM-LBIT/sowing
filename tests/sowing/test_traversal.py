from sowing.node import Node
from sowing.traversal import depth, euler, leaves
from sowing import traversal
from itertools import product
from .test_node import _make_grid


def assert_same_nodes(iterable, compare):
    for left, right in zip(iterable, compare, strict=True):
        assert left.node is right


def test_traverse():
    assert_same_nodes(depth(None), ())
    assert_same_nodes(euler(None), ())
    assert_same_nodes(leaves(None), ())

    c = Node("c")
    b = Node("b").add(c)
    f = Node("f")
    g = Node("g")
    i = Node("i")
    h = Node("h").add(i)
    e = Node("e").add(f).add(g).add(h)
    d = Node("d").add(e)
    a = Node("a").add(b).add(d)

    #   a
    #  / \
    # b   d
    # |   |
    # c   e
    #    /|\
    #   f g h
    #       |
    #       i

    assert_same_nodes(depth(a), (c, b, f, g, i, h, e, d, a))
    assert_same_nodes(depth(a, reverse=True), (a, d, e, h, i, g, f, b, c))
    assert_same_nodes(depth(a, preorder=True), (a, b, c, d, e, f, g, h, i))
    assert_same_nodes(
        depth(a, preorder=True, reverse=True), (i, h, g, f, e, d, c, b, a)
    )

    assert_same_nodes(euler(a), (a, b, c, b, a, d, e, f, e, g, e, h, i, h, e, d, a))
    assert_same_nodes(
        euler(a, reverse=True), (a, d, e, h, i, h, e, g, e, f, e, d, a, b, c, b, a)
    )

    assert_same_nodes(leaves(a), (c, f, g, i))
    assert_same_nodes(leaves(a, reverse=True), (i, g, f, c))


def test_traverse_repeats():
    c = Node("c")
    e = Node("e")
    g = Node("g")
    h = Node("h")
    f = Node("f").add(g).add(h)
    d = Node("d").add(e).add(f)
    b = Node("b").add(c).add(d)
    i = Node("i").add(d)
    k = Node("k").add(f)
    m = Node("m")
    n = Node("n")
    l = Node("l").add(m).add(h).add(n)  # noqa: E741
    j = Node("j").add(k).add(l)
    a = Node("a").add(b).add(i).add(j)

    #       a
    #     / | \
    #   b   i   j
    #  / \ /   / \
    # c   d   k   l
    #    / \ /   /|\
    #   e   f   m | n
    #      / \    /
    #     g   h _/

    assert_same_nodes(
        depth(a), (c, e, g, h, f, d, b, e, g, h, f, d, i, g, h, f, k, m, h, n, l, j, a)
    )
    assert_same_nodes(depth(a, unique=True), (c, e, g, h, f, d, b, i, k, m, n, l, j, a))
    assert_same_nodes(
        depth(a, reverse=True),
        (a, j, l, n, h, m, k, f, h, g, i, d, f, h, g, e, b, d, f, h, g, e, c),
    )
    assert_same_nodes(
        depth(a, reverse=True, unique=True), (a, j, l, n, h, m, k, f, g, i, d, e, b, c)
    )
    assert_same_nodes(
        depth(a, preorder=True),
        (a, b, c, d, e, f, g, h, i, d, e, f, g, h, j, k, f, g, h, l, m, h, n),
    )
    assert_same_nodes(
        depth(a, preorder=True, unique=True), (a, b, c, d, e, f, g, h, i, j, k, l, m, n)
    )
    assert_same_nodes(
        depth(a, preorder=True, reverse=True),
        (n, h, m, l, h, g, f, k, j, h, g, f, e, d, i, h, g, f, e, d, c, b, a),
    )
    assert_same_nodes(
        depth(a, preorder=True, reverse=True, unique=True),
        (n, h, m, l, g, f, k, j, e, d, i, c, b, a),
    )


def test_traverse_repeats_exp():
    size = 30
    grid = _make_grid(size)

    for cursor, cell in zip(depth(grid, unique=True), product(range(size), repeat=2)):
        assert cursor.node.data == cell


def test_map_relabel():
    before = (
        Node("a")
        .add(Node("b").add(Node("c")))
        .add(
            Node("d").add(
                Node("e").add(Node("f")).add(Node("g")).add(Node("h").add(Node("i")))
            )
        )
    )
    after_depth = (
        Node("aa")
        .add(Node("bb").add(Node("cc")))
        .add(
            Node("dd").add(
                Node("ee")
                .add(Node("ff"))
                .add(Node("gg"))
                .add(Node("hh").add(Node("ii")))
            )
        )
    )
    after_leaves = (
        Node("a")
        .add(Node("b").add(Node("cc")))
        .add(
            Node("d").add(
                Node("e").add(Node("ff")).add(Node("gg")).add(Node("h").add(Node("ii")))
            )
        )
    )

    # Double all node names
    def relabel(node):
        return node * 2

    assert traversal.map(relabel, depth(before)) == after_depth
    assert traversal.map(relabel, depth(before, preorder=True)) == after_depth
    assert traversal.map(relabel, leaves(before)) == after_leaves


def test_map_edges():
    before = (
        Node("a")
        .add(Node("b").add(Node("c")), data="z")
        .add(
            Node("d").add(
                Node("e")
                .add(Node("f"), data="w")
                .add(Node("g"), data="v")
                .add(Node("h").add(Node("i"), data="t"), data="u"),
                data="x",
            ),
            data="y",
        )
    )
    after = (
        Node("aa")
        .add(Node("bb").add(Node("cc")), data="zzz")
        .add(
            Node("dd").add(
                Node("ee")
                .add(Node("ff"), data="www")
                .add(Node("gg"), data="vvv")
                .add(Node("hh").add(Node("ii"), data="ttt"), data="uuu"),
                data="xxx",
            ),
            data="yyy",
        )
    )

    # Double node names and triple edge names
    def relabel(node, edge):
        node *= 2
        edge = edge * 3 if edge is not None else None
        return node, edge

    assert traversal.map(relabel, depth(before)) == after
    assert traversal.map(relabel, depth(before, preorder=True)) == after


def test_map_depth():
    before = (
        Node("a")
        .add(Node("b").add(Node("c")))
        .add(
            Node("d").add(
                Node("e").add(Node("f")).add(Node("g")).add(Node("h").add(Node("i")))
            )
        )
    )
    after = (
        Node(0)
        .add(Node(1).add(Node(2)))
        .add(Node(1).add(Node(2).add(Node(3)).add(Node(3)).add(Node(3).add(Node(4)))))
    )

    # Replace node values by their depth
    def map_depth(node, edge, _, depth):
        return depth, edge

    assert traversal.map(map_depth, depth(before)) == after
    assert traversal.map(map_depth, depth(before, preorder=True)) == after


def test_map_sibling():
    before = (
        Node("a")
        .add(Node("b").add(Node("c")))
        .add(
            Node("d").add(
                Node("e").add(Node("f")).add(Node("g")).add(Node("h").add(Node("i")))
            )
        )
    )
    after = (
        Node(-1)
        .add(Node(0).add(Node(0)))
        .add(Node(1).add(Node(0).add(Node(0)).add(Node(1)).add(Node(2).add(Node(0)))))
    )

    # Replace node values by their sibling index
    def map_index(node, edge, index):
        return index, edge

    assert traversal.map(map_index, depth(before)) == after
    assert traversal.map(map_index, depth(before, preorder=True)) == after


def test_map_visits():
    before = (
        Node(0)
        .add(Node(0).add(Node(0)))
        .add(Node(0).add(Node(0).add(Node(0)).add(Node(0)).add(Node(0).add(Node(0)))))
    )
    after_depth = (
        Node(1)
        .add(Node(1).add(Node(1)))
        .add(Node(1).add(Node(1).add(Node(1)).add(Node(1)).add(Node(1).add(Node(1)))))
    )
    after_euler = (
        Node(3)
        .add(Node(2).add(Node(1)))
        .add(Node(2).add(Node(4).add(Node(1)).add(Node(1)).add(Node(2).add(Node(1)))))
    )

    def visit(node):
        return node + 1

    assert traversal.map(visit, depth(before)) == after_depth
    assert traversal.map(visit, depth(before, preorder=True)) == after_depth
    assert traversal.map(visit, euler(before)) == after_euler


def test_fold_replace():
    before = (
        Node("a")
        .add(Node("b").add(Node("c")))
        .add(
            Node("d").add(
                Node("e").add(Node("f")).add(Node("g")).add(Node("h").add(Node("i")))
            )
        )
    )
    after = (
        Node("a")
        .add(Node("c"))
        .add(Node("e").add(Node("f")).add(Node("g")).add(Node("i")))
    )

    # Replace all unary nodes with their child
    def contract_unary(zipper):
        node = zipper.node

        if len(node.edges) == 1:
            return zipper.replace(node=node.edges[0].node)

        return zipper

    assert traversal.fold(contract_unary, depth(before)) == after
    assert traversal.fold(contract_unary, depth(before, preorder=True)) == after


def test_fold_remove():
    before = (
        Node("a")
        .add(
            Node("b")
            .add(Node("c"))
            .add(Node("d").add(Node("e")).add(Node("f")))
            .add(Node("g"))
        )
        .add(Node("h").add(Node("i").add(Node("j"))))
    )
    after_pre = (
        Node("a")
        .add(Node("b").add(Node("d").add(Node("e"))))
        .add(Node("i").add(Node("j")))
    )
    after_post = Node("a").add(Node("e")).add(Node("j"))

    # Remove unary nodes and leaves “c”, “f” and “g”
    def contract_remove(zipper):
        node = zipper.node

        if len(node.edges) == 1:
            return zipper.replace(node=node.edges[0].node)

        if len(node.edges) == 0 and node.data in "cfg":
            return zipper.replace(node=None)

        return zipper

    assert traversal.fold(contract_remove, depth(before)) == after_post
    assert traversal.fold(contract_remove, depth(before, preorder=True)) == after_pre


def test_fold_empty():
    before = (
        Node("a")
        .add(
            Node("b")
            .add(Node("c"))
            .add(Node("d").add(Node("e")).add(Node("f")))
            .add(Node("g"))
        )
        .add(Node("h").add(Node("i")).add(Node("j")))
    )

    def remove_all(zipper):
        return zipper.replace(node=None)

    assert traversal.fold(remove_all, depth(before)) is None
    assert traversal.fold(remove_all, depth(before, preorder=True)) is None

    result = traversal.fold(remove_all, depth(before, preorder=True))
    assert traversal.fold(remove_all, depth(result, preorder=True)) is None


def test_fold_reduce():
    before = (
        Node(int.__mul__)
        .add(Node(int.__add__).add(Node(6)).add(Node(2)))
        .add(
            Node(int.__floordiv__)
            .add(Node(18))
            .add(Node(int.__mul__).add(Node(2)).add(Node(3)))
        )
    )
    after = Node(24)

    # Reduce arithmetical expressions to their result
    def reduce(zipper):
        node = zipper.node

        if isinstance(node.data, int):
            return zipper

        args = map(lambda edge: edge.node.data, node.edges)
        return zipper.replace(node=Node(node.data(*args)))

    assert traversal.fold(reduce, depth(before)) == after


def test_fold_expand():
    before = Node(3)
    after_pre = Node(3).add(Node(2).add(Node(1).add(Node(0))))
    after_post = Node(3).add(Node(2))

    # Expand nodes according to their value
    def expand_value(zipper):
        node = zipper.node

        if node.data > 0:
            return zipper.replace(node=node.add(Node(node.data - 1)))

        return zipper

    assert traversal.fold(expand_value, depth(before)) == after_post
    assert traversal.fold(expand_value, depth(before, preorder=True)) == after_pre
