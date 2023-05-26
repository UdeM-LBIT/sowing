from sowing.node import Node
from sowing.traversal import Order, traverse, mapnodes
from ..clade import Clade


def quote_string(data: str):
    if any(char in "(),:;'\t\n" for char in data):
        return "'" + data.replace("'", "''") + "'"

    return data.replace(" ", "_")


def write_node(node: Node) -> str:
    if node.children:
        data = "(" + ",".join(node.data for node in node.children) + ")"
    else:
        data = ""

    if isinstance(node.data, Clade):
        data += quote_string(node.data.name)

        if node.data.branch_length is not None:
            data += f":{str(node.data.branch_length)}"

    return Node(data)


def write(root: Node):
    """Encode a tree into a Newick string."""
    return mapnodes(write_node, traverse(root, Order.Post)).data + ";"
