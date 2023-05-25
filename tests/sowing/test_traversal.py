from sowing.node import Node
from sowing.traversal import Order, traverse, maptree


def test_traverse():
    root = (
        Node("a")
        .add(Node("b").add(Node("c")))
        .add(Node("d").add(
            Node("e")
            .add(Node("f"))
            .add(Node("g"))
            .add(Node("h").add(Node("i")))
        ))
    )

    def assert_iter_eq(iterable1, iterable2):
        assert [zipper.node.data for zipper in iterable1] == list(iterable2)

    assert_iter_eq(traverse(root), "cbfgiheda")
    assert_iter_eq(traverse(root, reverse=True), "adehigfbc")

    assert_iter_eq(traverse(root, Order.Pre), "abcdefghi")
    assert_iter_eq(traverse(root, Order.Pre, reverse=True), "ihgfedcba")

    assert_iter_eq(traverse(root, Order.Euler), "abcbadefegehiheda")
    assert_iter_eq(traverse(root, Order.Euler, reverse=True), "adehihegefedabcba")


def test_transform_relabel():
    before = (
        Node("a")
        .add(Node("b").add(Node("c")))
        .add(Node("d").add(
            Node("e")
            .add(Node("f"))
            .add(Node("g"))
            .add(Node("h").add(Node("i")))
        ))
    )
    after = (
        Node("aa")
        .add(Node("bb").add(Node("cc")))
        .add(Node("dd").add(
            Node("ee")
            .add(Node("ff"))
            .add(Node("gg"))
            .add(Node("hh").add(Node("ii")))
        ))
    )

    # Double all node names (preorder or postorder)
    def relabel(node):
        return node.label(node.data * 2)

    assert maptree(relabel, traverse(before)) == after
    assert maptree(relabel, traverse(before, Order.Pre)) == after
    assert maptree(relabel, traverse(before, Order.Post)) == after


def test_transform_replace():
    before = (
        Node("a")
        .add(Node("b").add(Node("c")))
        .add(Node("d").add(
            Node("e")
            .add(Node("f"))
            .add(Node("g"))
            .add(Node("h").add(Node("i")))
        ))
    )
    after = (
        Node("a")
        .add(Node("c"))
        .add(Node("e").add(Node("f")).add(Node("g")).add(Node("i")))
    )

    # Remove all unary nodes (preorder or postorder)
    def remove_unary(node):
        if len(node.children) == 1:
            return node.children[0]

        return node

    assert maptree(remove_unary, traverse(before)) == after
    assert maptree(remove_unary, traverse(before, Order.Pre)) == after
    assert maptree(remove_unary, traverse(before, Order.Post)) == after


def test_transform_fold():
    before = (
        Node(int.__mul__)
        .add(Node(int.__add__)
             .add(Node(6))
             .add(Node(2))
        )
        .add(Node(int.__floordiv__)
             .add(Node(18))
             .add(Node(int.__mul__)
                  .add(Node(2))
                  .add(Node(3))
             )
        )
    )
    after = Node(24)

    # Fold arithmetical expressions to their result (postorder only)
    def fold_expression(node):
        if type(node.data) == int:
            return node

        args = map(lambda child: child.data, node.children)
        return Node(node.data(*args))

    assert maptree(fold_expression, traverse(before)) == after
    assert maptree(fold_expression, traverse(before, Order.Post)) == after


def test_transform_expand():
    before = Node(3)
    after_pre = Node(3).add(Node(2).add(Node(1).add(Node(0))))
    after_post = Node(3).add(Node(2))

    # Expand nodes according to their value
    def expand_value(node):
        if node.data > 0:
            return node.add(Node(node.data - 1))

        return node

    assert maptree(expand_value, traverse(before)) == after_post
    assert maptree(expand_value, traverse(before, Order.Pre)) == after_pre
    assert maptree(expand_value, traverse(before, Order.Post)) == after_post


def test_transform_depth():
    before = (
        Node("a")
        .add(Node("b").add(Node("c")))
        .add(Node("d").add(
            Node("e")
            .add(Node("f"))
            .add(Node("g"))
            .add(Node("h").add(Node("i")))
        ))
    )
    after = (
        Node(0)
        .add(Node(1).add(Node(2)))
        .add(Node(1).add(
            Node(2)
            .add(Node(3))
            .add(Node(3))
            .add(Node(3).add(Node(4)))
        ))
    )

    # Replace node values by their depth
    def depth(node, thread):
        return node.label(len(thread))

    assert maptree(depth, traverse(before)) == after
    assert maptree(depth, traverse(before, Order.Pre)) == after
    assert maptree(depth, traverse(before, Order.Post)) == after


def test_transform_visits():
    before = (
        Node(0)
        .add(Node(0).add(Node(0)))
        .add(Node(0).add(
            Node(0)
            .add(Node(0))
            .add(Node(0))
            .add(Node(0).add(Node(0)))
        ))
    )
    after_pre_post = (
        Node(1)
        .add(Node(1).add(Node(1)))
        .add(Node(1).add(
            Node(1)
            .add(Node(1))
            .add(Node(1))
            .add(Node(1).add(Node(1)))
        ))
    )
    after_euler = (
        Node(3)
        .add(Node(2).add(Node(1)))
        .add(Node(2).add(
            Node(4)
            .add(Node(1))
            .add(Node(1))
            .add(Node(2).add(Node(1)))
        ))
    )

    def visit(node):
        return node.label(node.data + 1)

    assert maptree(visit, traverse(before)) == after_pre_post
    assert maptree(visit, traverse(before, Order.Pre)) == after_pre_post
    assert maptree(visit, traverse(before, Order.Post)) == after_pre_post
    assert maptree(visit, traverse(before, Order.Euler)) == after_euler
