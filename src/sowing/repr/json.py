from typing import Any, Callable, Hashable, TypeVar
from json import JSONEncoder
from ..node import Node, Edge


NodeData = TypeVar("NodeData", bound=Hashable)
EdgeData = TypeVar("EdgeData", bound=Hashable)


class TreeEncoder(JSONEncoder):
    def default(self, value):
        match value:
            case Node(data, edges):
                return {"edges": edges, "data": data}

            case Edge(node, data):
                return {"node": node, "data": data}

        return super().default(value)


def passthrough(value):
    return value


def tree_decoder(
    value: dict,
    node_decoder: Callable[[Any], NodeData] = passthrough,
    edge_decoder: Callable[[Any], EdgeData] = passthrough,
) -> Node[NodeData, EdgeData] | Edge[NodeData, EdgeData]:
    if not isinstance(value, dict):
        raise TypeError("value must be a dict, got {type(value)}")

    if "edges" in value:
        if not isinstance(value["edges"], list):
            raise TypeError("node edges must be a list, got {type(value['edges'])}")

        return Node(
            edges=tuple(
                tree_decoder(item, node_decoder, edge_decoder)
                for item in value["edges"]
            ),
            data=node_decoder(value.get("data")),
        )

    if "node" in value:
        return Edge(
            node=tree_decoder(value["node"], node_decoder, edge_decoder),
            data=edge_decoder(value.get("data")),
        )

    raise TypeError(
        "value is neither a node with an 'edges' key nor"
        f" an edge with a 'node' key; got keys {list(value.keys())}"
    )
