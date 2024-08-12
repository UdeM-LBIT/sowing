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
        colon_props = []

        for key in ("length", "support", "probability"):
            if key in branch:
                colon_props.append(str(branch[key]))
                branch = branch.delete(key)
            else:
                colon_props.append("")

        while colon_props[-1] == "":
            colon_props.pop()

        other_props = write_props(branch)
        all_props = ":".join(colon_props) + other_props

        if all_props:
            data += ":" + all_props

    return cursor.replace(node=Node(data), data=None)


def write(root: Node[Map | None, Map | None]) -> str:
    """Encode a tree into a Newick string."""
    return traversal.fold(write_node, traversal.depth(root)).data + ";"
