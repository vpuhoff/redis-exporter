"""Integration tests for Redis Exporter"""

import pytest

from exporter import RedisCollector, Options
from tests.utils import redis_available


@pytest.mark.integration
class TestExporterIntegration:
    """Integration tests for Redis Exporter"""

    @pytest.mark.skipif(not redis_available(), reason="Redis not available")
    def test_collector_initialization(self):
        """Test collector initialization"""
        options = Options(redis_addr="redis://localhost:6379")
        collector = RedisCollector("redis://localhost:6379", options)
        
        assert collector.redis_addr == "redis://localhost:6379"
        assert collector.options == options

    @pytest.mark.skipif(not redis_available(), reason="Redis not available")
    def test_collect_basic_metrics(self):
        """Test collecting basic metrics"""
        options = Options(redis_addr="redis://localhost:6379", set_client_name=False)
        collector = RedisCollector("redis://localhost:6379", options)
        
        # Collect metrics
        metrics = list(collector.collect())
        
        assert len(metrics) > 0
        # Check that we have 'up' metric
        metric_names = [m.name for m in metrics]
        assert any("up" in name for name in metric_names)

    @pytest.mark.skipif(not redis_available(), reason="Redis not available")
    def test_collect_with_fake_redis_client(self, mock_redis_client):
        """Test collecting metrics with fake Redis client"""
        options = Options(redis_addr="redis://localhost:6379", set_client_name=False)
        collector = RedisCollector("redis://localhost:6379", options)
        
        # Replace client with mock
        collector.client = mock_redis_client
        
        # Collect metrics
        metrics = list(collector.collect())
        
        assert len(metrics) > 0

    @pytest.mark.skipif(not redis_available(), reason="Redis not available")
    def test_collect_with_check_keys(self):
        """Test collecting metrics with key checking"""
        import fakeredis
        
        client = fakeredis.FakeStrictRedis(decode_responses=False)
        client.set(b"test:key1", b"value1")
        client.set(b"test:key2", b"value2")
        
        options = Options(
            redis_addr="redis://localhost:6379",
            check_single_keys="test:key1",
            set_client_name=False,
        )
        collector = RedisCollector("redis://localhost:6379", options)
        collector.client = client
        
        # Collect metrics
        metrics = list(collector.collect())
        
        # Should have key_size metric
        metric_names = [m.name for m in metrics]
        assert any("key_size" in name for name in metric_names)

    @pytest.mark.skipif(not redis_available(), reason="Redis not available")
    def test_collect_with_pattern_keys(self):
        """Test collecting metrics with pattern keys"""
        import fakeredis
        
        client = fakeredis.FakeStrictRedis(decode_responses=False)
        client.set(b"pattern:key1", b"value1")
        client.set(b"pattern:key2", b"value2")
        client.set(b"other:key1", b"value3")
        
        options = Options(
            redis_addr="redis://localhost:6379",
            check_keys="pattern:*",
            set_client_name=False,
        )
        collector = RedisCollector("redis://localhost:6379", options)
        collector.client = client
        
        # Collect metrics
        metrics = list(collector.collect())
        
        # Should have key_size metrics for pattern keys
        metric_names = [m.name for m in metrics]
        assert any("key_size" in name for name in metric_names)

    @pytest.mark.skipif(not redis_available(), reason="Redis not available")
    def test_collect_up_metric_success(self):
        """Test 'up' metric is 1 on success"""
        options = Options(redis_addr="redis://localhost:6379", set_client_name=False)
        collector = RedisCollector("redis://localhost:6379", options)
        
        metrics = list(collector.collect())
        
        # Find up metric
        for metric in metrics:
            if "up" in metric.name:
                for sample in metric.samples:
                    if sample.name.endswith("_up"):
                        assert sample.value == 1.0

    @pytest.mark.skipif(not redis_available(), reason="Redis not available")
    def test_collect_up_metric_failure(self):
        """Test 'up' metric is 0 on failure"""
        options = Options(redis_addr="redis://localhost:9999", set_client_name=False)
        collector = RedisCollector("redis://localhost:9999", options)
        
        # This will fail to connect
        metrics = list(collector.collect())
        
        # Find up metric
        for metric in metrics:
            if "up" in metric.name:
                for sample in metric.samples:
                    if sample.name.endswith("_up"):
                        assert sample.value == 0.0

    @pytest.mark.skipif(not redis_available(), reason="Redis not available")
    def test_collect_exporter_metrics(self):
        """Test exporter internal metrics"""
        options = Options(redis_addr="redis://localhost:6379", set_client_name=False)
        collector = RedisCollector("redis://localhost:6379", options)
        
        metrics = list(collector.collect())
        
        # Find exporter metrics
        metric_names = [m.name for m in metrics]
        assert any("scrape_duration_seconds" in name for name in metric_names)
        assert any("scrape_error" in name for name in metric_names)

