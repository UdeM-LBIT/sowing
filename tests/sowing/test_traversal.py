from sowing.node import Node
from sowing.traversal import depth, euler, leaves
from sowing import traversal


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

    assert_iter_eq(depth(None), "")
    assert_iter_eq(euler(None), "")
    assert_iter_eq(leaves(None), "")

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

    # Double all node names
    def relabel(node, edge, *_):
        return node * 2, edge

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
    def relabel(node, edge, *_):
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
    def map_index(node, edge, index, *_):
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

    def visit(node, edge, *_):
        return node + 1, edge

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
