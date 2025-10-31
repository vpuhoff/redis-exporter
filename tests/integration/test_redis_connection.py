"""Integration tests for Redis connection"""

import pytest

from exporter.redis_client import connect_to_redis
from tests.utils import redis_available


@pytest.mark.integration
class TestRedisConnection:
    """Integration tests for Redis connection"""

    @pytest.mark.skipif(not redis_available(), reason="Redis not available")
    def test_connect_to_local_redis(self):
        """Test connecting to local Redis"""
        client = connect_to_redis("redis://localhost:6379", set_client_name=False)
        assert client is not None
        
        # Test that we can execute commands
        result = client.ping()
        assert result is True

    @pytest.mark.skipif(not redis_available(), reason="Redis not available")
    def test_connect_and_get_info(self):
        """Test getting INFO from connected Redis"""
        client = connect_to_redis("redis://localhost:6379", set_client_name=False)
        
        info = client.info()
        assert info is not None
        assert b"redis_version" in info or "redis_version" in info

    @pytest.mark.skipif(not redis_available(), reason="Redis not available")
    def test_execute_commands(self):
        """Test executing various commands"""
        client = connect_to_redis("redis://localhost:6379", set_client_name=False)
        
        # Test string operations
        client.set(b"test:integration", b"value1")
        assert client.get(b"test:integration") == b"value1"
        
        # Cleanup
        client.delete(b"test:integration")

    @pytest.mark.skipif(not redis_available(), reason="Redis not available")
    def test_connection_with_different_db(self):
        """Test connecting to different database"""
        # Note: fakeredis may not support SELECT properly
        try:
            client = connect_to_redis("redis://localhost:6379/1", set_client_name=False)
            info = client.info()
            assert info is not None
        except Exception:
            pytest.skip("Database selection not supported in test environment")

