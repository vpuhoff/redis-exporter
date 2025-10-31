"""Unit tests for config.py"""

import os
import pytest

from exporter.config import get_env, get_env_bool, get_env_float, Options


class TestGetEnv:
    """Tests for get_env function"""

    def test_get_env_existing(self):
        """Test getting existing environment variable"""
        os.environ["TEST_VAR"] = "test_value"
        assert get_env("TEST_VAR") == "test_value"

    def test_get_env_missing_without_default(self):
        """Test getting non-existing env var without default"""
        assert get_env("NON_EXISTENT_VAR") == ""

    def test_get_env_missing_with_default(self):
        """Test getting non-existing env var with default"""
        assert get_env("NON_EXISTENT_VAR", "default_value") == "default_value"

    def test_get_env_empty_string(self):
        """Test getting empty string environment variable"""
        os.environ["EMPTY_VAR"] = ""
        assert get_env("EMPTY_VAR") == ""


class TestGetEnvBool:
    """Tests for get_env_bool function"""

    def test_get_env_bool_true_values(self):
        """Test various true boolean values"""
        true_values = ["true", "True", "TRUE", "1", "yes", "Yes", "YES", "on", "On", "ON"]
        for val in true_values:
            os.environ["TEST_VAR"] = val
            assert get_env_bool("TEST_VAR") is True

    def test_get_env_bool_false_values(self):
        """Test various false boolean values"""
        false_values = ["false", "False", "FALSE", "0", "no", "No", "NO", "off", "Off", "OFF", "invalid"]
        for val in false_values:
            os.environ["TEST_VAR"] = val
            assert get_env_bool("TEST_VAR") is False

    def test_get_env_bool_missing_without_default(self):
        """Test getting non-existing env var without default"""
        assert get_env_bool("NON_EXISTENT_VAR") is False

    def test_get_env_bool_missing_with_default(self):
        """Test getting non-existing env var with default"""
        assert get_env_bool("NON_EXISTENT_VAR", True) is True
        assert get_env_bool("NON_EXISTENT_VAR", False) is False


class TestGetEnvFloat:
    """Tests for get_env_float function"""

    def test_get_env_float_valid_values(self):
        """Test valid float values"""
        test_cases = [
            ("123.45", 123.45),
            ("0.0", 0.0),
            ("-42.5", -42.5),
            ("1e-3", 0.001),
            ("10", 10.0),
        ]
        for val, expected in test_cases:
            os.environ["TEST_VAR"] = val
            assert get_env_float("TEST_VAR") == expected

    def test_get_env_float_invalid_values(self):
        """Test invalid float values"""
        invalid_values = ["not_a_number", "abc", "12.34.56"]
        for val in invalid_values:
            os.environ["TEST_VAR"] = val
            assert get_env_float("TEST_VAR") == 0.0

    def test_get_env_float_missing_without_default(self):
        """Test getting non-existing env var without default"""
        assert get_env_float("NON_EXISTENT_VAR") == 0.0

    def test_get_env_float_missing_with_default(self):
        """Test getting non-existing env var with default"""
        assert get_env_float("NON_EXISTENT_VAR", 5.5) == 5.5
        assert get_env_float("NON_EXISTENT_VAR", 0.0) == 0.0


class TestOptions:
    """Tests for Options class"""

    def test_options_default_values(self):
        """Test Options with default values"""
        opts = Options()
        assert opts.redis_addr == "redis://localhost:6379"
        assert opts.password == ""
        assert opts.user == ""
        assert opts.namespace == "redis"
        assert opts.check_keys == ""
        assert opts.check_single_keys == ""
        assert opts.connection_timeout == 15.0
        assert opts.set_client_name is True
        assert opts.web_listen_address == ":9121"

    def test_options_custom_values(self):
        """Test Options with custom values"""
        opts = Options(
            redis_addr="redis://custom:6380",
            password="secret",
            user="admin",
            namespace="custom",
            check_keys="key1,key2",
            check_single_keys="specific",
            connection_timeout=30.0,
            set_client_name=False,
            web_listen_address=":8080",
        )
        assert opts.redis_addr == "redis://custom:6380"
        assert opts.password == "secret"
        assert opts.user == "admin"
        assert opts.namespace == "custom"
        assert opts.check_keys == "key1,key2"
        assert opts.check_single_keys == "specific"
        assert opts.connection_timeout == 30.0
        assert opts.set_client_name is False
        assert opts.web_listen_address == ":8080"

    def test_options_from_env_defaults(self):
        """Test Options.from_env with no environment variables"""
        opts = Options.from_env()
        assert opts.redis_addr == "redis://localhost:6379"
        assert opts.password == ""
        assert opts.user == ""
        assert opts.namespace == "redis"
        assert opts.connection_timeout == 15.0
        assert opts.set_client_name is True

    def test_options_from_env_custom(self):
        """Test Options.from_env with custom environment variables"""
        os.environ["REDIS_ADDR"] = "redis://test:1234"
        os.environ["REDIS_PASSWORD"] = "testpass"
        os.environ["REDIS_USER"] = "testuser"
        os.environ["REDIS_EXPORTER_NAMESPACE"] = "custom_ns"
        os.environ["REDIS_EXPORTER_CHECK_KEYS"] = "pattern:*"
        os.environ["REDIS_EXPORTER_CHECK_SINGLE_KEYS"] = "key1"
        os.environ["REDIS_EXPORTER_CONNECTION_TIMEOUT"] = "30.5"
        os.environ["REDIS_EXPORTER_SET_CLIENT_NAME"] = "false"
        os.environ["REDIS_EXPORTER_WEB_LISTEN_ADDRESS"] = ":9999"

        opts = Options.from_env()
        assert opts.redis_addr == "redis://test:1234"
        assert opts.password == "testpass"
        assert opts.user == "testuser"
        assert opts.namespace == "custom_ns"
        assert opts.check_keys == "pattern:*"
        assert opts.check_single_keys == "key1"
        assert opts.connection_timeout == 30.5
        assert opts.set_client_name is False
        assert opts.web_listen_address == ":9999"

    def test_options_merge_cli_args(self):
        """Test Options.merge_cli_args method"""
        opts = Options()
        opts.merge_cli_args(
            redis_addr="redis://new:6380",
            password="newpass",
            namespace="new_ns",
            connection_timeout=60.0,
        )
        assert opts.redis_addr == "redis://new:6380"
        assert opts.password == "newpass"
        assert opts.namespace == "new_ns"
        assert opts.connection_timeout == 60.0
        # Check unchanged values
        assert opts.user == ""
        assert opts.set_client_name is True

    def test_options_merge_cli_args_none_values(self):
        """Test that None values in merge_cli_args are ignored"""
        opts = Options(namespace="original")
        opts.merge_cli_args(namespace=None)
        assert opts.namespace == "original"

    def test_options_merge_cli_args_empty_string(self):
        """Test that empty string values in merge_cli_args are set"""
        opts = Options(namespace="original")
        opts.merge_cli_args(namespace="")
        assert opts.namespace == ""
