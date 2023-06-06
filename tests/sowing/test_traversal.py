from sowing.node import Node
from sowing.traversal import Order, traverse, maptree, mapnodes, leaves


def test_traverse():
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

    assert_iter_eq(traverse(root), "cbfgiheda")
    assert_iter_eq(traverse(root, reverse=True), "adehigfbc")

    assert_iter_eq(traverse(root, Order.Pre), "abcdefghi")
    assert_iter_eq(traverse(root, Order.Pre, reverse=True), "ihgfedcba")

    assert_iter_eq(traverse(root, Order.Euler), "abcbadefegehiheda")
    assert_iter_eq(traverse(root, Order.Euler, reverse=True), "adehihegefedabcba")


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
    after = (
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

    # Double all node names (preorder or postorder)
    def relabel(node):
        return node.replace(data=node.data * 2)

    assert mapnodes(relabel, traverse(before)) == after
    assert mapnodes(relabel, traverse(before, Order.Pre)) == after
    assert mapnodes(relabel, traverse(before, Order.Post)) == after


def test_map_edges():
    before = (
        Node("a")
        .add(data="z", node=Node("b").add(Node("c")))
        .add(
            data="y",
            node=Node("d").add(
                data="x",
                node=Node("e")
                .add(data="w", node=Node("f"))
                .add(data="v", node=Node("g"))
                .add(data="u", node=Node("h").add(data="t", node=Node("i"))),
            ),
        )
    )
    after = (
        Node("aa")
        .add(data="zzz", node=Node("bb").add(Node("cc")))
        .add(
            data="yyy",
            node=Node("dd").add(
                data="xxx",
                node=Node("ee")
                .add(data="www", node=Node("ff"))
                .add(data="vvv", node=Node("gg"))
                .add(data="uuu", node=Node("hh").add(data="ttt", node=Node("ii"))),
            ),
        )
    )

    # Double node names and triple edge names
    def relabel(node, edge):
        node = node.replace(data=node.data * 2)
        edge = edge * 3 if edge is not None else None
        return node, edge

    assert mapnodes(relabel, traverse(before)) == after
    assert mapnodes(relabel, traverse(before, Order.Pre)) == after
    assert mapnodes(relabel, traverse(before, Order.Post)) == after


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

    assert mapnodes(contract_unary, traverse(before)) == after
    assert mapnodes(contract_unary, traverse(before, Order.Pre)) == after
    assert mapnodes(contract_unary, traverse(before, Order.Post)) == after


def test_map_remove():
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
    after = Node("a").add(Node("e")).add(Node("h").add(Node("i")).add(Node("j")))

    # Remove unary nodes and leaves “c”, “f” and “g”
    def contract_remove(node):
        if len(node.edges) == 1:
            return node.edges[0].node

        if len(node.edges) == 0 and node.data in "cfg":
            return None

        return node

    assert mapnodes(contract_remove, traverse(before, Order.Post)) == after


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

    assert mapnodes(fold_expression, traverse(before)) == after
    assert mapnodes(fold_expression, traverse(before, Order.Post)) == after


def test_map_expand():
    before = Node(3)
    after_pre = Node(3).add(Node(2).add(Node(1).add(Node(0))))
    after_post = Node(3).add(Node(2))

    # Expand nodes according to their value
    def expand_value(node):
        if node.data > 0:
            return node.add(Node(node.data - 1))

        return node

    assert mapnodes(expand_value, traverse(before)) == after_post
    assert mapnodes(expand_value, traverse(before, Order.Pre)) == after_pre
    assert mapnodes(expand_value, traverse(before, Order.Post)) == after_post


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
    def depth(cursor):
        return cursor.replace(node=cursor.node.replace(data=cursor.depth))

    assert maptree(depth, traverse(before, Order.Pre)) == after


def test_map_visits():
    before = (
        Node(0)
        .add(Node(0).add(Node(0)))
        .add(Node(0).add(Node(0).add(Node(0)).add(Node(0)).add(Node(0).add(Node(0)))))
    )
    after_pre_post = (
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

    assert mapnodes(visit, traverse(before)) == after_pre_post
    assert mapnodes(visit, traverse(before, Order.Pre)) == after_pre_post
    assert mapnodes(visit, traverse(before, Order.Post)) == after_pre_post
    assert mapnodes(visit, traverse(before, Order.Euler)) == after_euler


def test_leaves():
    single = Node("a")
    assert list(leaves(single)) == [Node("a")]

    root = (
        Node("a")
        .add(Node("b").add(Node("c")))
        .add(
            Node("d").add(
                Node("e").add(Node("f")).add(Node("g")).add(Node("h").add(Node("i")))
            )
        )
    )
    assert list(leaves(root)) == list(map(Node, "cfgi"))
