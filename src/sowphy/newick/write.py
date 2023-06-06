from sowing.node import Node
from sowing.traversal import Order, traverse, mapnodes
from ..clade import Clade, Branch


def quote_string(data: str) -> str:
    if any(char in "(),:;'\t\n" for char in data):
        return "'" + data.replace("'", "''") + "'"

    return data.replace(" ", "_")


def write_node(node: Node, branch: Branch | None) -> tuple[Node, None]:
    if node.edges:
        data = "(" + ",".join(edge.node.data for edge in node.edges) + ")"
    else:
        data = ""

    clade = node.data

    if isinstance(clade, Clade):
        data += quote_string(clade.name)

    if isinstance(branch, Branch):
        if branch.length is not None:
            data += f":{str(branch.length)}"

    return Node(data), None


def write(root: Node) -> str:
    """Encode a tree into a Newick string."""
    return mapnodes(write_node, traverse(root, Order.Post)).data + ";"
