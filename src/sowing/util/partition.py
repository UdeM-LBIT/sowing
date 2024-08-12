from collections import defaultdict
from typing import TypeVar, Generic, Iterable
from copy import deepcopy


Item = TypeVar("Item")


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
