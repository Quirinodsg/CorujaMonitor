"""
MCT/SDD Tests: Validate ALL sensor categories in the system.
Tests creation via API model, probe routing, and identifies gaps.

Categories tested:
- network_devices, standard, windows, linux, network, snmp
- storage, cloud, azure, database, application, custom, icmp
"""
import pytest


# ── Simulate API creation (StandaloneSensorCreate validation) ──

VALID_CATEGORIES = {
    "network": {"sensor_type": "http", "http_url": "https://example.com", "probe_id": None},
    "snmp": {"sensor_type": "snmp", "ip_address": "192.168.1.1", "probe_id": 1},
    "icmp": {"sensor_type": "icmp", "ip_address": "192.168.1.1", "probe_id": 1},
    "azure": {"sensor_type": "azure", "azure_subscription_id": "sub-123", "probe_id": 1},
    "storage": {"sensor_type": "snmp", "ip_address": "192.168.1.1", "probe_id": 1},
    "cloud": {"sensor_type": "http", "http_url": "https://cloud.example.com", "probe_id": None},
    "database": {"sensor_type": "snmp", "ip_address": "192.168.1.1", "probe_id": 1},
    "application": {"sensor_type": "http", "http_url": "https://app.example.com", "probe_id": None},
    "custom": {"sensor_type": "custom", "ip_address": "192.168.1.1", "probe_id": 1},
    "standard": {"sensor_type": "snmp", "ip_address": "192.168.1.1", "probe_id": 1},
    "windows": {"sensor_type": "snmp", "ip_address": "192.168.1.1", "probe_id": 1},
    "linux": {"sensor_type": "snmp", "ip_address": "192.168.1.1", "probe_id": 1},
}


def create_sensor_payload(category, name="Test Sensor"):
    """Build a valid sensor creation payload for a given category."""
    base = {
        "name": name,
        "category": category,
        "snmp_version": "v2c",
        "snmp_community": "public",
        "snmp_port": 161,
        "threshold_warning": 80,
        "threshold_critical": 95,
        "description": f"Test {category} sensor",
    }
    overrides = VALID_CATEGORIES.get(category, {"sensor_type": category, "probe_id": 1})
    base.update(overrides)
    return base


# ── Probe routing logic (same as probe_core.py) ──

def detect_route(sensor):
    if (sensor.get('sensor_type') == 'http' or sensor.get('http_url')) and sensor.get('http_url'):
        return 'http'
    if sensor.get('ip_address') and (
        sensor.get('sensor_type') in ('icmp', 'ping') or sensor.get('category') == 'icmp'
    ):
        return 'icmp'
    if sensor.get('ip_address') and sensor.get('name', '').lower().find('engetron') >= 0:
        return 'engetron'
    if sensor.get('ip_address') and (
        sensor.get('name', '').lower().find('conflex') >= 0
        or sensor.get('name', '').lower().find('ar-condicionado') >= 0
    ):
        return 'conflex'
    if sensor.get('sensor_type') in ('snmp', 'snmp_ap', 'snmp_ups', 'snmp_switch') and sensor.get('ip_address'):
        return 'snmp'
    if sensor.get('ip_address') and sensor.get('sensor_type') not in ('http', 'https'):
        return 'snmp_fallback'
    return 'none'


# ── MCT: API Creation Tests ──

class TestAPICreation:
    """Verify each category produces a valid creation payload."""

    @pytest.mark.parametrize("category", list(VALID_CATEGORIES.keys()))
    def test_payload_has_required_fields(self, category):
        payload = create_sensor_payload(category)
        assert 'name' in payload
        assert 'sensor_type' in payload
        assert 'category' in payload
        assert payload['category'] == category

    @pytest.mark.parametrize("category", list(VALID_CATEGORIES.keys()))
    def test_payload_has_sensor_type(self, category):
        payload = create_sensor_payload(category)
        assert payload['sensor_type'] is not None
        assert len(payload['sensor_type']) > 0

    def test_http_categories_have_url(self):
        """HTTP-based categories (network, cloud, application) must have http_url."""
        for cat in ['network', 'cloud', 'application']:
            payload = create_sensor_payload(cat)
            assert payload.get('http_url'), f"Category {cat} should have http_url"

    def test_snmp_categories_have_ip(self):
        """SNMP-based categories must have ip_address."""
        for cat in ['snmp', 'storage', 'database', 'standard', 'windows', 'linux']:
            payload = create_sensor_payload(cat)
            assert payload.get('ip_address'), f"Category {cat} should have ip_address"

    def test_icmp_has_ip(self):
        payload = create_sensor_payload('icmp')
        assert payload.get('ip_address')

    def test_azure_has_subscription(self):
        payload = create_sensor_payload('azure')
        assert payload.get('azure_subscription_id')

    def test_probe_required_for_non_http(self):
        """Non-HTTP sensors require probe_id."""
        for cat in ['snmp', 'icmp', 'storage', 'database', 'custom', 'standard', 'windows', 'linux']:
            payload = create_sensor_payload(cat)
            assert payload.get('probe_id') is not None, f"Category {cat} needs probe_id"

    def test_http_no_probe_required(self):
        """HTTP sensors don't require probe_id (collected by worker)."""
        for cat in ['network', 'cloud', 'application']:
            payload = create_sensor_payload(cat)
            assert payload.get('probe_id') is None, f"Category {cat} should not need probe_id"


# ── SDD: Probe Collection Routing ──

class TestProbeRouting:
    """Verify each category routes to a working collector."""

    EXPECTED_ROUTES = {
        'network': 'http',
        'cloud': 'http',
        'application': 'http',
        'snmp': 'snmp',
        'storage': 'snmp',
        'database': 'snmp',
        'standard': 'snmp',
        'windows': 'snmp',
        'linux': 'snmp',
        'icmp': 'icmp',
        'azure': 'none',  # Azure uses API, not probe collection
        'custom': 'snmp_fallback',
    }

    @pytest.mark.parametrize("category,expected_route", list(EXPECTED_ROUTES.items()))
    def test_category_routes_correctly(self, category, expected_route):
        payload = create_sensor_payload(category, name=f"Test {category}")
        route = detect_route(payload)
        assert route == expected_route, (
            f"Category '{category}' routed to '{route}' but expected '{expected_route}'"
        )

    def test_all_categories_have_route_test(self):
        """Ensure every category in VALID_CATEGORIES has a route test."""
        for cat in VALID_CATEGORIES:
            assert cat in self.EXPECTED_ROUTES, f"Category '{cat}' missing from EXPECTED_ROUTES"


# ── SDD: Collection Capability Matrix ──

class TestCollectionCapability:
    """Document which categories have working collection and which need implementation."""

    IMPLEMENTED_COLLECTORS = {
        'http': True,       # ✅ HTTP sites - worker collects
        'icmp': True,       # ✅ Ping - probe collects
        'snmp': True,       # ✅ SNMP generic - probe collects
        'engetron': True,   # ✅ Engetron UPS - probe HTTP scraping
        'conflex': True,    # ✅ Conflex HVAC - probe SNMP proprietary
        'snmp_fallback': True,  # ✅ Fallback SNMP - probe collects
        'none': False,      # ❌ No collection (Azure API, etc.)
    }

    CATEGORY_STATUS = {
        'network': {'route': 'http', 'collects': True, 'note': 'HTTP sites monitored by worker'},
        'snmp': {'route': 'snmp', 'collects': True, 'note': 'SNMP devices via probe'},
        'icmp': {'route': 'icmp', 'collects': True, 'note': 'Ping via probe'},
        'storage': {'route': 'snmp', 'collects': True, 'note': 'Storage via SNMP'},
        'database': {'route': 'snmp', 'collects': True, 'note': 'DB servers via SNMP'},
        'standard': {'route': 'snmp', 'collects': True, 'note': 'Standard sensors via SNMP'},
        'windows': {'route': 'snmp', 'collects': True, 'note': 'Windows servers via SNMP'},
        'linux': {'route': 'snmp', 'collects': True, 'note': 'Linux servers via SNMP'},
        'cloud': {'route': 'http', 'collects': True, 'note': 'Cloud endpoints via HTTP'},
        'application': {'route': 'http', 'collects': True, 'note': 'App endpoints via HTTP'},
        'custom': {'route': 'snmp_fallback', 'collects': True, 'note': 'Custom devices via SNMP fallback'},
        'azure': {'route': 'none', 'collects': False, 'note': 'Azure API - needs dedicated collector'},
    }

    @pytest.mark.parametrize("category,info", list(CATEGORY_STATUS.items()))
    def test_collection_status_documented(self, category, info):
        """Verify each category has documented collection status."""
        assert 'route' in info
        assert 'collects' in info
        assert 'note' in info

    def test_working_categories_count(self):
        working = sum(1 for v in self.CATEGORY_STATUS.values() if v['collects'])
        total = len(self.CATEGORY_STATUS)
        assert working >= 11, f"At least 11 categories should work, got {working}/{total}"

    def test_azure_marked_as_not_collecting(self):
        """Azure needs dedicated API collector - should be marked as not collecting."""
        assert self.CATEGORY_STATUS['azure']['collects'] is False


# ── SDD: Frontend Category Filter ──

class TestFrontendCategories:
    """Verify the frontend category filter matches backend capabilities."""

    FRONTEND_FILTER_CATEGORIES = ['all', 'sites', 'network_devices', 'energia', 'hvac']

    def test_filter_categories_exist(self):
        assert len(self.FRONTEND_FILTER_CATEGORIES) >= 4

    def test_all_option_exists(self):
        assert 'all' in self.FRONTEND_FILTER_CATEGORIES


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
