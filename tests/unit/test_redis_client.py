"""Unit tests for redis_client.py"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from exporter.redis_client import connect_to_redis, do_redis_cmd


class TestConnectToRedis:
    """Tests for connect_to_redis function"""

    @patch('exporter.redis_client.redis.Redis')
    def test_connect_basic(self, mock_redis_class):
        """Test basic connection"""
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_redis_class.return_value = mock_client
        
        client = connect_to_redis("redis://localhost:6379")
        
        assert client == mock_client
        mock_redis_class.assert_called_once()
        call_kwargs = mock_redis_class.call_args[1]
        assert call_kwargs["host"] == "localhost"
        assert call_kwargs["port"] == 6379

    @patch('exporter.redis_client.redis.Redis')
    def test_connect_without_scheme(self, mock_redis_class):
        """Test connection without scheme in URI"""
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_redis_class.return_value = mock_client
        
        client = connect_to_redis("localhost:6379")
        
        assert client == mock_client
        call_kwargs = mock_redis_class.call_args[1]
        assert call_kwargs["host"] == "localhost"
        assert call_kwargs["port"] == 6379

    @patch('exporter.redis_client.redis.Redis')
    def test_connect_with_password_in_uri(self, mock_redis_class):
        """Test connection with password in URI"""
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_redis_class.return_value = mock_client
        
        client = connect_to_redis("redis://:mypassword@localhost:6379")
        
        call_kwargs = mock_redis_class.call_args[1]
        assert call_kwargs["password"] == "mypassword"

    @patch('exporter.redis_client.redis.Redis')
    def test_connect_with_user_in_uri(self, mock_redis_class):
        """Test connection with username in URI"""
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_redis_class.return_value = mock_client
        
        client = connect_to_redis("redis://user:pass@localhost:6379")
        
        call_kwargs = mock_redis_class.call_args[1]
        assert call_kwargs["username"] == "user"
        assert call_kwargs["password"] == "pass"

    @patch('exporter.redis_client.redis.Redis')
    def test_connect_with_password_param(self, mock_redis_class):
        """Test connection with password parameter"""
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_redis_class.return_value = mock_client
        
        client = connect_to_redis("redis://localhost:6379", password="secret")
        
        call_kwargs = mock_redis_class.call_args[1]
        assert call_kwargs["password"] == "secret"

    @patch('exporter.redis_client.redis.Redis')
    def test_connect_with_tls(self, mock_redis_class):
        """Test connection with TLS"""
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_redis_class.return_value = mock_client
        
        client = connect_to_redis("rediss://localhost:6380")
        
        call_kwargs = mock_redis_class.call_args[1]
        assert call_kwargs["ssl"] is True

    @patch('exporter.redis_client.redis.Redis')
    def test_connect_with_timeout(self, mock_redis_class):
        """Test connection with timeout"""
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_redis_class.return_value = mock_client
        
        client = connect_to_redis("redis://localhost:6379", connection_timeout=10.0)
        
        call_kwargs = mock_redis_class.call_args[1]
        assert call_kwargs["socket_timeout"] == 10.0
        assert call_kwargs["socket_connect_timeout"] == 10.0

    @patch('exporter.redis_client.redis.Redis')
    def test_connect_set_client_name(self, mock_redis_class):
        """Test setting client name"""
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_client.client_setname.return_value = True
        mock_redis_class.return_value = mock_client
        
        client = connect_to_redis("redis://localhost:6379", set_client_name=True)
        
        mock_client.client_setname.assert_called_once_with("redis_exporter")

    @patch('exporter.redis_client.redis.Redis')
    def test_connect_skip_client_name(self, mock_redis_class):
        """Test skipping client name"""
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_redis_class.return_value = mock_client
        
        client = connect_to_redis("redis://localhost:6379", set_client_name=False)
        
        mock_client.client_setname.assert_not_called()

    @patch('exporter.redis_client.redis.Redis')
    def test_connect_default_port(self, mock_redis_class):
        """Test connection defaults to port 6379"""
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_redis_class.return_value = mock_client
        
        client = connect_to_redis("redis://localhost")
        
        call_kwargs = mock_redis_class.call_args[1]
        assert call_kwargs["port"] == 6379

    @patch('exporter.redis_client.redis.Redis')
    def test_connect_ping_fails(self, mock_redis_class):
        """Test connection failure"""
        mock_client = MagicMock()
        mock_client.ping.side_effect = Exception("Connection failed")
        mock_redis_class.return_value = mock_client
        
        with pytest.raises(Exception, match="Connection failed"):
            connect_to_redis("redis://localhost:6379")

    @patch('exporter.redis_client.redis.Redis')
    def test_connect_client_name_fails(self, mock_redis_class):
        """Test that client name failure doesn't fail connection"""
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_client.client_setname.side_effect = Exception("Cannot set name")
        mock_redis_class.return_value = mock_client
        
        # Should not raise
        client = connect_to_redis("redis://localhost:6379", set_client_name=True)
        assert client == mock_client


class TestDoRedisCmd:
    """Tests for do_redis_cmd function"""

    def test_do_redis_cmd_success(self):
        """Test successful command execution"""
        mock_client = MagicMock()
        mock_client.execute_command.return_value = "OK"
        
        result = do_redis_cmd(mock_client, "SET", "key", "value")
        
        assert result == "OK"
        mock_client.execute_command.assert_called_once_with("SET", "key", "value")

    def test_do_redis_cmd_with_multiple_args(self):
        """Test command with multiple arguments"""
        mock_client = MagicMock()
        mock_client.execute_command.return_value = 3
        
        result = do_redis_cmd(mock_client, "DEL", "key1", "key2", "key3")
        
        assert result == 3
        mock_client.execute_command.assert_called_once_with("DEL", "key1", "key2", "key3")

    def test_do_redis_cmd_no_args(self):
        """Test command with no arguments"""
        mock_client = MagicMock()
        mock_client.execute_command.return_value = "PONG"
        
        result = do_redis_cmd(mock_client, "PING")
        
        assert result == "PONG"
        mock_client.execute_command.assert_called_once_with("PING")

    def test_do_redis_cmd_failure(self):
        """Test command execution failure"""
        mock_client = MagicMock()
        mock_client.execute_command.side_effect = Exception("Command failed")
        
        with pytest.raises(Exception, match="Command failed"):
            do_redis_cmd(mock_client, "INVALID", "command")

