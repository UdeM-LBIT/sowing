from sowing.node import Node as N
from sowing import traversal
from sowing.comb.binary import is_binary, binarize_at, binarize
from math import prod
from itertools import product


a, b, c, d, e, f, g, h, p, r = map(N, "abcdefghpr")


def test_is_binary():
    assert is_binary(a)
    assert not is_binary(a.add(b))
    assert is_binary(a.add(b).add(c))
    assert not is_binary(a.add(b).add(c).add(d))
    assert not is_binary(a.add(b).add(c).add(c))
    assert is_binary(a.add(a.add(a).add(a)).add(b.add(c).add(c)))
    assert not is_binary(a.add(a.add(b).add(c)).add(b.add(c)))


def _assert_iter_eq(iterable1, iterable2):
    assert list(iterable1) == list(iterable2)


def _assert_same_leaves(tree1, tree2):
    assert set(cursor.node for cursor in traversal.leaves(tree1)) == set(
        cursor.node for cursor in traversal.leaves(tree2)
    )


def test_binarize_at_labeled():
    _assert_iter_eq(binarize_at(N("abc")), [N("abc")])

    _assert_iter_eq(
        binarize_at(N().extend(map(N, "ab"))),
        [N().extend(map(N, "ab"))],
    )

    _assert_iter_eq(
        binarize_at(N().extend(map(N, "abc"))),
        [
            N().add(N().add(a).add(b)).add(c),
            N().add(N().add(a).add(c)).add(b),
            N().add(a).add(N().add(b).add(c)),
        ],
    )

    _assert_iter_eq(
        binarize_at(N().extend(map(N, "abcd"))),
        [
            N().add(N().add(N().add(a).add(b)).add(c)).add(d),
            N().add(N().add(N().add(a).add(c)).add(b)).add(d),
            N().add(N().add(a).add(N().add(b).add(c))).add(d),
            N().add(N().add(N().add(a).add(b)).add(d)).add(c),
            N().add(N().add(N().add(a).add(d)).add(b)).add(c),
            N().add(N().add(a).add(N().add(b).add(d))).add(c),
            N().add(N().add(a).add(b)).add(N().add(c).add(d)),
            N().add(N().add(N().add(a).add(c)).add(d)).add(b),
            N().add(N().add(N().add(a).add(d)).add(c)).add(b),
            N().add(N().add(a).add(N().add(c).add(d))).add(b),
            N().add(N().add(a).add(c)).add(N().add(b).add(d)),
            N().add(N().add(a).add(d)).add(N().add(b).add(c)),
            N().add(a).add(N().add(N().add(b).add(c)).add(d)),
            N().add(a).add(N().add(N().add(b).add(d)).add(c)),
            N().add(a).add(N().add(b).add(N().add(c).add(d))),
        ],
    )

    # Number of unordered binary trees with n labeled leaves:
    # <https://oeis.org/A001147>
    for n in range(7):
        root = N().extend((N(i) for i in range(n)))
        trees = set()

        for tree in binarize_at(root):
            _assert_same_leaves(tree, root)
            trees.add(tree)

        count = prod(range(2 * n - 3, 0, -2))
        assert len(trees) == count


def test_binarize_at_unlabeled():
    _assert_iter_eq(binarize_at(N()), [N()])

    _assert_iter_eq(
        binarize_at(N().extend((N() for _ in range(2)))),
        [N().extend((N() for _ in range(2)))],
    )

    _assert_iter_eq(
        binarize_at(N().extend((N() for _ in range(3)))),
        [N().add(N().add(N()).add(N())).add(N())],
    )

    _assert_iter_eq(
        binarize_at(N().extend((N() for _ in range(4)))),
        [
            N().add(N().add(N().add(N()).add(N())).add(N())).add(N()),
            N().add(N().add(N()).add(N())).add(N().add(N()).add(N())),
        ],
    )

    _assert_iter_eq(
        binarize_at(N().extend((N() for _ in range(5)))),
        [
            N().add(N().add(N().add(N().add(N()).add(N())).add(N())).add(N())).add(N()),
            N()
            .add(
                N().add(N().add(N()).add(N())).add(N().add(N()).add(N())),
            )
            .add(N()),
            N().add(N().add(N().add(N()).add(N())).add(N())).add(N().add(N()).add(N())),
        ],
    )

    # Number of unordered binary trees with n unlabeled leaves:
    # <https://oeis.org/A001190>
    counts = (1, 1, 1, 1, 2, 3, 6, 11, 23, 46, 98, 207, 451, 983)

    for n, count in enumerate(counts):
        root = N().extend((N() for _ in range(n)))
        trees = set()

        for tree in binarize_at(root):
            _assert_same_leaves(tree, root)
            trees.add(tree)

        assert len(trees) == count


def test_binarize_at_multree():
    _assert_iter_eq(
        binarize_at(N().add(a).add(a).add(b)),
        [
            N().add(N().add(a).add(a)).add(b),
            N().add(N().add(a).add(b)).add(a),
        ],
    )

    _assert_iter_eq(
        binarize_at(N().add(a).add(b).add(b)),
        [
            N().add(N().add(a).add(b)).add(b),
            N().add(a).add(N().add(b).add(b)),
        ],
    )

    _assert_iter_eq(
        binarize_at(N().add(a).add(a).add(b).add(b)),
        [
            N().add(N().add(N().add(a).add(a)).add(b)).add(b),
            N().add(N().add(N().add(a).add(b)).add(a)).add(b),
            N().add(N().add(a).add(a)).add(N().add(b).add(b)),
            N().add(N().add(N().add(a).add(b)).add(b)).add(a),
            N().add(N().add(a).add(N().add(b).add(b))).add(a),
            N().add(N().add(a).add(b)).add(N().add(a).add(b)),
        ],
    )

    # Number of rooted binary MUL-trees with n leaves and 3 labels
    # <https://oeis.org/A220816>
    counts = (1, 3, 6, 18, 75, 333, 1620)

    for n, count in enumerate(counts):
        root = N().extend((N() for _ in range(n)))
        trees = set()

        for muls in product(range(n + 1), repeat=3):
            if sum(muls) != n:
                continue

            print(n, muls)

            mul_a, mul_b, mul_c = muls
            root = (
                N()
                .extend((N("a") for _ in range(mul_a)))
                .extend((N("b") for _ in range(mul_b)))
                .extend((N("c") for _ in range(mul_c)))
            )

            for tree in binarize_at(root):
                _assert_same_leaves(tree, root)
                trees.add(tree)

        assert len(trees) == count


def test_binarize():
    _assert_iter_eq(binarize(N("abc")), [N("abc")])

    _assert_iter_eq(binarize(a.add(b)), [a.add(b)])

    _assert_iter_eq(
        binarize(a.add(b).add(c)),
        [a.add(b).add(c)],
    )

    _assert_iter_eq(
        binarize(a.add(b).add(c).add(d)),
        [
            a.add(N().add(b).add(c)).add(d),
            a.add(N().add(b).add(d)).add(c),
            a.add(b).add(N().add(c).add(d)),
        ],
    )

    _assert_iter_eq(
        binarize(a.add(b, data="x").add(c, data="y").add(d, data="z")),
        [
            a.add(N().add(b, data="x").add(c, data="y")).add(d, data="z"),
            a.add(N().add(b, data="x").add(d, data="z")).add(c, data="y"),
            a.add(b, data="x").add(N().add(c, data="y").add(d, data="z")),
        ],
    )

    _assert_iter_eq(
        binarize(
            r.add(
                a.add(b, data="x").add(c, data="y").add(d, data="z"),
                data="w",
            )
        ),
        [
            r.add(
                a.add(N().add(b, data="x").add(c, data="y")).add(d, data="z"),
                data="w",
            ),
            r.add(
                a.add(N().add(b, data="x").add(d, data="z")).add(c, data="y"),
                data="w",
            ),
            r.add(
                a.add(b, data="x").add(N().add(c, data="y").add(d, data="z")),
                data="w",
            ),
        ],
    )

    _assert_iter_eq(
        binarize(
            N()
            .add(N().add(N().add(a).add(b)).add(p.add(c).add(d).add(e).add(f)).add(g))
            .add(h)
        ),
        [
            N()
            .add(
                N()
                .add(
                    N()
                    .add(N().add(a).add(b))
                    .add(p.add(N().add(N().add(c).add(d)).add(e)).add(f))
                )
                .add(g)
            )
            .add(h),
            N()
            .add(
                N()
                .add(N().add(N().add(a).add(b)).add(g))
                .add(p.add(N().add(N().add(c).add(d)).add(e)).add(f))
            )
            .add(h),
            N()
            .add(
                N()
                .add(N().add(a).add(b))
                .add(N().add(p.add(N().add(N().add(c).add(d)).add(e)).add(f)).add(g))
            )
            .add(h),
            N()
            .add(
                N()
                .add(
                    N()
                    .add(N().add(a).add(b))
                    .add(p.add(N().add(N().add(c).add(e)).add(d)).add(f))
                )
                .add(g)
            )
            .add(h),
            N()
            .add(
                N()
                .add(N().add(N().add(a).add(b)).add(g))
                .add(p.add(N().add(N().add(c).add(e)).add(d)).add(f))
            )
            .add(h),
            N()
            .add(
                N()
                .add(N().add(a).add(b))
                .add(N().add(p.add(N().add(N().add(c).add(e)).add(d)).add(f)).add(g))
            )
            .add(h),
            N()
            .add(
                N()
                .add(
                    N()
                    .add(N().add(a).add(b))
                    .add(p.add(N().add(c).add(N().add(d).add(e))).add(f))
                )
                .add(g)
            )
            .add(h),
            N()
            .add(
                N()
                .add(N().add(N().add(a).add(b)).add(g))
                .add(p.add(N().add(c).add(N().add(d).add(e))).add(f))
            )
            .add(h),
            N()
            .add(
                N()
                .add(N().add(a).add(b))
                .add(N().add(p.add(N().add(c).add(N().add(d).add(e))).add(f)).add(g))
            )
            .add(h),
            N()
            .add(
                N()
                .add(
                    N()
                    .add(N().add(a).add(b))
                    .add(p.add(N().add(N().add(c).add(d)).add(f)).add(e))
                )
                .add(g)
            )
            .add(h),
            N()
            .add(
                N()
                .add(N().add(N().add(a).add(b)).add(g))
                .add(p.add(N().add(N().add(c).add(d)).add(f)).add(e))
            )
            .add(h),
            N()
            .add(
                N()
                .add(N().add(a).add(b))
                .add(N().add(p.add(N().add(N().add(c).add(d)).add(f)).add(e)).add(g))
            )
            .add(h),
            N()
            .add(
                N()
                .add(
                    N()
                    .add(N().add(a).add(b))
                    .add(p.add(N().add(N().add(c).add(f)).add(d)).add(e))
                )
                .add(g)
            )
            .add(h),
            N()
            .add(
                N()
                .add(N().add(N().add(a).add(b)).add(g))
                .add(p.add(N().add(N().add(c).add(f)).add(d)).add(e))
            )
            .add(h),
            N()
            .add(
                N()
                .add(N().add(a).add(b))
                .add(N().add(p.add(N().add(N().add(c).add(f)).add(d)).add(e)).add(g))
            )
            .add(h),
            N()
            .add(
                N()
                .add(
                    N()
                    .add(N().add(a).add(b))
                    .add(p.add(N().add(c).add(N().add(d).add(f))).add(e))
                )
                .add(g)
            )
            .add(h),
            N()
            .add(
                N()
                .add(N().add(N().add(a).add(b)).add(g))
                .add(p.add(N().add(c).add(N().add(d).add(f))).add(e))
            )
            .add(h),
            N()
            .add(
                N()
                .add(N().add(a).add(b))
                .add(N().add(p.add(N().add(c).add(N().add(d).add(f))).add(e)).add(g))
            )
            .add(h),
            N()
            .add(
                N()
                .add(
                    N()
                    .add(N().add(a).add(b))
                    .add(p.add(N().add(c).add(d)).add(N().add(e).add(f)))
                )
                .add(g)
            )
            .add(h),
            N()
            .add(
                N()
                .add(N().add(N().add(a).add(b)).add(g))
                .add(p.add(N().add(c).add(d)).add(N().add(e).add(f)))
            )
            .add(h),
            N()
            .add(
                N()
                .add(N().add(a).add(b))
                .add(N().add(p.add(N().add(c).add(d)).add(N().add(e).add(f))).add(g))
            )
            .add(h),
            N()
            .add(
                N()
                .add(
                    N()
                    .add(N().add(a).add(b))
                    .add(p.add(N().add(N().add(c).add(e)).add(f)).add(d))
                )
                .add(g)
            )
            .add(h),
            N()
            .add(
                N()
                .add(N().add(N().add(a).add(b)).add(g))
                .add(p.add(N().add(N().add(c).add(e)).add(f)).add(d))
            )
            .add(h),
            N()
            .add(
                N()
                .add(N().add(a).add(b))
                .add(N().add(p.add(N().add(N().add(c).add(e)).add(f)).add(d)).add(g))
            )
            .add(h),
            N()
            .add(
                N()
                .add(
                    N()
                    .add(N().add(a).add(b))
                    .add(p.add(N().add(N().add(c).add(f)).add(e)).add(d))
                )
                .add(g)
            )
            .add(h),
            N()
            .add(
                N()
                .add(N().add(N().add(a).add(b)).add(g))
                .add(p.add(N().add(N().add(c).add(f)).add(e)).add(d))
            )
            .add(h),
            N()
            .add(
                N()
                .add(N().add(a).add(b))
                .add(N().add(p.add(N().add(N().add(c).add(f)).add(e)).add(d)).add(g))
            )
            .add(h),
            N()
            .add(
                N()
                .add(
                    N()
                    .add(N().add(a).add(b))
                    .add(p.add(N().add(c).add(N().add(e).add(f))).add(d))
                )
                .add(g)
            )
            .add(h),
            N()
            .add(
                N()
                .add(N().add(N().add(a).add(b)).add(g))
                .add(p.add(N().add(c).add(N().add(e).add(f))).add(d))
            )
            .add(h),
            N()
            .add(
                N()
                .add(N().add(a).add(b))
                .add(N().add(p.add(N().add(c).add(N().add(e).add(f))).add(d)).add(g))
            )
            .add(h),
            N()
            .add(
                N()
                .add(
                    N()
                    .add(N().add(a).add(b))
                    .add(p.add(N().add(c).add(e)).add(N().add(d).add(f)))
                )
                .add(g)
            )
            .add(h),
            N()
            .add(
                N()
                .add(N().add(N().add(a).add(b)).add(g))
                .add(p.add(N().add(c).add(e)).add(N().add(d).add(f)))
            )
            .add(h),
            N()
            .add(
                N()
                .add(N().add(a).add(b))
                .add(N().add(p.add(N().add(c).add(e)).add(N().add(d).add(f))).add(g))
            )
            .add(h),
            N()
            .add(
                N()
                .add(
                    N()
                    .add(N().add(a).add(b))
                    .add(p.add(N().add(c).add(f)).add(N().add(d).add(e)))
                )
                .add(g)
            )
            .add(h),
            N()
            .add(
                N()
                .add(N().add(N().add(a).add(b)).add(g))
                .add(p.add(N().add(c).add(f)).add(N().add(d).add(e)))
            )
            .add(h),
            N()
            .add(
                N()
                .add(N().add(a).add(b))
                .add(N().add(p.add(N().add(c).add(f)).add(N().add(d).add(e))).add(g))
            )
            .add(h),
            N()
            .add(
                N()
                .add(
                    N()
                    .add(N().add(a).add(b))
                    .add(p.add(c).add(N().add(N().add(d).add(e)).add(f)))
                )
                .add(g)
            )
            .add(h),
            N()
            .add(
                N()
                .add(N().add(N().add(a).add(b)).add(g))
                .add(p.add(c).add(N().add(N().add(d).add(e)).add(f)))
            )
            .add(h),
            N()
            .add(
                N()
                .add(N().add(a).add(b))
                .add(N().add(p.add(c).add(N().add(N().add(d).add(e)).add(f))).add(g))
            )
            .add(h),
            N()
            .add(
                N()
                .add(
                    N()
                    .add(N().add(a).add(b))
                    .add(p.add(c).add(N().add(N().add(d).add(f)).add(e)))
                )
                .add(g)
            )
            .add(h),
            N()
            .add(
                N()
                .add(N().add(N().add(a).add(b)).add(g))
                .add(p.add(c).add(N().add(N().add(d).add(f)).add(e)))
            )
            .add(h),
            N()
            .add(
                N()
                .add(N().add(a).add(b))
                .add(N().add(p.add(c).add(N().add(N().add(d).add(f)).add(e))).add(g))
            )
            .add(h),
            N()
            .add(
                N()
                .add(
                    N()
                    .add(N().add(a).add(b))
                    .add(p.add(c).add(N().add(d).add(N().add(e).add(f))))
                )
                .add(g)
            )
            .add(h),
            N()
            .add(
                N()
                .add(N().add(N().add(a).add(b)).add(g))
                .add(p.add(c).add(N().add(d).add(N().add(e).add(f))))
            )
            .add(h),
            N()
            .add(
                N()
                .add(N().add(a).add(b))
                .add(N().add(p.add(c).add(N().add(d).add(N().add(e).add(f)))).add(g))
            )
            .add(h),
        ],
    )


def test_binarize_default():
    default = N(42)

    _assert_iter_eq(binarize(N("abc"), default), [N("abc")])

    _assert_iter_eq(binarize(a.add(b), default), [a.add(b)])

    _assert_iter_eq(
        binarize(a.add(b).add(c), default),
        [a.add(b).add(c)],
    )

    _assert_iter_eq(
        binarize(a.add(b).add(c).add(d), default),
        [
            a.add(default.add(b).add(c)).add(d),
            a.add(default.add(b).add(d)).add(c),
            a.add(b).add(default.add(c).add(d)),
        ],
    )

    _assert_iter_eq(
        binarize(a.add(b, data="x").add(c, data="y").add(d, data="z"), default),
        [
            a.add(default.add(b, data="x").add(c, data="y")).add(d, data="z"),
            a.add(default.add(b, data="x").add(d, data="z")).add(c, data="y"),
            a.add(b, data="x").add(default.add(c, data="y").add(d, data="z")),
        ],
    )

    _assert_iter_eq(
        binarize(
            r.add(
                a.add(b, data="x").add(c, data="y").add(d, data="z"),
                data="w",
            ),
            default,
        ),
        [
            r.add(
                a.add(default.add(b, data="x").add(c, data="y")).add(d, data="z"),
                data="w",
            ),
            r.add(
                a.add(default.add(b, data="x").add(d, data="z")).add(c, data="y"),
                data="w",
            ),
            r.add(
                a.add(b, data="x").add(default.add(c, data="y").add(d, data="z")),
                data="w",
            ),
        ],
    )

    _assert_iter_eq(
        binarize(
            N()
            .add(N().add(N().add(a).add(b)).add(p.add(c).add(d).add(e).add(f)).add(g))
            .add(h),
            default,
        ),
        [
            N()
            .add(
                N()
                .add(
                    default.add(N().add(a).add(b)).add(
                        p.add(default.add(default.add(c).add(d)).add(e)).add(f)
                    )
                )
                .add(g)
            )
            .add(h),
            N()
            .add(
                N()
                .add(default.add(N().add(a).add(b)).add(g))
                .add(p.add(default.add(default.add(c).add(d)).add(e)).add(f))
            )
            .add(h),
            N()
            .add(
                N()
                .add(N().add(a).add(b))
                .add(
                    default.add(
                        p.add(default.add(default.add(c).add(d)).add(e)).add(f)
                    ).add(g)
                )
            )
            .add(h),
            N()
            .add(
                N()
                .add(
                    default.add(N().add(a).add(b)).add(
                        p.add(default.add(default.add(c).add(e)).add(d)).add(f)
                    )
                )
                .add(g)
            )
            .add(h),
            N()
            .add(
                N()
                .add(default.add(N().add(a).add(b)).add(g))
                .add(p.add(default.add(default.add(c).add(e)).add(d)).add(f))
            )
            .add(h),
            N()
            .add(
                N()
                .add(N().add(a).add(b))
                .add(
                    default.add(
                        p.add(default.add(default.add(c).add(e)).add(d)).add(f)
                    ).add(g)
                )
            )
            .add(h),
            N()
            .add(
                N()
                .add(
                    default.add(N().add(a).add(b)).add(
                        p.add(default.add(c).add(default.add(d).add(e))).add(f)
                    )
                )
                .add(g)
            )
            .add(h),
            N()
            .add(
                N()
                .add(default.add(N().add(a).add(b)).add(g))
                .add(p.add(default.add(c).add(default.add(d).add(e))).add(f))
            )
            .add(h),
            N()
            .add(
                N()
                .add(N().add(a).add(b))
                .add(
                    default.add(
                        p.add(default.add(c).add(default.add(d).add(e))).add(f)
                    ).add(g)
                )
            )
            .add(h),
            N()
            .add(
                N()
                .add(
                    default.add(N().add(a).add(b)).add(
                        p.add(default.add(default.add(c).add(d)).add(f)).add(e)
                    )
                )
                .add(g)
            )
            .add(h),
            N()
            .add(
                N()
                .add(default.add(N().add(a).add(b)).add(g))
                .add(p.add(default.add(default.add(c).add(d)).add(f)).add(e))
            )
            .add(h),
            N()
            .add(
                N()
                .add(N().add(a).add(b))
                .add(
                    default.add(
                        p.add(default.add(default.add(c).add(d)).add(f)).add(e)
                    ).add(g)
                )
            )
            .add(h),
            N()
            .add(
                N()
                .add(
                    default.add(N().add(a).add(b)).add(
                        p.add(default.add(default.add(c).add(f)).add(d)).add(e)
                    )
                )
                .add(g)
            )
            .add(h),
            N()
            .add(
                N()
                .add(default.add(N().add(a).add(b)).add(g))
                .add(p.add(default.add(default.add(c).add(f)).add(d)).add(e))
            )
            .add(h),
            N()
            .add(
                N()
                .add(N().add(a).add(b))
                .add(
                    default.add(
                        p.add(default.add(default.add(c).add(f)).add(d)).add(e)
                    ).add(g)
                )
            )
            .add(h),
            N()
            .add(
                N()
                .add(
                    default.add(N().add(a).add(b)).add(
                        p.add(default.add(c).add(default.add(d).add(f))).add(e)
                    )
                )
                .add(g)
            )
            .add(h),
            N()
            .add(
                N()
                .add(default.add(N().add(a).add(b)).add(g))
                .add(p.add(default.add(c).add(default.add(d).add(f))).add(e))
            )
            .add(h),
            N()
            .add(
                N()
                .add(N().add(a).add(b))
                .add(
                    default.add(
                        p.add(default.add(c).add(default.add(d).add(f))).add(e)
                    ).add(g)
                )
            )
            .add(h),
            N()
            .add(
                N()
                .add(
                    default.add(N().add(a).add(b)).add(
                        p.add(default.add(c).add(d)).add(default.add(e).add(f))
                    )
                )
                .add(g)
            )
            .add(h),
            N()
            .add(
                N()
                .add(default.add(N().add(a).add(b)).add(g))
                .add(p.add(default.add(c).add(d)).add(default.add(e).add(f)))
            )
            .add(h),
            N()
            .add(
                N()
                .add(N().add(a).add(b))
                .add(
                    default.add(
                        p.add(default.add(c).add(d)).add(default.add(e).add(f))
                    ).add(g)
                )
            )
            .add(h),
            N()
            .add(
                N()
                .add(
                    default.add(N().add(a).add(b)).add(
                        p.add(default.add(default.add(c).add(e)).add(f)).add(d)
                    )
                )
                .add(g)
            )
            .add(h),
            N()
            .add(
                N()
                .add(default.add(N().add(a).add(b)).add(g))
                .add(p.add(default.add(default.add(c).add(e)).add(f)).add(d))
            )
            .add(h),
            N()
            .add(
                N()
                .add(N().add(a).add(b))
                .add(
                    default.add(
                        p.add(default.add(default.add(c).add(e)).add(f)).add(d)
                    ).add(g)
                )
            )
            .add(h),
            N()
            .add(
                N()
                .add(
                    default.add(N().add(a).add(b)).add(
                        p.add(default.add(default.add(c).add(f)).add(e)).add(d)
                    )
                )
                .add(g)
            )
            .add(h),
            N()
            .add(
                N()
                .add(default.add(N().add(a).add(b)).add(g))
                .add(p.add(default.add(default.add(c).add(f)).add(e)).add(d))
            )
            .add(h),
            N()
            .add(
                N()
                .add(N().add(a).add(b))
                .add(
                    default.add(
                        p.add(default.add(default.add(c).add(f)).add(e)).add(d)
                    ).add(g)
                )
            )
            .add(h),
            N()
            .add(
                N()
                .add(
                    default.add(N().add(a).add(b)).add(
                        p.add(default.add(c).add(default.add(e).add(f))).add(d)
                    )
                )
                .add(g)
            )
            .add(h),
            N()
            .add(
                N()
                .add(default.add(N().add(a).add(b)).add(g))
                .add(p.add(default.add(c).add(default.add(e).add(f))).add(d))
            )
            .add(h),
            N()
            .add(
                N()
                .add(N().add(a).add(b))
                .add(
                    default.add(
                        p.add(default.add(c).add(default.add(e).add(f))).add(d)
                    ).add(g)
                )
            )
            .add(h),
            N()
            .add(
                N()
                .add(
                    default.add(N().add(a).add(b)).add(
                        p.add(default.add(c).add(e)).add(default.add(d).add(f))
                    )
                )
                .add(g)
            )
            .add(h),
            N()
            .add(
                N()
                .add(default.add(N().add(a).add(b)).add(g))
                .add(p.add(default.add(c).add(e)).add(default.add(d).add(f)))
            )
            .add(h),
            N()
            .add(
                N()
                .add(N().add(a).add(b))
                .add(
                    default.add(
                        p.add(default.add(c).add(e)).add(default.add(d).add(f))
                    ).add(g)
                )
            )
            .add(h),
            N()
            .add(
                N()
                .add(
                    default.add(N().add(a).add(b)).add(
                        p.add(default.add(c).add(f)).add(default.add(d).add(e))
                    )
                )
                .add(g)
            )
            .add(h),
            N()
            .add(
                N()
                .add(default.add(N().add(a).add(b)).add(g))
                .add(p.add(default.add(c).add(f)).add(default.add(d).add(e)))
            )
            .add(h),
            N()
            .add(
                N()
                .add(N().add(a).add(b))
                .add(
                    default.add(
                        p.add(default.add(c).add(f)).add(default.add(d).add(e))
                    ).add(g)
                )
            )
            .add(h),
            N()
            .add(
                N()
                .add(
                    default.add(N().add(a).add(b)).add(
                        p.add(c).add(default.add(default.add(d).add(e)).add(f))
                    )
                )
                .add(g)
            )
            .add(h),
            N()
            .add(
                N()
                .add(default.add(N().add(a).add(b)).add(g))
                .add(p.add(c).add(default.add(default.add(d).add(e)).add(f)))
            )
            .add(h),
            N()
            .add(
                N()
                .add(N().add(a).add(b))
                .add(
                    default.add(
                        p.add(c).add(default.add(default.add(d).add(e)).add(f))
                    ).add(g)
                )
            )
            .add(h),
            N()
            .add(
                N()
                .add(
                    default.add(N().add(a).add(b)).add(
                        p.add(c).add(default.add(default.add(d).add(f)).add(e))
                    )
                )
                .add(g)
            )
            .add(h),
            N()
            .add(
                N()
                .add(default.add(N().add(a).add(b)).add(g))
                .add(p.add(c).add(default.add(default.add(d).add(f)).add(e)))
            )
            .add(h),
            N()
            .add(
                N()
                .add(N().add(a).add(b))
                .add(
                    default.add(
                        p.add(c).add(default.add(default.add(d).add(f)).add(e))
                    ).add(g)
                )
            )
            .add(h),
            N()
            .add(
                N()
                .add(
                    default.add(N().add(a).add(b)).add(
                        p.add(c).add(default.add(d).add(default.add(e).add(f)))
                    )
                )
                .add(g)
            )
            .add(h),
            N()
            .add(
                N()
                .add(default.add(N().add(a).add(b)).add(g))
                .add(p.add(c).add(default.add(d).add(default.add(e).add(f))))
            )
            .add(h),
            N()
            .add(
                N()
                .add(N().add(a).add(b))
                .add(
                    default.add(
                        p.add(c).add(default.add(d).add(default.add(e).add(f)))
                    ).add(g)
                )
            )
            .add(h),
        ],
    )
