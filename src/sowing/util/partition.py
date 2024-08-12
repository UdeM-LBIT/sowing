from typing import TypeVar, Generic, Iterable, Self, Generator
from itertools import chain, combinations
from copy import deepcopy


Item = TypeVar("Item")


def powerset(iterable: Iterable[Item]) -> Generator[tuple[Item], None, None]:
    """Generate all subsets of a given sequence."""
    seq = list(iterable)
    return chain.from_iterable(
        combinations(seq, r=size) for size in range(len(seq) + 1)
    )


def groupings(
    iterable: Iterable[Item], size: int = 0
) -> Generator[tuple[tuple[Item]], None, None]:
    """
    Generate all ways to partition a sequence of elements.

    :param iterable: sequence of elements to partition
    :param size: number of subsets in the generated partitions,
        or 0 to generate partitions of any size
    :yields: possible partitions, starting with the largest ones
    """
    seq = tuple(iterable)

    if not seq:
        if size <= 0:
            yield ()

        return

    if size == 1:
        yield (seq,)
        return

    for subset in powerset(seq[1:]):
        subset = (seq[0],) + subset

        for rest in groupings(
            iterable=(item for item in seq if item not in subset),
            size=size - 1,
        ):
            yield (subset, *rest)


class Partition(Generic[Item]):
    """Partition structure implementing the union-find strategy."""

    def __init__(self, items: Iterable[Item] = ()):
        """Create a partition in which each item is in its own set."""
        self._keys = {item: None for item in items}
        self._parent = {item: item for item in self._keys}
        self._rank = {item: 0 for item in self._parent}
        self._count = len(self._parent)

    def copy(self) -> Self:
        """Return a copy of the partition."""
        return deepcopy(self)

    def find(self, item: Item) -> Item:
        """
        Find the group to which an item belongs.

        :returns: a representing item for the group
        """
        root = item

        while self._parent[root] != root:
            root = self._parent[root]

        while item != root:
            item, self._parent[item] = self._parent[item], root

        return root

    def union(self, *items: Item) -> bool:
        """
        Merge items into the same group.

        :param item: any number of items to merge
        :returns: True if and only if at least one group was merged
        """
        merged = False

        if len(items) <= 1:
            return False

        for item2 in items[1:]:
            root1 = self.find(items[0])
            root2 = self.find(item2)

            if root1 == root2:
                continue

            if self._rank[root1] == self._rank[root2]:
                self._parent[root2] = root1
                self._rank[root1] += 1
                del self._keys[root2]

            elif self._rank[root1] > self._rank[root2]:
                self._parent[root2] = root1
                del self._keys[root2]

            else:
                self._parent[root1] = root2
                del self._keys[root1]

            self._count -= 1
            merged = True

        return merged

    def merge(self, size: int = 0) -> Generator[Self, None, None]:
        """
        Generate all possible ways to merge groups of this partition.

        The number of results for a complete partition of `n` elements
        is `B_n`, the n-th Bell number.

        :param size: number of groups in the generated partitions
        :yields: each possible merging
        """
        for grouping in groupings(list(self.keys()), size=size):
            merged = self.copy()

            for group in grouping:
                merged.union(*group)

            yield merged

    def keys(self) -> Iterable[Item]:
        """List the group representants of this partition."""
        return self._keys.keys()

    def values(self) -> Iterable[list[Item]]:
        """List the groups of this partition."""
        result = {key: [] for key in self._keys}

        for item in self._parent:
            result[self.find(item)].append(item)

        return result.values()

    def items(self) -> Iterable[tuple[Item, list[Item]]]:
        return zip(self.keys(), self.values())

    def __repr__(self) -> str:
        items = ", ".join(f"{key!r}: {value!r}" for key, value in self.items())
        return f"{self.__class__.__qualname__}({{{items}}})"

    def __len__(self) -> int:
        """Get the number of groups in this partition."""
        return self._count

    def __eq__(self, other: Self) -> bool:
        return dict(self.items()) == dict(other.items())
