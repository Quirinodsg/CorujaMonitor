"""
Lexer para o Sensor DSL — Coruja Monitor v3.0

Gramática suportada:
  sensor "name" [extends "template"] { field = value ... }

Tokens: SENSOR, EXTENDS, STRING, NUMBER, IDENTIFIER, LBRACE, RBRACE, EQUALS
Comentários: # linha, /* bloco */
"""
import re
from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    SENSOR = auto()
    EXTENDS = auto()
    STRING = auto()
    NUMBER = auto()
    IDENTIFIER = auto()
    LBRACE = auto()
    RBRACE = auto()
    EQUALS = auto()
    EOF = auto()


@dataclass
class Token:
    type: TokenType
    value: str
    line: int


class LexerError(Exception):
    def __init__(self, message: str, line: int):
        super().__init__(f"Linha {line}: {message}")
        self.line = line


class Lexer:
    """Tokenizador para o Sensor DSL."""

    def tokenize(self, source: str) -> list[Token]:
        tokens = []
        pos = 0
        line = 1
        source = self._strip_comments(source)

        while pos < len(source):
            # Pular whitespace
            if source[pos] in ' \t\r':
                pos += 1
                continue
            if source[pos] == '\n':
                line += 1
                pos += 1
                continue

            # String "..."
            if source[pos] == '"':
                end = source.find('"', pos + 1)
                if end == -1:
                    raise LexerError("String não fechada", line)
                value = source[pos+1:end]
                tokens.append(Token(TokenType.STRING, value, line))
                pos = end + 1
                continue

            # Número (int ou float)
            m = re.match(r'\d+(\.\d+)?', source[pos:])
            if m:
                num_str = m.group(0)
                tokens.append(Token(TokenType.NUMBER, num_str, line))
                pos += len(num_str)
                continue

            # Identificador ou keyword
            m = re.match(r'[a-zA-Z_][a-zA-Z0-9_]*', source[pos:])
            if m:
                word = m.group(0)
                if word == 'sensor':
                    tokens.append(Token(TokenType.SENSOR, word, line))
                elif word == 'extends':
                    tokens.append(Token(TokenType.EXTENDS, word, line))
                else:
                    tokens.append(Token(TokenType.IDENTIFIER, word, line))
                pos += len(word)
                continue

            # Símbolos
            if source[pos] == '{':
                tokens.append(Token(TokenType.LBRACE, '{', line))
                pos += 1
                continue
            if source[pos] == '}':
                tokens.append(Token(TokenType.RBRACE, '}', line))
                pos += 1
                continue
            if source[pos] == '=':
                tokens.append(Token(TokenType.EQUALS, '=', line))
                pos += 1
                continue

            raise LexerError(f"Caractere inesperado: '{source[pos]}'", line)

        tokens.append(Token(TokenType.EOF, '', line))
        return tokens

    def _strip_comments(self, source: str) -> str:
        """Remove comentários de linha (#) e bloco (/* */)."""
        # Bloco /* */
        result = re.sub(r'/\*.*?\*/', lambda m: '\n' * m.group(0).count('\n'), source, flags=re.DOTALL)
        # Linha #
        result = re.sub(r'#[^\n]*', '', result)
        return result
