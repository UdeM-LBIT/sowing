from random import Random
import time
from sowing.util.rangequery import RangeQuery


def test_min():
    data = [3, 1, 5, 3, 4, 7, 6, 1]
    rq_min = RangeQuery(data, min)
    rq_max = RangeQuery(data, max)

    for i in range(len(data)):
        for j in range(len(data)):
            if i < j:
                assert rq_min(i, j) == min(data[i:j])
                assert rq_max(i, j) == max(data[i:j])
            else:
                assert rq_min(i, j) is None
                assert rq_max(i, j) is None


def test_change_source():
    data = [8, 8, 8]
    rmq = RangeQuery(data, min)
    data[0] = 0

    for i in range(len(data)):
        for j in range(i + 1, len(data)):
            assert rmq(i, j) == 8


def _compute_all_naive(data, function):
    size = len(data)
    results = [[None] * size for _ in range(size)]

    for i in range(size):
        for j in range(i + 1, size):
            results[i][j] = function(data[i:j])

    return results


def _compute_all_rmq(data, function):
    size = len(data)
    results = [[None] * size for _ in range(size)]
    rmq = RangeQuery(data, function)

    for i in range(len(data)):
        for j in range(i + 1, len(data)):
            results[i][j] = rmq(i, j)

    return results


def test_faster():
    gen = Random(1337)
    size = 1_000
    data = gen.sample(range(100_000), size)

    naive_start = time.time()
    naive_results = _compute_all_naive(data, min)
    naive_dur = time.time() - naive_start

    rmq_start = time.time()
    rmq_results = _compute_all_rmq(data, min)
    rmq_dur = time.time() - rmq_start

    for i in range(len(data)):
        for j in range(i + 1, len(data)):
            assert naive_results[i][j] == rmq_results[i][j]

    print("Naive time:", naive_dur)
    print("RMQ time:", rmq_dur)
    assert rmq_dur < naive_dur
