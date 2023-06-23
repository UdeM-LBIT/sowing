from sowing.node import Node
from sowing.repr.json import TreeEncoder, tree_decoder
from json import dumps, loads
import pytest


class _Test:
    def __eq__(self, other):
        return isinstance(other, _Test)

    def __hash__(self):
        return 0


def _test_decoder(value):
    if value == "test!":
        return _Test()

    return None


class _TestEncoder(TreeEncoder):
    def default(self, value):
        if value == _Test():
            return "test!"

        return super().default(value)


def test_plain_encode():
    assert dumps(Node(), cls=TreeEncoder) == dumps({"edges": [], "data": None})
    assert dumps(Node(8), cls=TreeEncoder) == dumps({"edges": [], "data": 8})

    assert dumps(
        Node("a").add(Node("b")).add(Node("c")),
        cls=TreeEncoder,
    ) == dumps(
        {
            "edges": [
                {"node": {"edges": [], "data": "b"}, "data": None},
                {"node": {"edges": [], "data": "c"}, "data": None},
            ],
            "data": "a",
        }
    )

    assert dumps(
        Node("a").add(Node("b"), data=1).add(Node("c"), data=2),
        cls=TreeEncoder,
    ) == dumps(
        {
            "edges": [
                {"node": {"edges": [], "data": "b"}, "data": 1},
                {"node": {"edges": [], "data": "c"}, "data": 2},
            ],
            "data": "a",
        }
    )


def test_plain_decode():
    assert tree_decoder(loads('{"data": null, "edges": []}')) == Node()
    assert tree_decoder(loads('{"edges": []}')) == Node()
    assert tree_decoder(loads('{"data": 8, "edges": []}')) == Node(8)

    with pytest.raises(TypeError) as err:
        tree_decoder(loads('{"invalid": "object"}'))

    assert (
        "value is neither a node with an 'edges' key nor an"
        " edge with a 'node' key; got keys ['invalid']" in str(err.value)
    )

    assert tree_decoder(
        loads(
            '{"data": "a", "edges": ['
            '{"node": {"data": "b", "edges": []}, "data": null},'
            '{"node": {"data": "c", "edges": []}, "data": null}'
            "]}"
        )
    ) == Node("a").add(Node("b")).add(Node("c"))

    assert tree_decoder(
        loads(
            '{"data": "a", "edges": ['
            '{"node": {"data": "b", "edges": []}},'
            '{"node": {"data": "c", "edges": []}}'
            "]}"
        )
    ) == Node("a").add(Node("b")).add(Node("c"))

    assert tree_decoder(
        loads(
            '{"data": "a", "edges": ['
            '{"node": {"data": "b", "edges": []}, "data": 1},'
            '{"node": {"data": "c", "edges": []}, "data": 2}'
            "]}"
        )
    ) == Node("a").add(Node("b"), data=1).add(Node("c"), data=2)


def test_complex_encode():
    with pytest.raises(TypeError) as err:
        dumps(Node(_Test()), cls=TreeEncoder)

    assert "Object of type _Test is not JSON serializable" in str(err.value)

    assert dumps(
        Node(_Test()),
        cls=_TestEncoder,
    ) == dumps({"edges": [], "data": "test!"})

    assert dumps(
        Node(_Test()).add(Node(_Test()), data=_Test()),
        cls=_TestEncoder,
    ) == dumps(
        {
            "edges": [{"node": {"edges": [], "data": "test!"}, "data": "test!"}],
            "data": "test!",
        }
    )


def test_complex_decode():
    assert tree_decoder(
        loads('{"data": "test!", "edges": []}'),
        node_decoder=_test_decoder,
    ) == Node(_Test())

    assert tree_decoder(
        loads(
            '{"data": "test!", "edges": ['
            '{"node": {"data": "test!", "edges": []}, "data": "test!"}]}'
        ),
        node_decoder=_test_decoder,
        edge_decoder=_test_decoder,
    ) == Node(_Test()).add(Node(_Test()), data=_Test())
