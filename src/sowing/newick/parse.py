from typing import Any, Iterator
from collections import deque
from ..net import Net
from enum import Enum, auto
from dataclasses import dataclass


class ParseError(Exception):
    """Parsing error with location information."""
    def __init__(self, message, start, end):
        if abs(start - end) <= 1:
            message = f"{message} (at position {start})"
        else:
            message = f"{message} (at range {start}-{end})"

        super().__init__(message)
        self.start = start
        self.end = end


class TokenKind(Enum):
    Open = "("
    Close = ")"

    Comma = ","
    Colon = ":"
    Semicolon = ";"

    String = "string"
    Comment = "comment"
    End = "end"


@dataclass(frozen=True)
class Token:
    """Token emitted by the lexer."""

    # Type of token
    kind: TokenKind

    # Token starting position in the data stream
    start: int

    # Position following the token end in the data stream
    end: int

    # Value associated with the token
    value: Any = None


# Class of characters that ignored by the lexer
WHITESPACE = " \t\n"


def tokenize(data: str) -> Iterator[Token]:
    """
    Lexer for the Newick format.

    :param data: input data stream
    :return: iterator emitting tokens
    """
    pos = 0

    while pos < len(data):
        # Skip over whitespace
        while pos < len(data) and data[pos] in WHITESPACE:
            pos += 1

        cur = data[pos]

        if cur in "(),:;":
            # Single-character token
            yield Token(TokenKind(cur), pos, pos + 1)
            pos += 1

        elif cur == "[":
            # Comment
            start = pos
            pos += 1
            depth = 1
            contents = "["

            while pos < len(data) and depth > 0:
                if data[pos] == "]":
                    depth -= 1
                elif data[pos] == "[":
                    depth += 1

                contents += data[pos]
                pos += 1

            if depth > 0:
                raise ParseError("unclosed comment", start, pos)

            yield Token(TokenKind.Comment, start, pos, contents)

        elif cur == "'":
            # Quoted string
            start = pos
            pos += 1
            contents = ""

            while pos < len(data):
                if data[pos] == "'":
                    if pos + 1 < len(data) and data[pos + 1] == "'":
                        contents += "'"
                        pos += 2
                    else:
                        break

                contents += data[pos]
                pos += 1

            if pos == len(data):
                raise ParseError("unclosed string", start, pos)

            yield Token(TokenKind.String, start, pos + 1, contents)
            pos += 1

        else:
            # Unquoted string
            start = pos
            pos += 1
            contents = cur

            while pos < len(data):
                if data[pos] in "()[],:;' \t\n":
                    break

                if data[pos] == "_":
                    contents += " "
                else:
                    contents += data[pos]

                pos += 1

            yield Token(TokenKind.String, start, pos, contents)

    yield Token(TokenKind.End, pos, pos)


class BufferedIterator:
    """Iterator wrapper that can accept back items after emitting them."""

    def __init__(self, iterator: Iterator):
        self.iterator = iterator
        self.buffer = deque()

    def __next__(self):
        if self.buffer:
            return self.buffer.popleft()

        return self.iterator.__next__()

    def push(self, item):
        """Push an item back into the stream."""
        self.buffer.append(item)


class ParseState(Enum):
    """States for the Newick parser."""

    # At the beginning of a node, ready to read its children
    NodeStart = auto()

    # After a node’s children, ready to read its attached data
    NodeData = auto()

    # At the end of a tree, before the final semicolon
    Finish = auto()


def parse_chain(data: str) -> tuple[Net, int]:
    """
    Chainable parser for single networks encoded as Newick strings.

    :param data: input data stream
    :return: parsed network and ending position
    """
    nodes = []
    tokens = BufferedIterator(tokenize(data))
    state = ParseState.NodeStart

    while state != ParseState.Finish:
        match state:
            case ParseState.NodeStart:
                # Start parsing a new node
                nodes.append(Net(""))

                match (token := next(tokens)).kind:
                    case TokenKind.Open:
                        state = ParseState.NodeStart

                    case _:
                        tokens.push(token)
                        state = ParseState.NodeData

            case ParseState.NodeData:
                # Parse metadata attached to a node
                active = nodes.pop()
                length = None

                # Parse node label
                match (token := next(tokens)).kind:
                    case TokenKind.String:
                        active = active.label(token.value)

                    case _:
                        tokens.push(token)

                # Parse branch length
                match (token := next(tokens)).kind:
                    case TokenKind.Colon:
                        token = next(tokens)

                        if token.kind != TokenKind.String:
                            raise ParseError(
                                "expected branch length value after ':', "
                                f"not '{token.kind.value}'",
                                token.start, token.end,
                            )

                        try:
                            length = float(token.value)
                        except ValueError:
                            raise ParseError(
                                "invalid branch length value",
                                token.start, token.end
                            )

                    case _:
                        tokens.push(token)

                # Parse comment
                match (token := next(tokens)).kind:
                    case TokenKind.Comment:
                        pass

                    case _:
                        tokens.push(token)

                if not nodes:
                    # Finished parsing the root node
                    state = ParseState.Finish
                    nodes.append(active)
                else:
                    # Attach parsed node to its parent
                    parent = nodes.pop()
                    nodes.append(parent.add(active, length))

                    match (token := next(tokens)).kind:
                        case TokenKind.Comma:
                            state = ParseState.NodeStart

                        case TokenKind.Close:
                            state = ParseState.NodeData

                        case _:
                            raise ParseError(
                                f"unexpected token '{token.kind.value}' "
                                "after node",
                                token.start, token.end,
                            )

    token = next(tokens)

    if token.kind != TokenKind.Semicolon:
        raise ParseError(
            f"expected ';' after end of tree, not '{token.kind.value}'",
            token.start, token.end,
        )

    return nodes.pop(), token.end


def parse(data: str) -> Net:
    """Parse a single network encoded as a Newick string."""
    net, pos = parse_chain(data)

    if data[pos:].strip(WHITESPACE):
        raise ParseError(
            "unexpected garbage after end of tree",
            pos, len(data)
        )

    return net


def parse_all(data: str) -> list[Net]:
    """Parse a sequence of networks encoded as Newick strings."""
    result = []

    while data.strip(WHITESPACE):
        net, pos = parse_chain(data)
        result.append(net)
        data = data[pos:]

    return result
