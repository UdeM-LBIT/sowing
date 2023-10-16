from immutables import Map
from sowing.node import Node
from sowing.zipper import Zipper
from sowing import traversal


def quote_string(data: str) -> str:
    if any(char in "_[](),:;='\t\n" for char in data):
        return "'" + data.replace("'", "''") + "'"

    return data.replace(" ", "_")


def write_props(props: Map) -> str:
    if not props:
        return ""

    return (
        "[&"
        + ",".join(
            f"{quote_string(str(key))}={quote_string(str(value))}"
            for key, value in sorted(props.items())
        )
        + "]"
    )


def write_node(cursor: Zipper[Map | None, Map | None]) -> Zipper[str, None]:
    node = cursor.node
    branch = cursor.data

    if node.edges:
        data = "(" + ",".join(edge.node.data for edge in node.edges) + ")"
    else:
        data = ""

    clade = node.data

    if isinstance(clade, Map):
        if "name" in clade:
            data += quote_string(clade["name"])
            clade = clade.delete("name")

        data += write_props(clade)

    if isinstance(branch, Map) and branch:
        data += ":"

        if "length" in branch:
            data += f"{branch['length']}"
            branch = branch.delete("length")

        data += write_props(branch)

    return cursor.replace(node=Node(data), data=None)


def write(root: Node[Map | None, Map | None]) -> str:
    """Encode a tree into a Newick string."""
    return traversal.fold(write_node, traversal.depth(root)).data + ";"
