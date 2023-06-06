from sowing.node import Node as N, Edge
from sowing import traversal
from sowing.comb.binarize import binarize_at, binarize
from math import factorial, prod
from itertools import product


a, b, c, d, e, f, g, h, p, r = map(N, "abcdefghpr")


def assert_iter_eq(iterable1, iterable2):
    assert list(iterable1) == list(iterable2)


def test_binarize_at_labeled():
    assert_iter_eq(binarize_at(N("abc")), [N("abc")])

    assert_iter_eq(
        binarize_at(N().extend(map(N, "ab"))),
        [N().extend(map(N, "ab"))],
    )

    assert_iter_eq(
        binarize_at(N().extend(map(N, "abc"))),
        [
            N().add(N().add(a).add(b)).add(c),
            N().add(N().add(a).add(c)).add(b),
            N().add(a).add(N().add(b).add(c)),
        ],
    )

    assert_iter_eq(
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
            assert set(traversal.leaves(tree)) == set(traversal.leaves(root))
            trees.add(tree)

        count = prod(range(2 * n - 3, 0, -2))
        assert len(trees) == count


def test_binarize_at_unlabeled():
    assert_iter_eq(binarize_at(N()), [N()])

    assert_iter_eq(
        binarize_at(N().extend((N() for _ in range(2)))),
        [N().extend((N() for _ in range(2)))],
    )

    assert_iter_eq(
        binarize_at(N().extend((N() for _ in range(3)))),
        [N().add(N().add(N()).add(N())).add(N())],
    )

    assert_iter_eq(
        binarize_at(N().extend((N() for _ in range(4)))),
        [
            N().add(N().add(N().add(N()).add(N())).add(N())).add(N()),
            N().add(N().add(N()).add(N())).add(N().add(N()).add(N())),
        ],
    )

    assert_iter_eq(
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
            assert set(traversal.leaves(tree)) == set(traversal.leaves(root))
            trees.add(tree)

        assert len(trees) == count


def test_binarize_at_multree():
    assert_iter_eq(
        binarize_at(N().add(a).add(a).add(b)),
        [
            N().add(N().add(a).add(a)).add(b),
            N().add(N().add(a).add(b)).add(a),
        ]
    )

    assert_iter_eq(
        binarize_at(N().add(a).add(b).add(b)),
        [
            N().add(N().add(a).add(b)).add(b),
            N().add(a).add(N().add(b).add(b)),
        ]
    )

    assert_iter_eq(
        binarize_at(N().add(a).add(a).add(b).add(b)),
        [
            N().add(N().add(N().add(a).add(a)).add(b)).add(b),
            N().add(N().add(N().add(a).add(b)).add(a)).add(b),
            N().add(N().add(a).add(a)).add(N().add(b).add(b)),
            N().add(N().add(N().add(a).add(b)).add(b)).add(a),
            N().add(N().add(a).add(N().add(b).add(b))).add(a),
            N().add(N().add(a).add(b)).add(N().add(a).add(b)),
        ]
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
                assert set(traversal.leaves(tree)) == set(traversal.leaves(root))
                trees.add(tree)

        assert len(trees) == count


def test_binarize():
    assert_iter_eq(binarize(N("abc")), [N("abc")])

    assert_iter_eq(binarize(a.add(b)), [a.add(b)])

    assert_iter_eq(
        binarize(a.add(b).add(c)),
        [a.add(b).add(c)],
    )

    assert_iter_eq(
        binarize(a.add(b).add(c).add(d)),
        [
            a.add(N().add(b).add(c)).add(d),
            a.add(N().add(b).add(d)).add(c),
            a.add(b).add(N().add(c).add(d)),
        ],
    )

    assert_iter_eq(
        binarize(a.add(b, "x").add(c, "y").add(d, "z")),
        [
            a.add(N().add(b, "x").add(c, "y")).add(d, "z"),
            a.add(N().add(b, "x").add(d, "z")).add(c, "y"),
            a.add(b, "x").add(N().add(c, "y").add(d, "z")),
        ],
    )

    assert_iter_eq(
        binarize(
            r.add(
                data="w",
                node=a.add(b, "x").add(c, "y").add(d, "z"),
            )
        ),
        [
            r.add(
                data="w",
                node=a.add(N().add(b, "x").add(c, "y")).add(d, "z"),
            ),
            r.add(
                data="w",
                node=a.add(N().add(b, "x").add(d, "z")).add(c, "y"),
            ),
            r.add(
                data="w",
                node=a.add(b, "x").add(N().add(c, "y").add(d, "z")),
            ),
        ],
    )

    assert_iter_eq(
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
