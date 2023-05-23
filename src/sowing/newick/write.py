from ..net import Net
from ..traversal import Order, traverse, transform


def map_edge(edge):
    child, length = edge

    if length is None:
        return child.data

    return f"{child.data}:{str(length)}"


def map_string(data: str):
    if any(char in "(),:;'\t\n" for char in data):
        return "'" + data.replace("'", "''") + "'"

    return data.replace(" ", "_")


def map_node(node: Net, _):
    if node.children:
        children = "(" + ",".join(map(map_edge, node.children)) + ")"
    else:
        children = ""

    return Net(children + map_string(node.data)), _


def write(net: Net):
    """Encode a network into a Newick string."""
    return transform(map_node, traverse(net, Order.Post)).data + ";"
