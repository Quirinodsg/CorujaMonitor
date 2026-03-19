"""
FASE 2 — Testes do SNMP Sensor
Valida: coleta v2c, v3, printer metrics, bulk walk, device discovery.
Todos os testes usam mocks — não requerem dispositivo SNMP real.
"""
import pytest
from unittest.mock import patch, MagicMock, call
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../probe'))

from collectors.snmp_collector import SNMPCollector, PYSNMP_AVAILABLE


# ─── Helpers ─────────────────────────────────────────────────────────────────

def make_varbind(oid_str, value_str):
    """Cria um varbind simulado (tupla oid, value)."""
    oid = MagicMock()
    oid.__str__ = MagicMock(return_value=oid_str)
    val = MagicMock()
    val.__str__ = MagicMock(return_value=value_str)
    return (oid, val)


def mock_getCmd_success(oid_value_map):
    """
    Retorna um mock de getCmd que itera sobre oid_value_map.
    Cada chamada a next() retorna (None, None, None, [varbind]).
    """
    def side_effect(*args, **kwargs):
        # Extrair o OID do ObjectType passado
        obj_type = args[-1] if args else None
        # Retornar um iterador com resultado de sucesso
        varbind = make_varbind("1.3.6.1.2.1.1.1.0", "Linux server")
        return iter([(None, None, None, [varbind])])
    return side_effect


# ─── Testes sem pysnmp (fallback) ────────────────────────────────────────────

class TestSNMPCollectorNoLibrary:

    def test_collect_without_pysnmp_returns_error(self):
        """Sem pysnmp instalado → retorna status error."""
        collector = SNMPCollector()

        with patch("collectors.snmp_collector.PYSNMP_AVAILABLE", False):
            result = collector.collect_snmp_v2c("192.168.1.1")

        assert result["status"] == "error"
        assert "pysnmp" in result["error"].lower()
        assert result["host"] == "192.168.1.1"


# ─── Testes de coleta v2c ────────────────────────────────────────────────────

@pytest.mark.skipif(not PYSNMP_AVAILABLE, reason="pysnmp not installed")
class TestSNMPCollectorV2c:

    def test_collect_v2c_success(self):
        """Coleta v2c com sucesso retorna status success."""
        collector = SNMPCollector()
        varbind = make_varbind("1.3.6.1.2.1.1.1.0", "Linux 5.15")

        with patch("collectors.snmp_collector.getCmd") as mock_get:
            mock_get.return_value = iter([(None, None, None, [varbind])])
            result = collector.collect_snmp_v2c("192.168.1.1", community="public", oids=["1.3.6.1.2.1.1.1.0"])

        assert result["status"] == "success"
        assert result["host"] == "192.168.1.1"
        assert result["version"] == "v2c"
        assert "data" in result
        assert "timestamp" in result

    def test_collect_v2c_error_indication(self):
        """errorIndication → OID ignorado, resultado ainda retorna success com data vazia."""
        collector = SNMPCollector()

        with patch("collectors.snmp_collector.getCmd") as mock_get:
            mock_get.return_value = iter([("No SNMP response", None, None, [])])
            result = collector.collect_snmp_v2c("192.168.1.1", oids=["1.3.6.1.2.1.1.1.0"])

        # Deve retornar success mas com data vazia (OID ignorado)
        assert result["status"] == "success"
        assert result["data"] == {}

    def test_collect_v2c_exception(self):
        """Exceção geral → status error."""
        collector = SNMPCollector()

        with patch("collectors.snmp_collector.getCmd", side_effect=Exception("connection failed")):
            result = collector.collect_snmp_v2c("192.168.1.1", oids=["1.3.6.1.2.1.1.1.0"])

        assert result["status"] == "error"
        assert "error" in result

    def test_collect_v2c_multiple_oids(self):
        """Coleta múltiplos OIDs."""
        collector = SNMPCollector()
        oids = ["1.3.6.1.2.1.1.1.0", "1.3.6.1.2.1.1.5.0"]

        call_count = {"n": 0}
        def mock_get(*args, **kwargs):
            call_count["n"] += 1
            vb = make_varbind(oids[min(call_count["n"]-1, len(oids)-1)], f"value_{call_count['n']}")
            return iter([(None, None, None, [vb])])

        with patch("collectors.snmp_collector.getCmd", side_effect=mock_get):
            result = collector.collect_snmp_v2c("192.168.1.1", oids=oids)

        assert result["status"] == "success"
        assert call_count["n"] == len(oids)


# ─── Testes de printer metrics ───────────────────────────────────────────────

@pytest.mark.skipif(not PYSNMP_AVAILABLE, reason="pysnmp not installed")
class TestSNMPPrinterMetrics:

    def test_collect_printer_success(self):
        """Coleta de impressora retorna estrutura correta."""
        collector = SNMPCollector()

        # Mock collect_snmp_v2c para retornar dados de impressora
        mock_result = {
            "status": "success",
            "host": "192.168.1.50",
            "data": {
                "1.3.6.1.2.1.43.11.1.1.9.1": "80",   # toner level
                "1.3.6.1.2.1.43.10.2.1.4.1": "15000",  # page count
            }
        }

        with patch.object(collector, "collect_snmp_v2c", return_value=mock_result):
            result = collector.collect_printer_metrics("192.168.1.50")

        assert result["status"] == "success"
        assert result["type"] == "printer"
        assert "data" in result
        assert "toner_levels" in result["data"]
        assert "page_count" in result["data"]

    def test_collect_printer_snmp_error(self):
        """Erro SNMP → propaga error."""
        collector = SNMPCollector()

        with patch.object(collector, "collect_snmp_v2c", return_value={"status": "error", "host": "x", "error": "timeout"}):
            result = collector.collect_printer_metrics("192.168.1.50")

        assert result["status"] == "error"


# ─── Testes de device discovery ──────────────────────────────────────────────

@pytest.mark.skipif(not PYSNMP_AVAILABLE, reason="pysnmp not installed")
class TestSNMPDeviceDiscovery:

    def test_discover_linux_server(self):
        """Descobre servidor Linux pela descrição."""
        collector = SNMPCollector()

        mock_result = {
            "status": "success",
            "host": "192.168.1.10",
            "data": {
                "1.3.6.1.2.1.1.1.0": "Linux ubuntu 5.15.0",
                "1.3.6.1.2.1.1.5.0": "srv-web-01",
                "1.3.6.1.2.1.1.3.0": "123456",
            }
        }

        with patch.object(collector, "collect_snmp_v2c", return_value=mock_result):
            result = collector.discover_device("192.168.1.10")

        assert result["status"] == "success"
        assert "device" in result
        assert result["device"]["name"] == "srv-web-01"

    def test_discover_cisco_switch(self):
        """Identifica switch Cisco pelo sysDescr."""
        collector = SNMPCollector()

        mock_result = {
            "status": "success",
            "host": "192.168.1.254",
            "data": {
                "1.3.6.1.2.1.1.1.0": "Cisco IOS Software, Version 15.2",
                "1.3.6.1.2.1.1.5.0": "core-switch-01",
                "1.3.6.1.2.1.1.3.0": "9876543",
            }
        }

        with patch.object(collector, "collect_snmp_v2c", return_value=mock_result):
            result = collector.discover_device("192.168.1.254")

        assert result["status"] == "success"
        assert result["device"]["type"] == "switch"
        assert result["device"]["vendor"] == "Cisco"

    def test_discover_error(self):
        """Erro na coleta → propaga error."""
        collector = SNMPCollector()

        with patch.object(collector, "collect_snmp_v2c", return_value={"status": "error", "host": "x", "error": "timeout"}):
            result = collector.discover_device("192.168.1.1")

        assert result["status"] == "error"


# ─── Testes de custom OIDs ───────────────────────────────────────────────────

class TestSNMPCustomOIDs:

    def test_add_custom_oid(self):
        collector = SNMPCollector()
        collector.add_custom_oid("myMetric", "1.3.6.1.4.1.99999.1.0", "Custom metric")
        assert "myMetric" in collector.custom_oids
        assert collector.custom_oids["myMetric"]["oid"] == "1.3.6.1.4.1.99999.1.0"

    def test_standard_oids_exist(self):
        """OIDs padrão RFC 1213 devem estar definidos."""
        collector = SNMPCollector()
        assert "sysDescr" in collector.STANDARD_OIDS
        assert "sysUpTime" in collector.STANDARD_OIDS
        assert "sysName" in collector.STANDARD_OIDS

    def test_linux_oids_exist(self):
        """OIDs de servidor Linux (UCD-SNMP-MIB) devem estar definidos."""
        collector = SNMPCollector()
        assert "ssCpuIdle" in collector.LINUX_SERVER_OIDS
        assert "memTotalReal" in collector.LINUX_SERVER_OIDS
        assert "laLoad1" in collector.LINUX_SERVER_OIDS

    def test_printer_oids_exist(self):
        """OIDs de impressora (RFC 3805) devem estar definidos."""
        collector = SNMPCollector()
        assert "prtMarkerSuppliesLevel" in collector.PRINTER_OIDS
        assert "prtMarkerLifeCount" in collector.PRINTER_OIDS


# ─── Testes de bulk walk ─────────────────────────────────────────────────────

@pytest.mark.skipif(not PYSNMP_AVAILABLE, reason="pysnmp not installed")
class TestSNMPBulkWalk:

    def test_bulk_walk_returns_list(self):
        """bulk_walk retorna lista de resultados."""
        collector = SNMPCollector()
        vb1 = make_varbind("1.3.6.1.2.1.2.2.1.2.1", "eth0")
        vb2 = make_varbind("1.3.6.1.2.1.2.2.1.2.2", "eth1")

        with patch("collectors.snmp_collector.bulkCmd") as mock_bulk:
            mock_bulk.return_value = iter([
                (None, None, None, [vb1]),
                (None, None, None, [vb2]),
            ])
            results = collector.bulk_walk("192.168.1.1", "public", "1.3.6.1.2.1.2.2.1.2")

        assert isinstance(results, list)
        assert len(results) == 2
        assert "oid" in results[0]
        assert "value" in results[0]

    def test_bulk_walk_error_returns_empty(self):
        """Erro no bulk walk → retorna lista vazia."""
        collector = SNMPCollector()

        with patch("collectors.snmp_collector.bulkCmd", side_effect=Exception("timeout")):
            results = collector.bulk_walk("192.168.1.1", "public", "1.3.6.1.2.1.2")

        assert results == []
