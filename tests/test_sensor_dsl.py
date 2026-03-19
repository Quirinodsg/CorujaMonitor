"""
Testes para Sensor DSL — Coruja Monitor v3.0
Properties 18-19 + testes unitários
"""
import pytest
from sensor_dsl.lexer import Lexer, LexerError
from sensor_dsl.parser import Parser, ParseError
from sensor_dsl.compiler import DSLCompiler, DSLSyntaxError
from sensor_dsl.printer import DSLPrinter
from sensor_dsl.ast_nodes import SensorNode, FieldNode
from core.spec.enums import Protocol


# ─── Helpers ────────────────────────────────────────────────────────────────

def compile_dsl(source: str):
    return DSLCompiler().compile(source)


def roundtrip(source: str):
    """parse → print → parse"""
    compiler = DSLCompiler()
    printer = DSLPrinter()
    sensors1 = compiler.compile(source)
    printed = printer.print_all(sensors1)
    sensors2 = compiler.compile(printed)
    return sensors1, sensors2


# ─── Property 18: DSL round-trip ────────────────────────────────────────────

class TestDSLRoundtrip:
    def test_roundtrip_simple_sensor(self):
        src = '''
        sensor "cpu_check" {
            protocol = "wmi"
            interval = 60
        }
        '''
        s1, s2 = roundtrip(src)
        assert len(s1) == len(s2) == 1
        assert s1[0].protocol == s2[0].protocol
        assert s1[0].interval == s2[0].interval
        assert s1[0].type == s2[0].type

    def test_roundtrip_with_thresholds(self):
        src = '''
        sensor "disk_check" {
            protocol = "snmp"
            interval = 300
            warning = 80
            critical = 95
        }
        '''
        s1, s2 = roundtrip(src)
        assert s1[0].thresholds == s2[0].thresholds

    def test_roundtrip_with_query(self):
        src = '''
        sensor "mem_check" {
            protocol = "wmi"
            interval = 60
            query = "SELECT * FROM Win32_OperatingSystem"
        }
        '''
        s1, s2 = roundtrip(src)
        assert s1[0].query == s2[0].query

    def test_roundtrip_with_timeout_retries(self):
        src = '''
        sensor "ping_check" {
            protocol = "icmp"
            interval = 30
            timeout = 10
            retries = 5
        }
        '''
        s1, s2 = roundtrip(src)
        assert s1[0].timeout == s2[0].timeout
        assert s1[0].retries == s2[0].retries

    def test_roundtrip_multiple_sensors(self):
        src = '''
        sensor "cpu" {
            protocol = "wmi"
            interval = 60
        }
        sensor "disk" {
            protocol = "snmp"
            interval = 300
            warning = 80
            critical = 95
        }
        '''
        s1, s2 = roundtrip(src)
        assert len(s1) == len(s2) == 2
        for a, b in zip(s1, s2):
            assert a.protocol == b.protocol
            assert a.interval == b.interval


# ─── Property 19: DSL rejeita protocolos inválidos ──────────────────────────

class TestInvalidProtocol:
    def test_invalid_protocol_raises_error(self):
        src = '''
        sensor "bad_sensor" {
            protocol = "ftp"
            interval = 60
        }
        '''
        with pytest.raises(DSLSyntaxError) as exc_info:
            compile_dsl(src)
        assert "protocol" in str(exc_info.value).lower() or "ftp" in str(exc_info.value).lower()

    def test_invalid_protocol_has_field_info(self):
        src = '''
        sensor "bad" {
            protocol = "telnet"
            interval = 60
        }
        '''
        with pytest.raises(DSLSyntaxError) as exc_info:
            compile_dsl(src)
        err = exc_info.value
        assert err.field == "protocol"

    def test_invalid_protocol_lists_valid_options(self):
        src = '''
        sensor "bad" {
            protocol = "xyz"
            interval = 60
        }
        '''
        with pytest.raises(DSLSyntaxError) as exc_info:
            compile_dsl(src)
        msg = str(exc_info.value)
        # Deve mencionar protocolos válidos
        assert any(p.value in msg for p in Protocol)

    def test_empty_protocol_rejected(self):
        src = '''
        sensor "bad" {
            protocol = ""
            interval = 60
        }
        '''
        with pytest.raises(DSLSyntaxError):
            compile_dsl(src)

    def test_valid_protocols_accepted(self):
        for proto in Protocol:
            src = f'''
            sensor "test_{proto.value}" {{
                protocol = "{proto.value}"
                interval = 60
            }}
            '''
            sensors = compile_dsl(src)
            assert sensors[0].protocol == proto


# ─── Testes unitários: parsing de DSL válida ────────────────────────────────

class TestValidDSLParsing:
    def test_minimal_sensor(self):
        src = '''
        sensor "ping" {
            protocol = "icmp"
            interval = 30
        }
        '''
        sensors = compile_dsl(src)
        assert len(sensors) == 1
        assert sensors[0].protocol == Protocol.ICMP
        assert sensors[0].interval == 30

    def test_sensor_with_all_fields(self):
        src = '''
        sensor "full_sensor" {
            protocol = "wmi"
            interval = 60
            timeout = 15
            retries = 2
            query = "SELECT LoadPercentage FROM Win32_Processor"
            warning = 80
            critical = 95
            description = "CPU monitor"
        }
        '''
        sensors = compile_dsl(src)
        s = sensors[0]
        assert s.protocol == Protocol.WMI
        assert s.interval == 60
        assert s.timeout == 15
        assert s.retries == 2
        assert s.query == "SELECT LoadPercentage FROM Win32_Processor"
        assert s.thresholds["warning"] == 80.0
        assert s.thresholds["critical"] == 95.0

    def test_sensor_type_is_name(self):
        src = '''
        sensor "my_custom_sensor" {
            protocol = "tcp"
            interval = 120
        }
        '''
        sensors = compile_dsl(src)
        assert sensors[0].type == "my_custom_sensor"

    def test_float_thresholds(self):
        src = '''
        sensor "temp" {
            protocol = "snmp"
            interval = 60
            warning = 75.5
            critical = 90.0
        }
        '''
        sensors = compile_dsl(src)
        assert sensors[0].thresholds["warning"] == 75.5
        assert sensors[0].thresholds["critical"] == 90.0

    def test_multiple_sensors_parsed(self):
        src = '''
        sensor "cpu" { protocol = "wmi" interval = 60 }
        sensor "mem" { protocol = "wmi" interval = 60 }
        sensor "disk" { protocol = "snmp" interval = 300 }
        '''
        sensors = compile_dsl(src)
        assert len(sensors) == 3

    def test_http_protocol(self):
        src = '''
        sensor "web_check" {
            protocol = "http"
            interval = 60
            query = "https://example.com/health"
        }
        '''
        sensors = compile_dsl(src)
        assert sensors[0].protocol == Protocol.HTTP


# ─── Testes unitários: comentários ignorados ────────────────────────────────

class TestCommentsIgnored:
    def test_line_comment_ignored(self):
        src = '''
        # Este é um comentário de linha
        sensor "cpu" {
            protocol = "wmi"  # protocolo WMI
            interval = 60     # a cada 60 segundos
        }
        '''
        sensors = compile_dsl(src)
        assert len(sensors) == 1
        assert sensors[0].protocol == Protocol.WMI

    def test_block_comment_ignored(self):
        src = '''
        /* Sensor de CPU
           Monitora uso de processador */
        sensor "cpu" {
            protocol = "wmi"
            interval = 60
            /* warning threshold */
            warning = 80
        }
        '''
        sensors = compile_dsl(src)
        assert len(sensors) == 1
        assert sensors[0].thresholds["warning"] == 80.0

    def test_multiline_block_comment(self):
        src = '''
        /*
         * Arquivo de configuração de sensores
         * Versão 3.0
         */
        sensor "disk" {
            protocol = "snmp"
            interval = 300
        }
        '''
        sensors = compile_dsl(src)
        assert len(sensors) == 1

    def test_comment_between_sensors(self):
        src = '''
        sensor "cpu" { protocol = "wmi" interval = 60 }
        # separador
        sensor "mem" { protocol = "wmi" interval = 60 }
        '''
        sensors = compile_dsl(src)
        assert len(sensors) == 2


# ─── Testes unitários: herança de templates ─────────────────────────────────

class TestTemplateInheritance:
    def _make_template_node(self, name: str, fields: dict) -> SensorNode:
        field_nodes = [FieldNode(k, v, 0) for k, v in fields.items()]
        return SensorNode(name=name, fields=field_nodes)

    def test_extends_inherits_fields(self):
        template_node = self._make_template_node("disk_template", {
            "protocol": "snmp",
            "interval": 300,
            "warning": 80,
            "critical": 95,
        })
        compiler = DSLCompiler(templates={"disk_template": template_node})
        src = '''
        sensor "disk_c" extends "disk_template" {
            query = "C:"
        }
        '''
        sensors = compiler.compile(src)
        assert sensors[0].protocol == Protocol.SNMP
        assert sensors[0].interval == 300
        assert sensors[0].thresholds["warning"] == 80.0
        assert sensors[0].query == "C:"

    def test_extends_overrides_fields(self):
        template_node = self._make_template_node("wmi_template", {
            "protocol": "wmi",
            "interval": 60,
            "warning": 80,
        })
        compiler = DSLCompiler(templates={"wmi_template": template_node})
        src = '''
        sensor "cpu_custom" extends "wmi_template" {
            interval = 30
            warning = 90
        }
        '''
        sensors = compiler.compile(src)
        assert sensors[0].interval == 30
        assert sensors[0].thresholds["warning"] == 90.0

    def test_extends_missing_template_raises_error(self):
        src = '''
        sensor "orphan" extends "nonexistent_template" {
            protocol = "wmi"
            interval = 60
        }
        '''
        with pytest.raises(DSLSyntaxError) as exc_info:
            compile_dsl(src)
        assert "nonexistent_template" in str(exc_info.value)


# ─── Testes de erros de sintaxe ─────────────────────────────────────────────

class TestSyntaxErrors:
    def test_missing_required_protocol(self):
        src = '''
        sensor "bad" {
            interval = 60
        }
        '''
        with pytest.raises(DSLSyntaxError) as exc_info:
            compile_dsl(src)
        assert "protocol" in str(exc_info.value)

    def test_missing_required_interval(self):
        src = '''
        sensor "bad" {
            protocol = "wmi"
        }
        '''
        with pytest.raises(DSLSyntaxError) as exc_info:
            compile_dsl(src)
        assert "interval" in str(exc_info.value)

    def test_unclosed_brace_raises_error(self):
        src = '''
        sensor "bad" {
            protocol = "wmi"
            interval = 60
        '''
        with pytest.raises((DSLSyntaxError, Exception)):
            compile_dsl(src)

    def test_unclosed_string_raises_error(self):
        src = 'sensor "bad { protocol = "wmi" interval = 60 }'
        with pytest.raises((DSLSyntaxError, LexerError, Exception)):
            compile_dsl(src)

    def test_empty_source_returns_empty_list(self):
        sensors = compile_dsl("")
        assert sensors == []

    def test_only_comments_returns_empty_list(self):
        src = '''
        # apenas comentários
        /* nada aqui */
        '''
        sensors = compile_dsl(src)
        assert sensors == []


# ─── Testes do Lexer ────────────────────────────────────────────────────────

class TestLexer:
    def test_tokenizes_sensor_keyword(self):
        from sensor_dsl.lexer import TokenType
        lexer = Lexer()
        tokens = lexer.tokenize('sensor "test" {}')
        types = [t.type for t in tokens]
        assert TokenType.SENSOR in types

    def test_tokenizes_extends_keyword(self):
        from sensor_dsl.lexer import TokenType
        lexer = Lexer()
        tokens = lexer.tokenize('sensor "a" extends "b" {}')
        types = [t.type for t in tokens]
        assert TokenType.EXTENDS in types

    def test_tokenizes_number_int(self):
        from sensor_dsl.lexer import TokenType
        lexer = Lexer()
        tokens = lexer.tokenize('x = 60')
        num_tokens = [t for t in tokens if t.type == TokenType.NUMBER]
        assert num_tokens[0].value == "60"

    def test_tokenizes_number_float(self):
        from sensor_dsl.lexer import TokenType
        lexer = Lexer()
        tokens = lexer.tokenize('x = 3.14')
        num_tokens = [t for t in tokens if t.type == TokenType.NUMBER]
        assert num_tokens[0].value == "3.14"


# ─── Testes do Printer ──────────────────────────────────────────────────────

class TestDSLPrinter:
    def test_print_produces_valid_dsl(self):
        src = '''
        sensor "cpu" {
            protocol = "wmi"
            interval = 60
        }
        '''
        sensors = compile_dsl(src)
        printer = DSLPrinter()
        output = printer.print(sensors[0])
        assert 'sensor "cpu"' in output
        assert 'protocol = "wmi"' in output
        assert 'interval = 60' in output

    def test_print_all_separates_with_blank_line(self):
        src = '''
        sensor "a" { protocol = "wmi" interval = 60 }
        sensor "b" { protocol = "snmp" interval = 300 }
        '''
        sensors = compile_dsl(src)
        printer = DSLPrinter()
        output = printer.print_all(sensors)
        assert '\n\n' in output
