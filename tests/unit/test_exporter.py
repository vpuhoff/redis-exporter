"""Unit tests for exporter.py"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from exporter import RedisCollector, Options
from exporter.exporter import GaugeMetricFamily, CounterMetricFamily


class TestRedisCollector:
    """Tests for RedisCollector class"""

    def test_collector_initialization(self):
        """Test collector initialization"""
        options = Options()
        collector = RedisCollector("redis://localhost:6379", options)
        
        assert collector.redis_addr == "redis://localhost:6379"
        assert collector.options == options
        assert collector.client is None
        assert len(collector.metric_map_gauges) > 0
        assert len(collector.metric_map_counters) > 0

    def test_register_metric(self):
        """Test metric registration"""
        collector = RedisCollector("redis://localhost:6379", Options())
        
        collector._register_metric("test_metric", 42.0)
        assert "test_metric" in collector._current_metrics
        assert len(collector._current_metrics["test_metric"]) == 1
        assert collector._current_metrics["test_metric"][0]["value"] == 42.0

    def test_register_metric_with_labels(self):
        """Test metric registration with labels"""
        collector = RedisCollector("redis://localhost:6379", Options())
        
        collector._register_metric("test_metric", 100.0, labels={"key": "value"})
        assert collector._current_metrics["test_metric"][0]["labels"] == {"key": "value"}

    def test_register_metric_counter(self):
        """Test registering counter metric"""
        collector = RedisCollector("redis://localhost:6379", Options())
        
        collector._register_metric("test_counter", 5.0, is_counter=True)
        assert collector._current_metrics["test_counter"][0]["is_counter"] is True

    @patch('exporter.exporter.connect_to_redis')
    def test_connect_new_connection(self, mock_connect):
        """Test creating new connection"""
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_connect.return_value = mock_client
        
        collector = RedisCollector("redis://localhost:6379", Options())
        client = collector._connect()
        
        assert client == mock_client
        mock_connect.assert_called_once()

    @patch('exporter.exporter.connect_to_redis')
    def test_connect_reuse_connection(self, mock_connect):
        """Test reusing existing connection"""
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_connect.return_value = mock_client
        
        collector = RedisCollector("redis://localhost:6379", Options())
        collector._connect()
        
        # Second call should not call connect_to_redis again
        collector._connect()
        assert mock_connect.call_count == 1

    @patch('exporter.exporter.connect_to_redis')
    def test_connect_recreate_on_failure(self, mock_connect):
        """Test recreating connection on failure"""
        mock_client = MagicMock()
        mock_client.ping.side_effect = [Exception("Connection lost"), True]
        mock_connect.return_value = mock_client
        
        collector = RedisCollector("redis://localhost:6379", Options())
        collector.client = mock_client
        
        collector._connect()
        collector._connect()  # Should recreate
        
        assert mock_connect.call_count == 1  # Called once during second _connect

    def test_create_metric_descr(self):
        """Test metric description creation"""
        collector = RedisCollector("redis://localhost:6379", Options())
        
        # Should not raise
        collector._create_metric_descr("test_metric")
        collector._create_metric_descr("test_metric", labels=["label1", "label2"])

