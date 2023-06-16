from sowing.node import Node
from sowing.zipper import Zipper
from sowing import traversal
from ..clade import Clade, Branch, Map


def quote_string(data: str) -> str:
    if any(char in "(),:;='\t\n" for char in data):
        return "'" + data.replace("'", "''") + "'"

    return data.replace(" ", "_")


def write_props(props: Map) -> str:
    return (
        "[&"
        + ",".join(
            f"{quote_string(str(key))}={quote_string(str(value))}"
            for key, value in sorted(props.items())
        )
        + "]"
    )


def write_node(cursor: Zipper[Clade | None, Branch | None]) -> Zipper[str, None]:
    node = cursor.node
    branch = cursor.data

    if node.edges:
        data = "(" + ",".join(edge.node.data for edge in node.edges) + ")"
    else:
        data = ""

    clade = node.data

    if isinstance(clade, Clade):
        data += quote_string(clade.name)

        if clade.props:
            data += write_props(clade.props)

    if isinstance(branch, Branch):
        if branch.length is not None or branch.props:
            data += ":"

        if branch.length is not None:
            data += f"{str(branch.length)}"

        if branch.props:
            data += write_props(branch.props)

    return cursor.replace(node=Node(data), data=None)


def write(root: Node[Clade | None, Branch | None]) -> str:
    """Encode a tree into a Newick string."""
    return traversal.fold(write_node, traversal.depth(root)).data + ";"
