"""
Unit tests for Sensor DSL — Coruja Monitor v3.0
Tests: Lexer tokenization, Parser SensorNode, template inheritance,
       syntax errors (DSLSyntaxError), invalid protocol, comment removal.
Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7
"""
import pytest

from sensor_dsl.lexer import Lexer, LexerError, TokenType
from sensor_dsl.parser import Parser, ParseError
from sensor_dsl.ast_nodes import SensorNode, FieldNode
from sensor_dsl.compiler import DSLCompiler, DSLSyntaxError
from sensor_dsl.printer import DSLPrinter
from core.spec.enums import Protocol


# ---------------------------------------------------------------------------
# Lexer — tokenization
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestLexer:
    """Req 9.2 — correct tokenization of keywords, strings, numbers, symbols."""

    def test_tokenize_simple_sensor(self):
        source = 'sensor "cpu_usage" { protocol = "wmi" interval = 60 }'
        tokens = Lexer().tokenize(source)
        types = [t.type for t in tokens]
        assert TokenType.SENSOR in types
        assert TokenType.STRING in types
        assert TokenType.LBRACE in types
        assert TokenType.RBRACE in types
        assert TokenType.IDENTIFIER in types
        assert TokenType.EQUALS in types
        assert TokenType.NUMBER in types
        assert types[-1] == TokenType.EOF

    def test_tokenize_extends_keyword(self):
        source = 'sensor "child" extends "parent" { protocol = "snmp" interval = 30 }'
        tokens = Lexer().tokenize(source)
        types = [t.type for t in tokens]
        assert TokenType.EXTENDS in types

    def test_tokenize_float_number(self):
        source = 'sensor "s" { protocol = "wmi" interval = 60 warning = 80.5 }'
        tokens = Lexer().tokenize(source)
        number_tokens = [t for t in tokens if t.type == TokenType.NUMBER]
        values = [t.value for t in number_tokens]
        assert "80.5" in values

    def test_unclosed_string_raises_error(self):
        source = 'sensor "unclosed'
        with pytest.raises(LexerError):
            Lexer().tokenize(source)

    def test_unexpected_character_raises_error(self):
        source = 'sensor "s" { protocol = "wmi" interval = 60 @ }'
        with pytest.raises(LexerError):
            Lexer().tokenize(source)


# ---------------------------------------------------------------------------
# Parser — SensorNode
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestParser:
    """Req 9.3 — correct SensorNode with required and optional fields."""

    def test_parse_simple_sensor(self):
        source = 'sensor "cpu" { protocol = "wmi" interval = 60 }'
        tokens = Lexer().tokenize(source)
        nodes = Parser(tokens).parse()
        assert len(nodes) == 1
        assert nodes[0].name == "cpu"
        assert nodes[0].extends is None
        assert len(nodes[0].fields) == 2

    def test_parse_sensor_with_extends(self):
        source = 'sensor "child" extends "base_tmpl" { protocol = "snmp" interval = 30 }'
        tokens = Lexer().tokenize(source)
        nodes = Parser(tokens).parse()
        assert nodes[0].extends == "base_tmpl"

    def test_parse_multiple_sensors(self):
        source = '''
        sensor "a" { protocol = "wmi" interval = 60 }
        sensor "b" { protocol = "snmp" interval = 30 }
        '''
        tokens = Lexer().tokenize(source)
        nodes = Parser(tokens).parse()
        assert len(nodes) == 2

    def test_unclosed_block_raises_error(self):
        source = 'sensor "broken" { protocol = "wmi"'
        tokens = Lexer().tokenize(source)
        with pytest.raises(ParseError):
            Parser(tokens).parse()

    def test_field_values_extracted(self):
        source = 'sensor "s" { protocol = "wmi" interval = 120 warning = 80 }'
        tokens = Lexer().tokenize(source)
        nodes = Parser(tokens).parse()
        fields = {f.name: f.value for f in nodes[0].fields}
        assert fields["protocol"] == "wmi"
        assert fields["interval"] == 120
        assert fields["warning"] == 80


# ---------------------------------------------------------------------------
# Template inheritance
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestTemplateInheritance:
    """Req 9.4 — sensor extends template inherits and overrides fields."""

    def test_inherits_template_fields(self):
        template_node = SensorNode(
            name="base",
            fields=[
                FieldNode(name="protocol", value="wmi"),
                FieldNode(name="interval", value=60),
                FieldNode(name="timeout", value=45),
            ],
        )
        compiler = DSLCompiler(templates={"base": template_node})
        source = 'sensor "child" extends "base" { warning = 80 critical = 95 }'
        sensors = compiler.compile(source)
        assert len(sensors) == 1
        s = sensors[0]
        assert s.protocol in (Protocol.WMI, "wmi")
        assert s.interval == 60
        assert s.timeout == 45
        assert s.thresholds["warning"] == 80.0
        assert s.thresholds["critical"] == 95.0

    def test_child_overrides_template_field(self):
        template_node = SensorNode(
            name="base",
            fields=[
                FieldNode(name="protocol", value="wmi"),
                FieldNode(name="interval", value=60),
                FieldNode(name="timeout", value=30),
            ],
        )
        compiler = DSLCompiler(templates={"base": template_node})
        source = 'sensor "child" extends "base" { interval = 120 }'
        sensors = compiler.compile(source)
        assert sensors[0].interval == 120

    def test_missing_template_raises_error(self):
        compiler = DSLCompiler(templates={})
        source = 'sensor "child" extends "nonexistent" { protocol = "wmi" interval = 60 }'
        with pytest.raises(DSLSyntaxError):
            compiler.compile(source)


# ---------------------------------------------------------------------------
# Syntax errors (DSLSyntaxError)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestSyntaxErrors:
    """Req 9.5 — DSLSyntaxError with line and field info."""

    def test_missing_required_field(self):
        compiler = DSLCompiler()
        source = 'sensor "s" { protocol = "wmi" }'  # missing interval
        with pytest.raises(DSLSyntaxError) as exc_info:
            compiler.compile(source)
        assert "interval" in str(exc_info.value)

    def test_missing_protocol(self):
        compiler = DSLCompiler()
        source = 'sensor "s" { interval = 60 }'
        with pytest.raises(DSLSyntaxError) as exc_info:
            compiler.compile(source)
        assert "protocol" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Invalid protocol
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestInvalidProtocol:
    """Req 9.5, 9.6 — invalid protocol raises DSLSyntaxError listing valid ones."""

    def test_invalid_protocol_rejected(self):
        compiler = DSLCompiler()
        source = 'sensor "s" { protocol = "ftp" interval = 60 }'
        with pytest.raises(DSLSyntaxError) as exc_info:
            compiler.compile(source)
        err_msg = str(exc_info.value)
        assert "protocol" in err_msg.lower()
        # Should list valid protocols
        assert "wmi" in err_msg or "snmp" in err_msg

    def test_valid_protocols_accepted(self):
        compiler = DSLCompiler()
        for proto in ["wmi", "snmp", "icmp", "tcp", "http"]:
            source = f'sensor "s_{proto}" {{ protocol = "{proto}" interval = 60 }}'
            sensors = compiler.compile(source)
            assert len(sensors) == 1


# ---------------------------------------------------------------------------
# Comment removal
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestCommentRemoval:
    """Req 9.7 — line (#) and block (/* */) comments removed by Lexer."""

    def test_line_comment_removed(self):
        source = '''
        # This is a comment
        sensor "s" {
            protocol = "wmi"  # inline comment
            interval = 60
        }
        '''
        compiler = DSLCompiler()
        sensors = compiler.compile(source)
        assert len(sensors) == 1
        assert sensors[0].interval == 60

    def test_block_comment_removed(self):
        source = '''
        /* Multi-line
           block comment */
        sensor "s" {
            protocol = "snmp"
            interval = 30
        }
        '''
        compiler = DSLCompiler()
        sensors = compiler.compile(source)
        assert len(sensors) == 1

    def test_comments_dont_affect_compilation(self):
        source_clean = 'sensor "s" { protocol = "wmi" interval = 60 warning = 80 critical = 95 }'
        source_commented = '''
        # header comment
        sensor "s" {
            protocol = "wmi"   # protocol
            interval = 60      # interval
            /* threshold block */
            warning = 80
            critical = 95
        }
        '''
        compiler = DSLCompiler()
        clean = compiler.compile(source_clean)
        commented = compiler.compile(source_commented)
        assert clean[0].protocol == commented[0].protocol
        assert clean[0].interval == commented[0].interval
        assert clean[0].thresholds == commented[0].thresholds
