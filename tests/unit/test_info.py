"""Unit tests for info.py"""

import pytest
from exporter.info import (
    parse_db_keyspace_string,
    parse_command_stats,
    parse_error_stats,
    extract_info_metrics,
    _should_include_metric,
    _get_metric_name,
)


class TestParseDbKeyspaceString:
    """Tests for parse_db_keyspace_string function"""

    def test_parse_valid_keyspace(self):
        """Test parsing valid keyspace string"""
        result = parse_db_keyspace_string("db0", "keys=1000,expires=50,avg_ttl=3600000")
        assert result == (1000, 50, 3600000, -1)

    def test_parse_keyspace_with_cached(self):
        """Test parsing keyspace with cached keys"""
        result = parse_db_keyspace_string("db0", "keys=100,expires=10,avg_ttl=1800,keys_cached=5")
        assert result == (100, 10, 1800, 5)

    def test_parse_keyspace_partial(self):
        """Test parsing partial keyspace info"""
        result = parse_db_keyspace_string("db0", "keys=100,expires=10")
        assert result == (100, 10, -1, -1)

    def test_parse_keyspace_empty(self):
        """Test parsing empty keyspace"""
        result = parse_db_keyspace_string("db0", "")
        assert result == (0, 0, -1, -1)

    def test_parse_keyspace_invalid_values(self):
        """Test parsing with invalid values"""
        result = parse_db_keyspace_string("db0", "keys=100,expires=invalid,avg_ttl=50")
        assert result == (100, 0, 50, -1)

    def test_parse_keyspace_zero_values(self):
        """Test parsing zero values"""
        result = parse_db_keyspace_string("db0", "keys=0,expires=0,avg_ttl=0")
        assert result == (0, 0, 0, -1)


class TestParseCommandStats:
    """Tests for parse_command_stats function"""

    def test_parse_basic_cmdstat(self):
        """Test parsing basic command stats"""
        result = parse_command_stats("cmdstat_get", "calls=1000,usec=5000,usec_per_call=5.00")
        assert result is not None
        cmd, calls, rejected, failed, usec, extended = result
        assert cmd == "get"
        assert calls == 1000.0
        assert rejected == 0.0
        assert failed == 0.0
        assert usec == 5000.0
        assert extended is False

    def test_parse_extended_cmdstat(self):
        """Test parsing extended command stats"""
        result = parse_command_stats(
            "cmdstat_set",
            "calls=500,usec=2500,usec_per_call=5.00,rejected_calls=10,failed_calls=5"
        )
        assert result is not None
        cmd, calls, rejected, failed, usec, extended = result
        assert cmd == "set"
        assert calls == 500.0
        assert rejected == 10.0
        assert failed == 5.0
        assert usec == 2500.0
        assert extended is True

    def test_parse_invalid_key(self):
        """Test parsing invalid key"""
        result = parse_command_stats("invalid_key", "calls=100")
        assert result is None

    def test_parse_cmdstat_partial(self):
        """Test parsing partial command stats"""
        result = parse_command_stats("cmdstat_del", "calls=100")
        assert result is not None
        cmd, calls, rejected, failed, usec, extended = result
        assert cmd == "del"
        assert calls == 100.0
        assert rejected == 0.0
        assert failed == 0.0
        assert usec == 0.0
        assert extended is False

    def test_parse_cmdstat_empty(self):
        """Test parsing empty command stats"""
        result = parse_command_stats("cmdstat_get", "")
        assert result is not None
        cmd, calls, rejected, failed, usec, extended = result
        assert calls == 0.0


class TestParseErrorStats:
    """Tests for parse_error_stats function"""

    def test_parse_valid_errorstat(self):
        """Test parsing valid error stat"""
        result = parse_error_stats("errorstat_ERR", "count=10")
        assert result is not None
        error_type, count = result
        assert error_type == "ERR"
        assert count == 10.0

    def test_parse_errorstat_zero(self):
        """Test parsing zero error count"""
        result = parse_error_stats("errorstat_WRONGTYPE", "count=0")
        assert result is not None
        error_type, count = result
        assert error_type == "WRONGTYPE"
        assert count == 0.0

    def test_parse_errorstat_invalid_key(self):
        """Test parsing invalid key"""
        result = parse_error_stats("invalid_key", "count=10")
        assert result is None

    def test_parse_errorstat_invalid_format(self):
        """Test parsing invalid format"""
        result = parse_error_stats("errorstat_ERR", "invalid=10")
        assert result is not None
        error_type, count = result
        assert count == 0.0

    def test_parse_errorstat_invalid_count(self):
        """Test parsing invalid count value"""
        result = parse_error_stats("errorstat_ERR", "count=invalid")
        assert result is None


class TestExtractInfoMetrics:
    """Tests for extract_info_metrics function"""

    @pytest.fixture
    def sample_info_string(self):
        """Sample INFO output"""
        return """# Server
redis_version:7.0.0
os:Linux 6.0.0
process_id:12345
uptime_in_seconds:86400
tcp_port:6379

# Clients
connected_clients:10
maxclients:10000
blocked_clients:0

# Memory
used_memory:1048576
used_memory_rss:2097152
mem_fragmentation_ratio:2.0

# Stats
total_connections_received:1000
total_commands_processed:50000
instantaneous_ops_per_sec:10

# Keyspace
db0:keys=1000,expires=100,avg_ttl=3600000
db1:keys=500,expires=50,avg_ttl=1800000

# Commandstats
cmdstat_get:calls=10000,usec=50000,usec_per_call=5.00
cmdstat_set:calls=5000,usec=25000,usec_per_call=5.00

# Errorstats
errorstat_ERR:count=10
errorstat_WRONGTYPE:count=5
"""

    def test_extract_basic_metrics(self, sample_info_string, mock_collector):
        """Test extracting basic metrics from INFO"""
        metric_map_gauges = {
            "connected_clients": "connected_clients",
            "used_memory": "memory_used_bytes",
        }
        metric_map_counters = {
            "total_commands_processed": "commands_processed_total",
        }
        
        extract_info_metrics(
            sample_info_string,
            metric_map_gauges,
            metric_map_counters,
            mock_collector,
        )
        
        # Check that metrics were registered
        assert len(mock_collector._current_metrics) > 0
        assert "connected_clients" in mock_collector._current_metrics
        assert "memory_used_bytes" in mock_collector._current_metrics
        assert "commands_processed_total" in mock_collector._current_metrics

    def test_extract_keyspace_metrics(self, sample_info_string, mock_collector):
        """Test extracting keyspace metrics"""
        metric_map_gauges = {}
        metric_map_counters = {}
        
        extract_info_metrics(
            sample_info_string,
            metric_map_gauges,
            metric_map_counters,
            mock_collector,
        )
        
        # Check keyspace metrics
        assert "db_keys" in mock_collector._current_metrics
        assert "db_keys_expiring" in mock_collector._current_metrics
        assert "db_avg_ttl_seconds" in mock_collector._current_metrics

    def test_extract_command_stats(self, sample_info_string, mock_collector):
        """Test extracting command stats"""
        metric_map_gauges = {}
        metric_map_counters = {}
        
        extract_info_metrics(
            sample_info_string,
            metric_map_gauges,
            metric_map_counters,
            mock_collector,
        )
        
        # Check command stats
        assert "commands_total" in mock_collector._current_metrics
        assert "commands_duration_seconds_total" in mock_collector._current_metrics

    def test_extract_error_stats(self, sample_info_string, mock_collector):
        """Test extracting error stats"""
        metric_map_gauges = {}
        metric_map_counters = {}
        
        extract_info_metrics(
            sample_info_string,
            metric_map_gauges,
            metric_map_counters,
            mock_collector,
        )
        
        # Check error stats
        assert "errors_total" in mock_collector._current_metrics


class TestShouldIncludeMetric:
    """Tests for _should_include_metric function"""

    def test_include_db_keys(self):
        """Test including db keys"""
        metric_map_gauges = {}
        metric_map_counters = {}
        
        assert _should_include_metric("db0", metric_map_gauges, metric_map_counters) is True
        assert _should_include_metric("db1", metric_map_gauges, metric_map_counters) is True

    def test_include_cmdstat_keys(self):
        """Test including cmdstat keys"""
        metric_map_gauges = {}
        metric_map_counters = {}
        
        assert _should_include_metric("cmdstat_get", metric_map_gauges, metric_map_counters) is True
        assert _should_include_metric("cmdstat_set", metric_map_gauges, metric_map_counters) is True

    def test_include_in_maps(self):
        """Test including metrics in maps"""
        metric_map_gauges = {"used_memory": "memory"}
        metric_map_counters = {"total_commands": "cmds"}
        
        assert _should_include_metric("used_memory", metric_map_gauges, metric_map_counters) is True
        assert _should_include_metric("total_commands", metric_map_gauges, metric_map_counters) is True
        assert _should_include_metric("other", metric_map_gauges, metric_map_counters) is False


class TestGetMetricName:
    """Tests for _get_metric_name function"""

    def test_get_name_from_gauge_map(self):
        """Test getting name from gauge map"""
        metric_map_gauges = {"used_memory": "memory_used_bytes"}
        metric_map_counters = {}
        
        name = _get_metric_name("used_memory", metric_map_gauges, metric_map_counters)
        assert name == "memory_used_bytes"

    def test_get_name_from_counter_map(self):
        """Test getting name from counter map"""
        metric_map_gauges = {}
        metric_map_counters = {"total_commands_processed": "commands_processed_total"}
        
        name = _get_metric_name("total_commands_processed", metric_map_gauges, metric_map_counters)
        assert name == "commands_processed_total"

    def test_get_name_sanitized(self):
        """Test getting sanitized name"""
        metric_map_gauges = {}
        metric_map_counters = {}
        
        name = _get_metric_name("metric-with.dots", metric_map_gauges, metric_map_counters)
        assert name == "metric_with_dots"

