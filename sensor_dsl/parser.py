"""
Parser recursivo descendente para o Sensor DSL — Coruja Monitor v3.0

Gramática BNF:
  program     ::= sensor_def*
  sensor_def  ::= 'sensor' STRING ('extends' STRING)? '{' field* '}'
  field       ::= IDENTIFIER '=' (STRING | NUMBER)
"""
from sensor_dsl.lexer import Token, TokenType, LexerError
from sensor_dsl.ast_nodes import SensorNode, FieldNode


class ParseError(Exception):
    def __init__(self, message: str, line: int):
        super().__init__(f"Linha {line}: {message}")
        self.line = line


class Parser:
    """Parser recursivo descendente para o Sensor DSL."""

    def __init__(self, tokens: list[Token]):
        self._tokens = tokens
        self._pos = 0

    def _current(self) -> Token:
        return self._tokens[self._pos]

    def _peek(self) -> Token:
        if self._pos + 1 < len(self._tokens):
            return self._tokens[self._pos + 1]
        return self._tokens[-1]

    def _consume(self, expected_type: TokenType = None) -> Token:
        token = self._current()
        if expected_type and token.type != expected_type:
            raise ParseError(
                f"Esperado {expected_type.name}, encontrado {token.type.name} ('{token.value}')",
                token.line,
            )
        self._pos += 1
        return token

    def parse(self) -> list[SensorNode]:
        """Parseia o programa completo e retorna lista de SensorNode."""
        sensors = []
        while self._current().type != TokenType.EOF:
            sensor = self._parse_sensor()
            sensors.append(sensor)
        return sensors

    def _parse_sensor(self) -> SensorNode:
        """sensor_def ::= 'sensor' STRING ('extends' STRING)? '{' field* '}'"""
        start_token = self._consume(TokenType.SENSOR)
        name_token = self._consume(TokenType.STRING)

        extends = None
        if self._current().type == TokenType.EXTENDS:
            self._consume(TokenType.EXTENDS)
            extends_token = self._consume(TokenType.STRING)
            extends = extends_token.value

        self._consume(TokenType.LBRACE)

        fields = []
        while self._current().type != TokenType.RBRACE:
            if self._current().type == TokenType.EOF:
                raise ParseError("Bloco sensor não fechado (falta '}')", start_token.line)
            field = self._parse_field()
            fields.append(field)

        self._consume(TokenType.RBRACE)

        return SensorNode(
            name=name_token.value,
            fields=fields,
            extends=extends,
            line=start_token.line,
        )

    def _parse_field(self) -> FieldNode:
        """field ::= IDENTIFIER '=' (STRING | NUMBER)"""
        name_token = self._consume(TokenType.IDENTIFIER)
        self._consume(TokenType.EQUALS)

        value_token = self._current()
        if value_token.type == TokenType.STRING:
            self._consume(TokenType.STRING)
            return FieldNode(name=name_token.value, value=value_token.value, line=name_token.line)
        elif value_token.type == TokenType.NUMBER:
            self._consume(TokenType.NUMBER)
            # Converter para int ou float
            num_str = value_token.value
            value = float(num_str) if '.' in num_str else int(num_str)
            return FieldNode(name=name_token.value, value=value, line=name_token.line)
        else:
            raise ParseError(
                f"Valor inválido para campo '{name_token.value}': "
                f"esperado STRING ou NUMBER, encontrado {value_token.type.name}",
                name_token.line,
            )
