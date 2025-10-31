"""Pytest configuration and fixtures"""

import os
import pytest
from typing import Generator
from unittest.mock import MagicMock

import fakeredis

from exporter.config import Options
from tests.utils import create_sample_info


@pytest.fixture
def options() -> Options:
    """Create default Options for testing"""
    return Options(
        redis_addr="redis://localhost:6379",
        password="",
        user="",
        namespace="redis",
        check_keys="",
        check_single_keys="",
        connection_timeout=5.0,
        set_client_name=False,
        web_listen_address=":9121",
    )


@pytest.fixture
def mock_redis_client() -> fakeredis.FakeStrictRedis:
    """Create a mock Redis client using fakeredis"""
    client = fakeredis.FakeStrictRedis(decode_responses=False)
    
    # Set up common test data
    client.set(b"test:key1", b"value1")
    client.set(b"test:key2", b"value2")
    client.hset(b"test:hash1", b"field1", b"value1")
    client.hset(b"test:hash1", b"field2", b"value2")
    client.lpush(b"test:list1", b"item1", b"item2", b"item3")
    client.sadd(b"test:set1", b"member1", b"member2")
    client.zadd(b"test:zset1", {b"member1": 1.0, b"member2": 2.0})
    
    return client


@pytest.fixture
def redis_client():
    """Real Redis client fixture"""
    try:
        import redis
        client = redis.Redis(host="localhost", port=6379, decode_responses=False)
        client.ping()
        yield client
    except Exception:
        pytest.skip("Redis not available")


@pytest.fixture
def sample_info() -> str:
    """Sample Redis INFO output"""
    return create_sample_info()


@pytest.fixture
def mock_collector():
    """Mock collector for testing parsers"""
    collector = MagicMock()
    collector._current_metrics = {}
    
    def mock_register_metric(metric_name, value, **kwargs):
        if metric_name not in collector._current_metrics:
            collector._current_metrics[metric_name] = []
        collector._current_metrics[metric_name].append({"value": value, **kwargs})
    
    def mock_create_metric_descr(metric_name, **kwargs):
        pass
    
    collector._register_metric = mock_register_metric
    collector._create_metric_descr = mock_create_metric_descr
    
    return collector


@pytest.fixture(autouse=True)
def clear_env():
    """Clear environment variables before each test"""
    env_vars = [
        "REDIS_ADDR",
        "REDIS_PASSWORD",
        "REDIS_USER",
        "REDIS_EXPORTER_NAMESPACE",
        "REDIS_EXPORTER_CHECK_KEYS",
        "REDIS_EXPORTER_CHECK_SINGLE_KEYS",
        "REDIS_EXPORTER_CONNECTION_TIMEOUT",
        "REDIS_EXPORTER_SET_CLIENT_NAME",
        "REDIS_EXPORTER_WEB_LISTEN_ADDRESS",
    ]
    
    # Save original values
    original = {var: os.environ.get(var) for var in env_vars}
    
    # Clear all
    for var in env_vars:
        if var in os.environ:
            del os.environ[var]
    
    yield
    
    # Restore original values
    for var, value in original.items():
        if value is None:
            os.environ.pop(var, None)
        else:
            os.environ[var] = value


@pytest.fixture
def redis_available():
    """Check if real Redis is available"""
    try:
        import redis
        client = redis.Redis(host="localhost", port=6379, socket_connect_timeout=1)
        client.ping()
        return True
    except Exception:
        return False

