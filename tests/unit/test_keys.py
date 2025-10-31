"""Unit tests for keys.py"""

import pytest
from exporter.keys import (
    DbKeyPair,
    parse_key_arg,
    scan_keys,
    get_key_info,
    get_keys_from_patterns,
)


class TestDbKeyPair:
    """Tests for DbKeyPair class"""

    def test_db_key_pair_initialization(self):
        """Test DbKeyPair initialization"""
        pair = DbKeyPair("0", "mykey")
        assert pair.db == "0"
        assert pair.key == "mykey"

    def test_db_key_pair_different_db(self):
        """Test DbKeyPair with different database"""
        pair = DbKeyPair("5", "test:key")
        assert pair.db == "5"
        assert pair.key == "test:key"


class TestParseKeyArg:
    """Tests for parse_key_arg function"""

    def test_parse_single_key_default_db(self):
        """Test parsing single key with default db"""
        result = parse_key_arg("mykey")
        assert len(result) == 1
        assert result[0].db == "0"
        assert result[0].key == "mykey"

    def test_parse_key_with_db(self):
        """Test parsing key with db specified"""
        result = parse_key_arg("db1=mykey")
        assert len(result) == 1
        assert result[0].db == "1"
        assert result[0].key == "mykey"

    def test_parse_multiple_keys_comma_separated(self):
        """Test parsing multiple keys"""
        result = parse_key_arg("key1,key2,key3")
        assert len(result) == 3
        assert all(pair.db == "0" for pair in result)
        assert result[0].key == "key1"
        assert result[1].key == "key2"
        assert result[2].key == "key3"

    def test_parse_multiple_keys_with_db(self):
        """Test parsing multiple keys with different dbs"""
        result = parse_key_arg("db0=key1,db1=key2,db2=key3")
        assert len(result) == 3
        assert result[0].db == "0"
        assert result[0].key == "key1"
        assert result[1].db == "1"
        assert result[1].key == "key2"
        assert result[2].db == "2"
        assert result[2].key == "key3"

    def test_parse_url_encoded_key(self):
        """Test parsing URL encoded key"""
        result = parse_key_arg("test%3Akey")
        assert len(result) == 1
        assert result[0].key == "test:key"

    def test_parse_empty_string(self):
        """Test parsing empty string"""
        result = parse_key_arg("")
        assert len(result) == 0

    def test_parse_whitespace(self):
        """Test parsing with whitespace"""
        result = parse_key_arg(" key1 , db1= key2 ")
        assert len(result) == 2
        assert result[0].key == "key1"
        assert result[1].key == "key2"

    def test_parse_invalid_db(self):
        """Test parsing with invalid db number"""
        result = parse_key_arg("db-1=key,db10=key2")
        # Should skip invalid db-1
        assert len(result) == 1
        assert result[0].db == "10"


class TestScanKeys:
    """Tests for scan_keys function"""

    def test_scan_keys_with_pattern(self, mock_redis_client):
        """Test scanning keys with pattern"""
        # Add some test keys
        mock_redis_client.set(b"test:key1", b"value1")
        mock_redis_client.set(b"test:key2", b"value2")
        mock_redis_client.set(b"other:key1", b"value3")
        
        result = scan_keys(mock_redis_client, "test:*")
        # Note: mock_redis_client already has keys from fixture setup
        assert len(result) >= 2
        assert b"test:key1" in result
        assert b"test:key2" in result

    def test_scan_keys_no_matches(self, mock_redis_client):
        """Test scanning with no matches"""
        result = scan_keys(mock_redis_client, "nonexistent:*")
        assert len(result) == 0

    def test_scan_keys_empty_pattern_error(self):
        """Test scanning with empty pattern raises error"""
        from exporter.keys import scan_keys
        import fakeredis
        
        client = fakeredis.FakeStrictRedis()
        with pytest.raises(ValueError):
            scan_keys(client, "")


class TestGetKeyInfo:
    """Tests for get_key_info function"""

    def test_get_key_info_string(self, mock_redis_client):
        """Test getting info for string key"""
        mock_redis_client.set(b"test:str", b"string_value")
        result = get_key_info(mock_redis_client, "test:str")
        
        assert result is not None
        key_type, size, str_val = result
        assert key_type == "string"
        assert size > 0
        assert str_val == "string_value"

    def test_get_key_info_hash(self, mock_redis_client):
        """Test getting info for hash key"""
        mock_redis_client.hset(b"test:hash", mapping={b"field1": b"val1", b"field2": b"val2"})
        result = get_key_info(mock_redis_client, "test:hash")
        
        assert result is not None
        key_type, size, str_val = result
        assert key_type == "hash"
        assert size == 2
        assert str_val is None

    def test_get_key_info_list(self, mock_redis_client):
        """Test getting info for list key"""
        mock_redis_client.lpush(b"test:list", b"item1", b"item2", b"item3")
        result = get_key_info(mock_redis_client, "test:list")
        
        assert result is not None
        key_type, size, str_val = result
        assert key_type == "list"
        assert size == 3
        assert str_val is None

    def test_get_key_info_set(self, mock_redis_client):
        """Test getting info for set key"""
        mock_redis_client.sadd(b"test:set", b"member1", b"member2")
        result = get_key_info(mock_redis_client, "test:set")
        
        assert result is not None
        key_type, size, str_val = result
        assert key_type == "set"
        assert size == 2
        assert str_val is None

    def test_get_key_info_zset(self, mock_redis_client):
        """Test getting info for sorted set key"""
        mock_redis_client.zadd(b"test:zset", {b"member1": 1.0, b"member2": 2.0})
        result = get_key_info(mock_redis_client, "test:zset")
        
        assert result is not None
        key_type, size, str_val = result
        assert key_type == "zset"
        assert size == 2
        assert str_val is None

    def test_get_key_info_nonexistent(self, mock_redis_client):
        """Test getting info for non-existent key"""
        result = get_key_info(mock_redis_client, "nonexistent:key")
        
        assert result is not None
        key_type, size, str_val = result
        assert key_type == "none"
        assert size == 0
        assert str_val is None


class TestGetKeysFromPatterns:
    """Tests for get_keys_from_patterns function"""

    def test_expand_pattern(self, mock_redis_client):
        """Test expanding pattern"""
        mock_redis_client.set(b"test:key1", b"value1")
        mock_redis_client.set(b"test:key2", b"value2")
        
        keys = [DbKeyPair("0", "test:*")]
        result = get_keys_from_patterns(mock_redis_client, keys)
        
        assert len(result) >= 2
        result_keys = [pair.key for pair in result]
        assert "test:key1" in result_keys or b"test:key1" in result_keys
        assert "test:key2" in result_keys or b"test:key2" in result_keys

    def test_no_pattern_key(self, mock_redis_client):
        """Test key without pattern"""
        keys = [DbKeyPair("0", "simplekey")]
        result = get_keys_from_patterns(mock_redis_client, keys)
        
        assert len(result) == 1
        assert result[0].key == "simplekey"

    def test_mixed_patterns_and_keys(self, mock_redis_client):
        """Test mixed patterns and specific keys"""
        mock_redis_client.set(b"test:key1", b"value1")
        
        keys = [
            DbKeyPair("0", "test:*"),
            DbKeyPair("0", "specific:key"),
        ]
        result = get_keys_from_patterns(mock_redis_client, keys)
        
        assert len(result) >= 2
        result_keys = [pair.key for pair in result if isinstance(pair.key, str)]
        result_keys_bytes = [pair.key for pair in result if isinstance(pair.key, bytes)]
        assert "specific:key" in result_keys or "specific:key".encode() in result_keys_bytes

