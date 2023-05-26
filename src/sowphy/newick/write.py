from sowing.node import Node, Zipper
from sowing.traversal import Order, traverse, maptree
from ..clade import Clade, Branch


def quote_string(data: str):
    if any(char in "(),:;'\t\n" for char in data):
        return "'" + data.replace("'", "''") + "'"

    return data.replace(" ", "_")


def write_node(cursor: Zipper) -> str:
    node = cursor.node

    if node.edges:
        data = "(" + ",".join(edge.node.data for edge in node.edges) + ")"
    else:
        data = ""

    if isinstance(node.data, Clade):
        data += quote_string(node.data.name)

    if isinstance(cursor.data, Branch):
        if cursor.data.length is not None:
            data += f":{str(cursor.data.length)}"

    return cursor.replace(node=Node(data), data=None)


def write(root: Node):
    """Encode a tree into a Newick string."""
    return maptree(write_node, traverse(root, Order.Post)).data + ";"
