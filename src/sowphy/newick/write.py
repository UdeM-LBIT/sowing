from sowing.node import Node
from sowing.traversal import Order, traverse, maptree


def map_string(data: str):
    if any(char in "(),:;'\t\n" for char in data):
        return "'" + data.replace("'", "''") + "'"

    return data.replace(" ", "_")


def map_node(node: Node):
    if node.children:
        data = "(" + ",".join(node.data for node in node.children) + ")"
    else:
        data = ""

    data += map_string(node.data.name)

    if node.data.branch_length is not None:
        data += f":{str(node.data.branch_length)}"

    return Node(data)


def write(root: Node):
    """Encode a tree into a Newick string."""
    return maptree(map_node, traverse(root, Order.Post)).data + ";"