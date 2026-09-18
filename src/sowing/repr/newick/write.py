from immutables import Map

from sowing import traversal
from sowing.node import Node
from sowing.zipper import Zipper


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


def write_node(
    cursor: Zipper[Map | None, Map | None],
    pretty: bool,
    indent: str,
) -> Zipper[str, None]:
    node = cursor.node
    branch = cursor.data
    indent *= cursor.depth

    if node.edges:
        children = (edge.node.data for edge in node.edges)

        if pretty:
            data = f"{indent}(\n{',\n'.join(children)}\n{indent})"
        else:
            data = "(" + ",".join(children) + ")"
    else:
        data = indent if pretty else ""

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


def write(
    root: Node[Map | None, Map | None],
    pretty: bool = False,
    indent: str = "  ",
) -> str:
    """
    Encode a tree into a Newick string.

    :param pretty: whether to print the tree with additional line breaks and
        whitespace to improve readability (default: False)
    :param indent: indentation string added to visually indicate nesting
        in pretty-print mode
    """
    raw_result = traversal.fold(
        lambda cursor: write_node(cursor, pretty, indent),
        traversal.depth(root),
    )
    return raw_result.data + ";"
