from typing import Any, Iterator
from collections import deque
from enum import Enum, auto
from dataclasses import dataclass
from immutables import Map
from sowing.node import Node


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
    OpenParen = "("
    CloseParen = ")"

    OpenPropsNHX = "[&&NHX"
    OpenPropsBEAST = "[&"
    CloseProps = "]"

    Comma = ","
    Colon = ":"
    Semicolon = ";"
    Equals = "="

    String = "string"
    End = "end"


class PropStyle(Enum):
    """Lexer state for different existing notations for properties."""

    # Outside of any property block
    Normal = auto()

    # Properties using the New Hampshire eXtended (NHX) notation
    # <https://home.cc.umanitoba.ca/~psgendb/doc/atv/NHX.pdf>
    NHX = auto()

    # Properties using the BEAST notation
    # <https://beast.community/nexus_metacomments.html>
    BEAST = auto()


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


def _lex_whitespace(data: str, pos: int) -> int:
    """Advance past whitespace in a Newick string."""
    while pos < len(data) and data[pos] in WHITESPACE:
        pos += 1

    return pos


def _lex_comment(data: str, pos: int) -> int:
    """Advance past a comment in a Newick string."""
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

    return pos


def _lex_quoted_string(data: str, pos: int) -> tuple[Token, int]:
    """Extract a token for a string surrounded by single quotes."""
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

    end = pos + 1
    return Token(TokenKind.String, start, end, contents), end


def _lex_unquoted_string(data: str, state: PropStyle, pos: int) -> tuple[Token, int]:
    """Extract a token for a plain unquoted string."""
    start = pos
    contents = data[pos]
    pos += 1

    match state:
        case PropStyle.Normal:
            break_chars = "()[],:;' \t\n"

        case PropStyle.NHX:
            break_chars = "[]:= \t\n"

        case PropStyle.BEAST:
            break_chars = "[],= \t\n"

    while pos < len(data):
        cur = data[pos]

        if cur in break_chars:
            break

        if cur == "_":
            contents += " "
        else:
            contents += cur

        pos += 1

    return Token(TokenKind.String, start, pos, contents), pos


def tokenize(data: str) -> Iterator[Token]:
    """Tokenize a Newick string."""
    pos = 0
    state = PropStyle.Normal
    nhx_start = TokenKind.OpenPropsNHX
    beast_start = TokenKind.OpenPropsBEAST

    while (pos := _lex_whitespace(data, pos)) < len(data):
        cur = data[pos]

        match state:
            case PropStyle.Normal:
                token_chars = "(),:;"

            case PropStyle.NHX:
                token_chars = ":="

            case PropStyle.BEAST:
                token_chars = ",="

        if cur in token_chars:
            yield Token(TokenKind(cur), pos, pos + 1)
            pos += 1

        elif data[pos:].startswith(nhx_start.value):
            state = PropStyle.NHX
            yield Token(nhx_start, pos, pos + len(nhx_start.value))
            pos += len(nhx_start.value)

        elif data[pos:].startswith(beast_start.value):
            state = PropStyle.BEAST
            yield Token(beast_start, pos, pos + len(beast_start.value))
            pos += len(beast_start.value)

        elif cur == "]":
            if state == PropStyle.Normal:
                raise ParseError("unexpected ']'", pos, pos + 1)
            else:
                yield Token(TokenKind.CloseProps, pos, pos + 1)
                state = PropStyle.Normal
                pos += 1

        elif cur == "[":
            pos = _lex_comment(data, pos)

        elif cur == "'":
            token, pos = _lex_quoted_string(data, pos)
            yield token

        else:
            token, pos = _lex_unquoted_string(data, state, pos)
            yield token

    yield Token(TokenKind.End, pos, pos)


class TokenIterator:
    """Token iterator with pushback."""

    def __init__(self, iterator: Iterator):
        self.iterator = iterator
        self.buffer = deque()

    def __next__(self):
        if self.buffer:
            return self.buffer.popleft()

        return self.iterator.__next__()

    def push(self, token: Token) -> None:
        """Push a token back into the stream."""
        self.buffer.append(token)

    def skip(self, kind: TokenKind) -> None:
        """Skip over the next token if it is of given type."""
        token = next(self)

        if token.kind != kind:
            self.push(token)

    def expect(self, kind: TokenKind) -> Token:
        """Ensure the next token is of given type and return it."""
        token = next(self)

        if token.kind != kind:
            raise ParseError(
                f"expected '{kind.value}', not '{token.kind.value}'",
                token.start,
                token.end,
            )

        return token


class ParseState(Enum):
    """States for the Newick parser."""

    # At the beginning of a node, ready to read its children
    NodeStart = auto()

    # After a node’s children, ready to read its attached data
    NodeData = auto()

    # At the end of a tree, before the final semicolon
    Finish = auto()


def _parse_props_nhx(tokens: TokenIterator) -> Map:
    """Parse a block of Newick properties in NHX format."""
    result = {}

    while (token := next(tokens)).kind == TokenKind.Colon:
        key = tokens.expect(TokenKind.String).value
        tokens.expect(TokenKind.Equals)

        if (token := next(tokens)).kind == TokenKind.String:
            value = token.value
        else:
            tokens.push(token)
            value = ""

        result[key] = value

    tokens.push(token)
    tokens.expect(TokenKind.CloseProps)
    return Map(result)


def _parse_props_beast(tokens: TokenIterator) -> Map:
    """Parse a block of Newick properties in BEAST format."""
    result = {}

    while (token := next(tokens)).kind == TokenKind.String:
        key = token.value
        tokens.expect(TokenKind.Equals)

        if (token := next(tokens)).kind == TokenKind.String:
            value = token.value
        else:
            tokens.push(token)
            value = ""

        result[key] = value
        tokens.skip(TokenKind.Comma)

    tokens.push(token)
    tokens.expect(TokenKind.CloseProps)
    return Map(result)


def _parse_props(tokens: TokenIterator) -> tuple[Map]:
    """Parse a block of Newick properties."""
    match (start := next(tokens)).kind:
        case TokenKind.OpenPropsNHX:
            return _parse_props_nhx(tokens)

        case TokenKind.OpenPropsBEAST:
            return _parse_props_beast(tokens)

        case _:
            tokens.push(start)
            return Map()


def parse_chain(data: str) -> tuple[Node, int]:
    """
    Chainable parser for single trees encoded as Newick strings.

    :param data: input data stream
    :return: parsed tree and ending position in the string
    """
    nodes = []
    tokens = TokenIterator(tokenize(data))
    state = ParseState.NodeStart

    while state != ParseState.Finish:
        match state:
            case ParseState.NodeStart:
                # Start parsing a new node
                nodes.append(Node())

                if (token := next(tokens)).kind == TokenKind.OpenParen:
                    state = ParseState.NodeStart
                else:
                    tokens.push(token)
                    state = ParseState.NodeData

            case ParseState.NodeData:
                # Parse metadata attached to a node
                clade = Map()
                branch = Map()

                # Parse node label
                if (token := next(tokens)).kind == TokenKind.String:
                    clade = clade.set("name", token.value)
                else:
                    tokens.push(token)

                # Parse node props
                clade = clade.update(_parse_props(tokens))

                if (token := next(tokens)).kind == TokenKind.Colon:
                    # Parse branch length
                    if (token := next(tokens)).kind == TokenKind.String:
                        branch = branch.set("length", token.value)
                    else:
                        tokens.push(token)

                    # Parse branch props
                    branch = branch.update(_parse_props(tokens))
                else:
                    tokens.push(token)

                active = nodes.pop()
                active = active.replace(data=clade or None)

                if not nodes:
                    # Finished parsing the root node
                    state = ParseState.Finish
                    nodes.append(active)
                else:
                    # Attach parsed node to its parent
                    parent = nodes.pop()
                    nodes.append(parent.add(active, data=branch or None))

                    match (token := next(tokens)).kind:
                        case TokenKind.Comma:
                            state = ParseState.NodeStart

                        case TokenKind.CloseParen:
                            state = ParseState.NodeData

                        case _:
                            raise ParseError(
                                f"unexpected token '{token.kind.value}' after node",
                                token.start,
                                token.end,
                            )

    token = next(tokens)

    if token.kind != TokenKind.Semicolon:
        raise ParseError(
            f"expected ';' after end of tree, not '{token.kind.value}'",
            token.start,
            token.end,
        )

    return nodes.pop(), token.end


def parse(data: str) -> Node[Map, Map]:
    """Parse a single tree encoded as a Newick string."""
    node, pos = parse_chain(data)

    if data[pos:].strip(WHITESPACE):
        raise ParseError("unexpected garbage after end of tree", pos, len(data))

    return node


def parse_all(data: str) -> list[Node[Map, Map]]:
    """Parse a sequence of trees encoded as Newick strings."""
    result = []

    while data.strip(WHITESPACE):
        node, pos = parse_chain(data)
        result.append(node)
        data = data[pos:]

    return result
