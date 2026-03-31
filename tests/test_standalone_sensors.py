"""
MCT (Model-based Component Testing) + SDD (Scenario-Driven Development)
Tests for standalone sensor creation, API response, and probe collection routing.

Tests each sensor type:
1. HTTP (Sites) - sensor_type=http, needs http_url
2. ICMP (Ping) - sensor_type=icmp, needs ip_address
3. SNMP (Generic) - sensor_type=snmp, needs ip_address
4. Engetron (UPS) - sensor_type=snmp, name contains 'engetron'
5. Conflex (HVAC) - sensor_type=snmp, name contains 'ar-condicionado' or 'conflex'
"""
import pytest
import re
from datetime import datetime


# ── Simulated sensor data (as returned by /sensors/standalone/by-probe) ──

SENSOR_HTTP = {
    "id": 1001, "name": "Site Techbiz", "sensor_type": "http",
    "category": "network", "http_url": "https://techbiz.com.br",
    "http_method": "GET", "ip_address": None,
    "snmp_community": "public", "snmp_port": 161, "snmp_version": "v2c",
    "threshold_warning": 80.0, "threshold_critical": 95.0,
}

SENSOR_ICMP = {
    "id": 1002, "name": "Ping Automatizador", "sensor_type": "icmp",
    "category": "icmp", "http_url": None, "http_method": "GET",
    "ip_address": "192.168.31.34",
    "snmp_community": "public", "snmp_port": 161, "snmp_version": "v2c",
    "threshold_warning": 100.0, "threshold_critical": 500.0,
}

SENSOR_ICMP_BY_CATEGORY = {
    "id": 1003, "name": "Conflex Monitor", "sensor_type": "snmp",
    "category": "icmp", "http_url": None, "http_method": "GET",
    "ip_address": "192.168.31.34",
    "snmp_community": "public", "snmp_port": 161, "snmp_version": "v2c",
    "threshold_warning": 100.0, "threshold_critical": 500.0,
}

SENSOR_SNMP = {
    "id": 1004, "name": "Switch Core", "sensor_type": "snmp",
    "category": "snmp", "http_url": None, "http_method": "GET",
    "ip_address": "192.168.31.48",
    "snmp_community": "public", "snmp_port": 161, "snmp_version": "v2c",
    "threshold_warning": 80.0, "threshold_critical": 95.0,
}

SENSOR_ENGETRON = {
    "id": 1005, "name": "Nobreak Engetron", "sensor_type": "snmp",
    "category": "snmp", "http_url": None, "http_method": "GET",
    "ip_address": "192.168.31.134",
    "snmp_community": "public", "snmp_port": 161, "snmp_version": "v2c",
    "threshold_warning": 80.0, "threshold_critical": 95.0,
}

SENSOR_CONFLEX = {
    "id": 1006, "name": "Ar-Condicionado Conflex", "sensor_type": "snmp",
    "category": "snmp", "http_url": None, "http_method": "GET",
    "ip_address": "192.168.31.34",
    "snmp_community": "public", "snmp_port": 161, "snmp_version": "v2c",
    "threshold_warning": 80.0, "threshold_critical": 95.0,
}

SENSOR_FALLBACK = {
    "id": 1007, "name": "Dispositivo Generico", "sensor_type": "custom",
    "category": "custom", "http_url": None, "http_method": "GET",
    "ip_address": "192.168.31.99",
    "snmp_community": "public", "snmp_port": 161, "snmp_version": "v2c",
    "threshold_warning": 80.0, "threshold_critical": 95.0,
}

SENSOR_NO_IP = {
    "id": 1008, "name": "Sensor Sem IP", "sensor_type": "custom",
    "category": "custom", "http_url": None, "http_method": "GET",
    "ip_address": None,
    "snmp_community": "public", "snmp_port": 161, "snmp_version": "v2c",
    "threshold_warning": 80.0, "threshold_critical": 95.0,
}


# ── Route detection logic (mirrors probe_core.py _collect_standalone_sensors) ──

def detect_collection_route(sensor):
    """
    Simulates the probe's routing logic for standalone sensors.
    Returns the collector name that would handle this sensor.
    """
    # HTTP
    if (sensor.get('sensor_type') == 'http' or sensor.get('http_url')) and sensor.get('http_url'):
        return 'http'

    # ICMP by type/category (PRIORITY - before name-based detection)
    if sensor.get('ip_address') and (
        sensor.get('sensor_type') in ('icmp', 'ping')
        or sensor.get('category') == 'icmp'
    ):
        return 'icmp'

    # Engetron by name
    if sensor.get('ip_address') and sensor.get('name', '').lower().find('engetron') >= 0:
        return 'engetron'

    # Conflex by name
    if sensor.get('ip_address') and (
        sensor.get('name', '').lower().find('conflex') >= 0
        or sensor.get('name', '').lower().find('ar-condicionado') >= 0
        or sensor.get('name', '').lower().find('ar condicionado') >= 0
    ):
        return 'conflex'

    # SNMP by type
    if sensor.get('sensor_type') in ('snmp', 'snmp_ap', 'snmp_ups', 'snmp_switch') and sensor.get('ip_address'):
        return 'snmp'

    # Fallback with IP
    if sensor.get('ip_address') and sensor.get('sensor_type') not in ('http', 'https'):
        return 'snmp_fallback'

    # No collection possible
    return 'none'


# ── MCT: Route Detection Tests ──

class TestRouteDetection:
    """MCT: Verify each sensor type routes to the correct collector."""

    def test_http_sensor_routes_to_http(self):
        assert detect_collection_route(SENSOR_HTTP) == 'http'

    def test_icmp_sensor_routes_to_icmp(self):
        assert detect_collection_route(SENSOR_ICMP) == 'icmp'

    def test_icmp_by_category_routes_to_icmp(self):
        """Sensor with sensor_type=snmp but category=icmp should route to ICMP."""
        assert detect_collection_route(SENSOR_ICMP_BY_CATEGORY) == 'icmp'

    def test_snmp_sensor_routes_to_snmp(self):
        assert detect_collection_route(SENSOR_SNMP) == 'snmp'

    def test_engetron_routes_to_engetron(self):
        assert detect_collection_route(SENSOR_ENGETRON) == 'engetron'

    def test_conflex_routes_to_conflex(self):
        assert detect_collection_route(SENSOR_CONFLEX) == 'conflex'

    def test_fallback_routes_to_snmp_fallback(self):
        assert detect_collection_route(SENSOR_FALLBACK) == 'snmp_fallback'

    def test_no_ip_routes_to_none(self):
        assert detect_collection_route(SENSOR_NO_IP) == 'none'

    def test_icmp_with_conflex_name_still_routes_icmp(self):
        """Critical: sensor_type=icmp with 'conflex' in name must route to ICMP, not Conflex."""
        sensor = {**SENSOR_ICMP, "name": "Conflex ICMP Monitor", "sensor_type": "icmp", "category": "icmp"}
        assert detect_collection_route(sensor) == 'icmp'

    def test_engetron_name_variations(self):
        for name in ["Nobreak Engetron", "ENGETRON UPS", "engetron 15kva", "UPS Engetron DC"]:
            sensor = {**SENSOR_ENGETRON, "name": name}
            assert detect_collection_route(sensor) == 'engetron', f"Failed for name: {name}"

    def test_conflex_name_variations(self):
        for name in ["Ar-Condicionado", "AR-CONDICIONADO CPD", "Conflex AGST", "ar condicionado sala"]:
            sensor = {**SENSOR_CONFLEX, "name": name}
            assert detect_collection_route(sensor) == 'conflex', f"Failed for name: {name}"

    def test_http_without_url_does_not_route_http(self):
        sensor = {**SENSOR_HTTP, "http_url": None}
        # Should fall through to 'none' since no IP either
        assert detect_collection_route(sensor) == 'none'


# ── SDD: Scenario Tests ──

class TestScenarios:
    """SDD: End-to-end scenarios for sensor lifecycle."""

    def test_scenario_add_http_site(self):
        """Scenario: User adds a new HTTP site monitor."""
        sensor = {
            "name": "Site CRM", "sensor_type": "http", "category": "network",
            "http_url": "https://crm.techbiz.com.br", "ip_address": None,
        }
        route = detect_collection_route(sensor)
        assert route == 'http', "HTTP site should route to http collector"

    def test_scenario_add_icmp_automator(self):
        """Scenario: User adds ICMP ping for an automation device."""
        sensor = {
            "name": "Automatizador Predial", "sensor_type": "icmp", "category": "icmp",
            "http_url": None, "ip_address": "192.168.31.50",
        }
        route = detect_collection_route(sensor)
        assert route == 'icmp', "ICMP device should route to icmp collector"

    def test_scenario_add_snmp_switch(self):
        """Scenario: User adds SNMP switch monitor."""
        sensor = {
            "name": "Switch Andar 3", "sensor_type": "snmp", "category": "snmp",
            "http_url": None, "ip_address": "192.168.31.200",
        }
        route = detect_collection_route(sensor)
        assert route == 'snmp', "SNMP switch should route to snmp collector"

    def test_scenario_add_nobreak(self):
        """Scenario: User adds Engetron UPS monitor."""
        sensor = {
            "name": "Nobreak Engetron 30kVA", "sensor_type": "snmp", "category": "snmp",
            "http_url": None, "ip_address": "192.168.31.134",
        }
        route = detect_collection_route(sensor)
        assert route == 'engetron', "Engetron UPS should route to engetron collector"

    def test_scenario_add_hvac(self):
        """Scenario: User adds Conflex HVAC monitor."""
        sensor = {
            "name": "Ar-Condicionado CPD", "sensor_type": "snmp", "category": "snmp",
            "http_url": None, "ip_address": "192.168.31.34",
        }
        route = detect_collection_route(sensor)
        assert route == 'conflex', "HVAC should route to conflex collector"

    def test_scenario_add_camera_icmp(self):
        """Scenario: User adds camera with ICMP ping."""
        sensor = {
            "name": "Camera Estacionamento", "sensor_type": "icmp", "category": "icmp",
            "http_url": None, "ip_address": "192.168.31.80",
        }
        route = detect_collection_route(sensor)
        assert route == 'icmp', "Camera ICMP should route to icmp collector"

    def test_scenario_conflex_named_sensor_with_icmp_type(self):
        """Scenario: User creates sensor named 'Conflex' but with type ICMP.
        ICMP type must take priority over name detection."""
        sensor = {
            "name": "Comunicação Conflex", "sensor_type": "icmp", "category": "icmp",
            "http_url": None, "ip_address": "192.168.31.34",
        }
        route = detect_collection_route(sensor)
        assert route == 'icmp', "ICMP type must override Conflex name detection"

    def test_scenario_unknown_device_with_ip(self):
        """Scenario: User adds unknown device type with IP - should fallback to SNMP."""
        sensor = {
            "name": "Impressora HP", "sensor_type": "printer", "category": "custom",
            "http_url": None, "ip_address": "192.168.31.150",
        }
        route = detect_collection_route(sensor)
        assert route == 'snmp_fallback', "Unknown device with IP should fallback to SNMP"

    def test_scenario_sensor_without_ip_or_url(self):
        """Scenario: User creates sensor without IP or URL - should not collect."""
        sensor = {
            "name": "Azure Monitor", "sensor_type": "azure", "category": "azure",
            "http_url": None, "ip_address": None,
        }
        route = detect_collection_route(sensor)
        assert route == 'none', "Sensor without IP/URL should not be collected"


# ── MCT: API Response Validation ──

class TestAPIResponse:
    """MCT: Validate the by-probe API response has all required fields."""

    REQUIRED_FIELDS = ['id', 'name', 'sensor_type', 'category', 'ip_address',
                       'http_url', 'snmp_community', 'snmp_port', 'snmp_version']

    @pytest.mark.parametrize("sensor", [
        SENSOR_HTTP, SENSOR_ICMP, SENSOR_SNMP, SENSOR_ENGETRON,
        SENSOR_CONFLEX, SENSOR_FALLBACK, SENSOR_ICMP_BY_CATEGORY,
    ])
    def test_all_required_fields_present(self, sensor):
        for field in self.REQUIRED_FIELDS:
            assert field in sensor, f"Missing field '{field}' in sensor {sensor['name']}"

    def test_http_sensor_has_url(self):
        assert SENSOR_HTTP['http_url'] is not None

    def test_icmp_sensor_has_ip(self):
        assert SENSOR_ICMP['ip_address'] is not None

    def test_snmp_sensor_has_ip_and_community(self):
        assert SENSOR_SNMP['ip_address'] is not None
        assert SENSOR_SNMP['snmp_community'] is not None

    def test_icmp_category_preserved(self):
        assert SENSOR_ICMP['category'] == 'icmp'
        assert SENSOR_ICMP_BY_CATEGORY['category'] == 'icmp'


# ── MCT: Engetron HTML Parser ──

class TestEngetronParser:
    """MCT: Validate Engetron HTML parsing regexes."""

    SAMPLE_HTML = '''
    <b>Entrada</b>
    <td class=tdl>Tens&atilde;o</td>
    <td class=tdv>              123 V</td>
    <td class=tdv>              124 V</td>
    <td class=tdv>              125 V</td>
    <b>Sa&iacute;da</b>
    <td class=tdl>Tens&atilde;o</td>
    <td class=tdv>              127 V</td>
    <td class=tdv>              126 V</td>
    <td class=tdv>              127 V</td>
    <td class=tdl>Carga Utilizada</td>
    <td class=tdv>               13 %</td>
    <td class=tdv>               12 %</td>
    <td class=tdv>                4 %</td>
    <td class=tdl>Temperatura interna</td>
    <td class=tdv>               22 °C</td>
    <td class=tdl>Ligado / Desligado</td>
    <td class=tdv>           LIGADO</td>
    '''

    def test_temperature_regex(self):
        match = re.search(r"Temperatura interna</td>\s*<td class=tdv>\s*(\d+)", self.SAMPLE_HTML)
        assert match is not None
        assert float(match.group(1)) == 22

    def test_tensao_entrada_regex(self):
        match = re.search(r"Entrada.*?Tens[^<]*o</td>\s*<td class=tdv>\s*([\d.]+)\s*V</td>\s*<td class=tdv>\s*([\d.]+)\s*V</td>\s*<td class=tdv>\s*([\d.]+)\s*V", self.SAMPLE_HTML, re.DOTALL)
        assert match is not None, "Should match 3 input voltages"
        assert float(match.group(1)) == 123
        assert float(match.group(2)) == 124
        assert float(match.group(3)) == 125

    def test_tensao_saida_regex(self):
        match = re.search(r"Sa.*?Tens[^<]*o</td>\s*<td class=tdv>\s*([\d.]+)\s*V</td>\s*<td class=tdv>\s*([\d.]+)\s*V</td>\s*<td class=tdv>\s*([\d.]+)\s*V", self.SAMPLE_HTML, re.DOTALL)
        assert match is not None, "Should match 3 output voltages"
        assert float(match.group(1)) == 127
        assert float(match.group(2)) == 126
        assert float(match.group(3)) == 127

    def test_carga_regex(self):
        cargas = re.findall(r"Carga Utilizada</td>\s*<td class=tdv>\s*(\d+)\s*%", self.SAMPLE_HTML)
        assert len(cargas) >= 1
        assert int(cargas[0]) == 13

    def test_status_ligado(self):
        assert "LIGADO" in self.SAMPLE_HTML


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
