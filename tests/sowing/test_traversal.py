from sowing.node import Node
from sowing.traversal import depth, euler, leaves, maptree, mapnodes


def test_traverse():
    single = Node("a")
    root = (
        Node("a")
        .add(Node("b").add(Node("c")))
        .add(
            Node("d").add(
                Node("e").add(Node("f")).add(Node("g")).add(Node("h").add(Node("i")))
            )
        )
    )

    def assert_iter_eq(iterable1, iterable2):
        assert [zipper.node.data for zipper in iterable1] == list(iterable2)

    assert_iter_eq(depth(single), "a")
    assert_iter_eq(depth(single, reverse=True), "a")
    assert_iter_eq(depth(single, preorder=True), "a")
    assert_iter_eq(depth(single, preorder=True, reverse=True), "a")

    assert_iter_eq(euler(single), "a")
    assert_iter_eq(euler(single, reverse=True), "a")

    assert_iter_eq(leaves(single), "a")
    assert_iter_eq(leaves(single, reverse=True), "a")

    assert_iter_eq(depth(root), "cbfgiheda")
    assert_iter_eq(depth(root, reverse=True), "adehigfbc")
    assert_iter_eq(depth(root, preorder=True), "abcdefghi")
    assert_iter_eq(depth(root, preorder=True, reverse=True), "ihgfedcba")

    assert_iter_eq(euler(root), "abcbadefegehiheda")
    assert_iter_eq(euler(root, reverse=True), "adehihegefedabcba")

    assert_iter_eq(leaves(root), "cfgi")
    assert_iter_eq(leaves(root, reverse=True), "igfc")


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

    # Double all node names (preorder or postorder)
    def relabel(node):
        return node.replace(data=node.data * 2)

    assert mapnodes(relabel, depth(before)) == after_depth
    assert mapnodes(relabel, depth(before, preorder=True)) == after_depth
    assert mapnodes(relabel, leaves(before)) == after_leaves


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
        node = node.replace(data=node.data * 2)
        edge = edge * 3 if edge is not None else None
        return node, edge

    assert mapnodes(relabel, depth(before)) == after
    assert mapnodes(relabel, depth(before, preorder=True)) == after


def test_map_replace():
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

    # Replace all unary nodes with their child (preorder or postorder)
    def contract_unary(node):
        if len(node.edges) == 1:
            return node.edges[0].node

        return node

    assert mapnodes(contract_unary, depth(before)) == after
    assert mapnodes(contract_unary, depth(before, preorder=True)) == after


def test_map_remove():
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
    def contract_remove(node):
        if len(node.edges) == 1:
            return node.edges[0].node

        if len(node.edges) == 0 and node.data in "cfg":
            return None

        return node

    assert mapnodes(contract_remove, depth(before)) == after_post
    assert mapnodes(contract_remove, depth(before, preorder=True)) == after_pre


def test_map_remove_all():
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

    def remove_all(node):
        return None

    assert mapnodes(remove_all, depth(before)) is None
    assert mapnodes(remove_all, depth(before, preorder=True)) is None


def test_map_fold():
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

    # Fold arithmetical expressions to their result (postorder only)
    def fold_expression(node):
        if type(node.data) == int:
            return node

        args = map(lambda edge: edge.node.data, node.edges)
        return Node(node.data(*args))

    assert mapnodes(fold_expression, depth(before)) == after


def test_map_expand():
    before = Node(3)
    after_pre = Node(3).add(Node(2).add(Node(1).add(Node(0))))
    after_post = Node(3).add(Node(2))

    # Expand nodes according to their value
    def expand_value(node):
        if node.data > 0:
            return node.add(Node(node.data - 1))

        return node

    assert mapnodes(expand_value, depth(before)) == after_post
    assert mapnodes(expand_value, depth(before, preorder=True)) == after_pre


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
    def label_depth(cursor):
        return cursor.replace(node=cursor.node.replace(data=cursor.depth))

    assert maptree(label_depth, depth(before)) == after
    assert maptree(label_depth, depth(before, preorder=True)) == after


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
        return node.replace(data=node.data + 1)

    assert mapnodes(visit, depth(before)) == after_depth
    assert mapnodes(visit, depth(before, preorder=True)) == after_depth
    assert mapnodes(visit, euler(before)) == after_euler
