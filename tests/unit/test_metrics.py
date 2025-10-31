"""Unit tests for metrics.py"""

import pytest

from exporter.metrics import (
    sanitize_metric_name,
    parse_metric_value,
    format_keyspace_info,
    format_cmdstat_info,
    should_include_metric,
)


class TestSanitizeMetricName:
    """Tests for sanitize_metric_name function"""

    def test_sanitize_valid_name(self):
        """Test sanitizing already valid metric name"""
        assert sanitize_metric_name("valid_metric_name") == "valid_metric_name"
        assert sanitize_metric_name("valid123") == "valid123"

    def test_sanitize_spaces(self):
        """Test sanitizing spaces"""
        assert sanitize_metric_name("metric name") == "metric_name"
        assert sanitize_metric_name("  multi  space  ") == "__multi__space__"

    def test_sanitize_hyphens(self):
        """Test sanitizing hyphens"""
        assert sanitize_metric_name("metric-name") == "metric_name"
        assert sanitize_metric_name("snake-case-metric") == "snake_case_metric"

    def test_sanitize_special_chars(self):
        """Test sanitizing special characters"""
        assert sanitize_metric_name("metric.name") == "metric_name"
        assert sanitize_metric_name("metric@name#123") == "metric_name_123"
        assert sanitize_metric_name("metric/name\\value") == "metric_name_value"

    def test_sanitize_mixed(self):
        """Test sanitizing mixed invalid characters"""
        assert sanitize_metric_name("my-metric.name_123") == "my_metric_name_123"
        assert sanitize_metric_name("@#special$%chars^&") == "__special__chars__"

    def test_sanitize_empty(self):
        """Test sanitizing empty string"""
        assert sanitize_metric_name("") == ""


class TestParseMetricValue:
    """Tests for parse_metric_value function"""

    def test_parse_numeric_values(self):
        """Test parsing numeric values"""
        assert parse_metric_value("123") == 123.0
        assert parse_metric_value("123.45") == 123.45
        assert parse_metric_value("-42") == -42.0
        assert parse_metric_value("0") == 0.0
        assert parse_metric_value("1e10") == 1e10

    def test_parse_boolean_true(self):
        """Test parsing boolean true values"""
        assert parse_metric_value("ok") == 1.0
        assert parse_metric_value("Ok") == 1.0
        assert parse_metric_value("OK") == 1.0
        assert parse_metric_value("true") == 1.0
        assert parse_metric_value("True") == 1.0
        assert parse_metric_value("TRUE") == 1.0

    def test_parse_boolean_false(self):
        """Test parsing boolean false values"""
        assert parse_metric_value("err") == 0.0
        assert parse_metric_value("Err") == 0.0
        assert parse_metric_value("ERR") == 0.0
        assert parse_metric_value("fail") == 0.0
        assert parse_metric_value("FAIL") == 0.0
        assert parse_metric_value("false") == 0.0
        assert parse_metric_value("False") == 0.0
        assert parse_metric_value("FALSE") == 0.0

    def test_parse_invalid_values(self):
        """Test parsing invalid values"""
        assert parse_metric_value("not_a_number") is None
        assert parse_metric_value("abc123") is None
        assert parse_metric_value("12.34.56") is None

    def test_parse_empty_string(self):
        """Test parsing empty string"""
        assert parse_metric_value("") is None

    def test_parse_none(self):
        """Test parsing None value"""
        assert parse_metric_value(None) is None


class TestFormatKeyspaceInfo:
    """Tests for format_keyspace_info function"""

    def test_format_valid_keyspace(self):
        """Test formatting valid keyspace info"""
        info = "keys=1000,expires=50,avg_ttl=3600000"
        result = format_keyspace_info("db0", info)
        
        assert len(result) == 3
        assert ("keyspace_keys", 1000.0, {"db": "db0"}) in result
        assert ("keyspace_expires", 50.0, {"db": "db0"}) in result
        assert ("keyspace_avg_ttl", 3600000.0, {"db": "db0"}) in result

    def test_format_keyspace_partial(self):
        """Test formatting partial keyspace info"""
        info = "keys=100,expires=10"
        result = format_keyspace_info("db1", info)
        
        assert len(result) == 2
        assert ("keyspace_keys", 100.0, {"db": "db1"}) in result
        assert ("keyspace_expires", 10.0, {"db": "db1"}) in result

    def test_format_keyspace_invalid_values(self):
        """Test formatting with invalid values"""
        info = "keys=100,expires=invalid,avg_ttl=50"
        result = format_keyspace_info("db0", info)
        
        assert len(result) == 2
        assert ("keyspace_keys", 100.0, {"db": "db0"}) in result
        assert ("keyspace_avg_ttl", 50.0, {"db": "db0"}) in result

    def test_format_keyspace_no_equals(self):
        """Test formatting keyspace without equals sign"""
        info = "keys,expires,avg_ttl"
        result = format_keyspace_info("db0", info)
        
        assert len(result) == 0

    def test_format_keyspace_empty(self):
        """Test formatting empty keyspace"""
        result = format_keyspace_info("db0", "")
        assert len(result) == 0


class TestFormatCmdstatInfo:
    """Tests for format_cmdstat_info function"""

    def test_format_valid_cmdstat(self):
        """Test formatting valid command stats"""
        info = "calls=1000,usec=5000,usec_per_call=5.00"
        result = format_cmdstat_info("get", info)
        
        assert len(result) == 3
        # Check if all three metrics are present
        metric_names = [r[0] for r in result]
        assert "command_get_calls" in metric_names
        assert "command_get_usec" in metric_names
        assert "command_get_per_call" in metric_names

    def test_format_cmdstat_per_call_conversion(self):
        """Test usec_per_call is converted to per_call"""
        info = "usec_per_call=5.00"
        result = format_cmdstat_info("set", info)
        
        assert len(result) == 1
        assert result[0][0] == "command_set_per_call"

    def test_format_cmdstat_labels(self):
        """Test command stats labels"""
        info = "calls=100"
        result = format_cmdstat_info("del", info)
        
        assert len(result) == 1
        assert result[0][2]["cmd"] == "del"

    def test_format_cmdstat_invalid_values(self):
        """Test formatting with invalid values"""
        info = "calls=100,usec=invalid,usec_per_call=5"
        result = format_cmdstat_info("get", info)
        
        assert len(result) == 2
        metric_names = [r[0] for r in result]
        assert "command_get_calls" in metric_names
        assert "command_get_per_call" in metric_names

    def test_format_cmdstat_empty(self):
        """Test formatting empty command stats"""
        result = format_cmdstat_info("get", "")
        assert len(result) == 0


class TestShouldIncludeMetric:
    """Tests for should_include_metric function"""

    def test_include_db_keys(self):
        """Test including db keys"""
        metric_map_gauges = {}
        metric_map_counters = {}
        
        assert should_include_metric("db0", metric_map_gauges, metric_map_counters) is True
        assert should_include_metric("db1", metric_map_gauges, metric_map_counters) is True
        assert should_include_metric("db_abc", metric_map_gauges, metric_map_counters) is True

    def test_include_cmdstat_keys(self):
        """Test including cmdstat keys"""
        metric_map_gauges = {}
        metric_map_counters = {}
        
        assert should_include_metric("cmdstat_get", metric_map_gauges, metric_map_counters) is True
        assert should_include_metric("cmdstat_set", metric_map_gauges, metric_map_counters) is True
        assert should_include_metric("cmdstat_del", metric_map_gauges, metric_map_counters) is True

    def test_include_in_gauge_map(self):
        """Test including metrics in gauge map"""
        metric_map_gauges = {"used_memory": "memory_used_bytes", "connected_clients": "clients"}
        metric_map_counters = {}
        
        assert should_include_metric("used_memory", metric_map_gauges, metric_map_counters) is True
        assert should_include_metric("connected_clients", metric_map_gauges, metric_map_counters) is True
        assert should_include_metric("other_metric", metric_map_gauges, metric_map_counters) is False

    def test_include_in_counter_map(self):
        """Test including metrics in counter map"""
        metric_map_gauges = {}
        metric_map_counters = {"total_commands_processed": "commands_total"}
        
        assert should_include_metric("total_commands_processed", metric_map_gauges, metric_map_counters) is True
        assert should_include_metric("other_metric", metric_map_gauges, metric_map_counters) is False

    def test_exclude_other_metrics(self):
        """Test excluding other metrics"""
        metric_map_gauges = {}
        metric_map_counters = {}
        
        assert should_include_metric("other_metric", metric_map_gauges, metric_map_counters) is False
        assert should_include_metric("random_key", metric_map_gauges, metric_map_counters) is False

