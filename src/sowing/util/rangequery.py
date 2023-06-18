def _ilog2(value: int):
    """Integral part of the base-2 logarithm of a positive integer."""
    return value.bit_length() - 1


class RangeQuery:
    """
    Structure for fast computation of indempotent functions on ranges.

    For an input list of N elements, this structure can compute the
    value of any idempotent function (min, max) on any range of the list
    in constant time.

    The structure does not take changes in the input list after
    initialization into account.

    See <https://cp-algorithms.com/data_structures/sparse-table.html>.
    """

    __slots__ = ["sparse_table", "function"]

    def __init__(self, data, function=min):
        """
        Pre-compute the sparse table for range queries.

        Complexity: O(N × log(N)), where N = len(data).

        :param data: input list of objects
        :param function: binary idempotent function to compute
        """
        length = len(data)
        levels = _ilog2(length) + 1

        # sparse_table[depth][i] stores the value of the function
        # on the (i, i + 2**depth) range
        self.sparse_table = [[None] * length for _ in range(levels)]

        if levels > 0:
            self.sparse_table[0] = list(data)

            for depth in range(1, levels):
                for i in range(length - 2**depth + 1):
                    left = self.sparse_table[depth - 1][i]
                    assert left is not None
                    right = self.sparse_table[depth - 1][i + 2 ** (depth - 1)]
                    assert right is not None
                    self.sparse_table[depth][i] = function(left, right)

        self.function = function

    def __call__(self, start: int, stop: int):
        """
        Compute the value of the function on a range.

        Complexity: O(1).

        :param start: first index of the range
        :param stop: index following the last index of the range
        :returns: computed value, or None if the range is empty
        """
        if start >= stop:
            return None

        depth = _ilog2(stop - start)
        return self.function(
            self.sparse_table[depth][start],
            self.sparse_table[depth][stop - 2**depth],
        )
