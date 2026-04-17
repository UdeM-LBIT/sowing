from collections.abc import Hashable, Sequence
from dataclasses import dataclass, replace
from typing import Any, Self, TypeVar, overload
from .node import Node
from .zipper import Zipper

NodeData = TypeVar("NodeData", bound=Hashable)
EdgeData = TypeVar("EdgeData", bound=Hashable)


@dataclass(frozen=True, slots=True)
class Hedge[NodeData, EdgeData](Sequence[Zipper[NodeData, EdgeData]]):
    """Ordered set of consecutive sibling trees."""

    cursor: Zipper[NodeData, EdgeData] = Zipper()
    """
    Zipper pointing on the root of the first tree in the hedge.
    The other elements of the hedge are the next siblings of that root.
    The zipper may be invalid if the hedge is empty.
    """

    breadth: int = 0
    """
    Total number of trees in the hedge, i.e., one more than the number
    of siblings of `cursor` to include in the hedge.
    """

    @classmethod
    def of(cls, *roots: Node[NodeData, EdgeData]) -> Self:
        """
        Create a hedge from a sequence of trees.

        When multiple trees are combined in a hedge, they are attached below a virtual
        node so that they can be represented inside a zipper.

        :param roots: sequence of trees to group as a hedge
        :returns: created hedge
        """
        if len(roots) == 0:
            return cls(cursor=Zipper(), breadth=0)
        if len(roots) == 1:
            return cls(cursor=roots[0].unzip(), breadth=1)
        else:
            forest = Node().extend(roots)
            return cls(cursor=forest.unzip().down(), breadth=len(roots))

    @overload
    def __getitem__(self, index: int) -> Zipper[NodeData, EdgeData]: ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[Zipper[NodeData, EdgeData]]: ...

    def __getitem__(self, index):
        """
        Retrieve a tree of the hedge or a subhedge.

        :param index: tree index or hedge slice
        :returns: resulting tree or hedge
        """
        if isinstance(index, int):
            if 0 <= index < self.breadth:
                return self.cursor.sibling(index)

            raise IndexError("index out of bounds")
        elif isinstance(index, slice):
            if index.start is not None:
                if not (0 <= index.start <= self.breadth):
                    raise IndexError("index out of bounds")

                self = replace(
                    self,
                    cursor=self.cursor.sibling(index.start),
                    breadth=self.breadth - index.start,
                )

            if index.stop is not None:
                breadth = index.stop - (index.start or 0)

                if not (0 <= breadth <= self.breadth):
                    raise IndexError("index out of bounds")

                self = replace(self, breadth=breadth)

            if index.step is not None:
                raise IndexError("unsupported step in slice")

            return self
        else:
            raise TypeError("invalid index type")

    def __eq__(self, other: Any) -> bool:
        """
        Test whether two objects represent the same hedge.

        Note that empty hedges always compare equal regardless of their cursor.
        """
        if not isinstance(other, Hedge):
            return NotImplemented

        if self.breadth == 0:
            return other.breadth == 0

        return self.breadth == other.breadth and self.cursor == other.cursor

    def __len__(self) -> int:
        """Get the number of trees in the hedge."""
        return self.breadth
