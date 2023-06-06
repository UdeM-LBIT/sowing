from collections import defaultdict
from typing import TypeVar, Generic, Iterable


Item = TypeVar("Item")


class Partition(Generic[Item]):
    """Partition structure implementing the union-find strategy."""

    def __init__(self, items: Iterable[Item]):
        """Create a partition in which each item is in its own set."""
        self._parent = {item: item for item in items}
        self._rank = {item: 0 for item in self._parent}
        self._count = len(self._parent)

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

        if not items:
            return False

        root1 = self.find(items[0])

        for item2 in items:
            root2 = self.find(item2)

            if root1 == root2:
                continue

            if self._rank[root1] == self._rank[root2]:
                self._parent[root2] = root1
                self._rank[root1] += 1

            elif self._rank[root1] > self._rank[root2]:
                self._parent[root2] = root1

            else:
                self._parent[root1] = root2

            self._count -= 1
            merged = True

        return merged

    def groups(self) -> list[list[Item]]:
        """List the groups of this partition."""
        result = defaultdict(list)

        for item in self._parent:
            result[self.find(item)].append(item)

        return list(result.values())

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}({self.groups()!r})"

    def __len__(self) -> int:
        """Get the number of groups in this partition."""
        return self._count
