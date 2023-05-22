from ..net import Net, Order


def write_edge(edge):
    child, length = edge

    if length is None:
        return child.data

    return f"{child.data}:{str(length)}"


def write_string(data: str):
    if any(char in "(),:;'\t\n" for char in data):
        return "'" + data.replace("'", "''") + "'"

    return data.replace(" ", "_")


def write_node(node: Net):
    if node.children:
        children = "(" + ",".join(map(write_edge, node.children)) + ")"
    else:
        children = ""

    return Net(children + write_string(node.data))


def write(net: Net):
    """Encode a network into a Newick string."""
    return net.map(write_node, Order.Post).data + ";"
