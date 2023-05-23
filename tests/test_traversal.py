from sowing.net import Net
from sowing.traversal import Order, traverse, transform


def test_traverse():
    root = (
        Net("a")
        .add(Net("b").add(Net("c")))
        .add(Net("d").add(
            Net("e")
            .add(Net("f"))
            .add(Net("g"))
            .add(Net("h").add(Net("i")))
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
        Net("a")
        .add(Net("b").add(Net("c")))
        .add(Net("d").add(
            Net("e")
            .add(Net("f"))
            .add(Net("g"))
            .add(Net("h").add(Net("i")))
        ))
    )
    after = (
        Net("aa")
        .add(Net("bb").add(Net("cc")))
        .add(Net("dd").add(
            Net("ee")
            .add(Net("ff"))
            .add(Net("gg"))
            .add(Net("hh").add(Net("ii")))
        ))
    )

    # Double all node names (preorder or postorder)
    def relabel(node, _):
        return node.label(node.data * 2), _

    assert transform(relabel, traverse(before)) == after
    assert transform(relabel, traverse(before, Order.Pre)) == after
    assert transform(relabel, traverse(before, Order.Post)) == after


def test_transform_replace():
    before = (
        Net("a")
        .add(Net("b").add(Net("c")))
        .add(Net("d").add(
            Net("e")
            .add(Net("f"))
            .add(Net("g"))
            .add(Net("h").add(Net("i")))
        ))
    )
    after = (
        Net("a")
        .add(Net("c"))
        .add(Net("e").add(Net("f")).add(Net("g")).add(Net("i")))
    )

    # Remove all unary nodes (preorder or postorder)
    def remove_unary(node, _):
        if len(node.children) == 1:
            return node.children[0][0], _

        return node, _

    assert transform(remove_unary, traverse(before)) == after
    assert transform(remove_unary, traverse(before, Order.Pre)) == after
    assert transform(remove_unary, traverse(before, Order.Post)) == after


def test_transform_fold():
    before = (
        Net(int.__mul__)
        .add(Net(int.__add__)
             .add(Net(6))
             .add(Net(2))
        )
        .add(Net(int.__floordiv__)
             .add(Net(18))
             .add(Net(int.__mul__)
                  .add(Net(2))
                  .add(Net(3))
             )
        )
    )
    after = Net(24)

    # Fold arithmetical expressions to their result (postorder only)
    def fold_expression(node, _):
        if type(node.data) == int:
            return node, _

        args = map(lambda child: child[0].data, node.children)
        return Net(node.data(*args)), _

    assert transform(fold_expression, traverse(before)) == after
    assert transform(fold_expression, traverse(before, Order.Post)) == after


def test_transform_expand():
    before = Net(3)
    after_pre = Net(3).add(Net(2).add(Net(1).add(Net(0))))
    after_post = Net(3).add(Net(2))

    # Expand nodes according to their value
    def expand_value(node, _):
        if node.data > 0:
            return node.add(Net(node.data - 1)), _

        return node, _

    assert transform(expand_value, traverse(before)) == after_post
    assert transform(expand_value, traverse(before, Order.Pre)) == after_pre
    assert transform(expand_value, traverse(before, Order.Post)) == after_post


def test_transform_depth():
    before = (
        Net("a")
        .add(Net("b").add(Net("c")))
        .add(Net("d").add(
            Net("e")
            .add(Net("f"))
            .add(Net("g"))
            .add(Net("h").add(Net("i")))
        ))
    )
    after = (
        Net(0)
        .add(Net(1).add(Net(2)))
        .add(Net(1).add(
            Net(2)
            .add(Net(3))
            .add(Net(3))
            .add(Net(3).add(Net(4)))
        ))
    )

    # Replace node values by their depth
    def depth(node, thread):
        return node.label(len(thread)), thread

    assert transform(depth, traverse(before)) == after
    assert transform(depth, traverse(before, Order.Pre)) == after
    assert transform(depth, traverse(before, Order.Post)) == after
