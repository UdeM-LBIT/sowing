from collections.abc import Mapping, Callable
from sowing.node import Node
from sowing import traversal

escape_rules = str.maketrans({'"': r"\""})
Style = Mapping[str, str]


def serialize_keyval(key: str, value: str) -> str:
    return f'{key}="{value.translate(escape_rules)}"'


def serialize_style(style: Style) -> str:
    if style:
        return (
            " ["
            + ", ".join(serialize_keyval(key, val) for key, val in style.items())
            + "]"
        )
    else:
        return ""


def serialize_props(style: Style) -> list[str]:
    return [serialize_keyval(key, val) + ";" for key, val in style.items()]


def default_node_style[NodeData](data: NodeData) -> Style:
    return {"shape": "box", "style": "rounded", "label": str(data) if data else ""}


def default_edge_style[EdgeData](data: EdgeData) -> Style:
    if data:
        return {"label": str(data)}
    else:
        return {}


def write[NodeData, EdgeData](
    root: Node[NodeData, EdgeData],
    node_style: Callable[[NodeData], Style] = default_node_style,
    edge_style: Callable[[EdgeData], Style] = default_edge_style,
    graph_style: Style = {},
):
    """
    Represent a graph in the DOT format.

    :param root: graph to be represented
    :param node_style: mapping from node data to a dictionary of GraphViz attributes to
        assign to the node (see <https://graphviz.org/docs/nodes/> for possible values)
    :param edge_style: mapping from edge data to a dictionary of GraphViz attributes to
        assign to the edge (see <https://graphviz.org/docs/edges/> for possible values)
    :param graph_style: dictionary of GraphViz attributes for the whole graph
        (see <https://graphviz.org/docs/graph/> for possible values)
    :return: DOT-formatted string representing the graph
    """
    # Assign a unique sequential ID to each node
    ids: dict[int, int] = {}

    def seq_id(node: Node) -> int:
        if id(node) not in ids:
            ids[id(node)] = len(ids)

        return ids[id(node)]

    lines = ["digraph {"]
    lines.extend(serialize_props(graph_style))

    # Traverse the graph, skipping repeated subtrees
    for cursor in traversal.depth(root, preorder=True, unique="id"):
        source = cursor.node
        assert source is not None

        lines.append(f"{seq_id(source)}{serialize_style(node_style(source.data))}")

        for edge in source.edges:
            target = edge.node
            lines.append(
                f"{seq_id(source)} -> {seq_id(target)}{serialize_style(edge_style(edge.data))}"
            )

    lines.append("}")
    return "\n".join(lines)
