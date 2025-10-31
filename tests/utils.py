"""Test utilities for Redis Exporter tests"""

import os
from typing import Any, Dict, Optional


def redis_available(host: str = "localhost", port: int = 6379) -> bool:
    """
    Check if Redis is available for testing
    
    Args:
        host: Redis host
        port: Redis port
    
    Returns:
        True if Redis is accessible
    """
    try:
        import redis
        
        client = redis.Redis(host=host, port=port, socket_connect_timeout=1)
        client.ping()
        return True
    except Exception:
        return False


def create_sample_info() -> str:
    """
    Create sample Redis INFO output for testing
    
    Returns:
        Sample INFO string
    """
    return """# Server
redis_version:7.0.0
redis_git_sha1:00000000
redis_git_dirty:0
redis_build_id:3b5e48647f1c1ec8
redis_mode:standalone
os:Linux 6.0.0
arch_bits:64
multiplexing_api:epoll
atomicvar_api:atomic-builtin
gcc_version:11.2.0
process_id:12345
process_supervised:no
run_id:abcd1234efgh5678
tcp_port:6379
server_time_usec:1234567890123
uptime_in_seconds:86400
uptime_in_days:1
hz:10
configured_hz:10
lru_clock:12345678
executable:/usr/local/bin/redis-server
config_file:/etc/redis/redis.conf
io_threads_active:0

# Clients
connected_clients:10
cluster_connections:0
maxclients:10000
client_recent_max_input_buffer:2
client_recent_max_output_buffer:0
blocked_clients:0
tracking_clients:0
clients_in_timeout_table:0

# Memory
used_memory:1048576
used_memory_human:1.00M
used_memory_rss:2097152
used_memory_rss_human:2.00M
used_memory_peak:2097152
used_memory_peak_human:2.00M
used_memory_peak_perc:50.00%
used_memory_overhead:819200
used_memory_startup:824208
used_memory_dataset:229376
used_memory_dataset_perc:27.91%
allocator_allocated:1048576
allocator_active:1572864
allocator_resident:2097152
total_system_memory:17179869184
total_system_memory_human:16.00G
used_memory_lua:32768
used_memory_vm_eval:0
used_memory_scripts_eval:0
number_of_cached_scripts:0
number_of_functions:0
number_of_libraries:0
used_memory_vm_functions:32768
used_memory_vm_total:65536
used_memory_vm_total_human:64.00K
used_memory_functions:0
used_memory_scripts:0
used_memory_scripts_human:0B
maxmemory:0
maxmemory_human:0B
maxmemory_policy:noeviction
allocator_frag_ratio:1.50
allocator_frag_bytes:524288
allocator_rss_ratio:1.33
allocator_rss_bytes:524288
rss_overhead_ratio:1.00
rss_overhead_bytes:0
mem_fragmentation_ratio:2.00
mem_fragmentation_bytes:1048576
mem_not_counted_for_evict:0
mem_replication_backlog:0
mem_total_replication_buffers:0
mem_clients_slaves:0
mem_clients_normal:415440
mem_clients_acl:0
mem_aof_buffer:0
mem_allocator:jemalloc-5.3.0
active_defrag_running:0
lazyfree_pending_objects:0
lazyfreed_objects:0

# Persistence
loading:0
async_loading:0
current_cow_peak:0
current_cow_size:0
current_cow_size_age:0
current_fork_perc:0.00
current_save_keys_processed:0
current_save_keys_total:0
rdb_changes_since_last_save:0
rdb_bgsave_in_progress:0
rdb_last_save_time:1234567890
rdb_last_bgsave_status:ok
rdb_last_bgsave_time_sec:0
rdb_current_bgsave_time_sec:-1
rdb_save_incremental_fsync_yes:0
rdb_save_incremental_fsync_no:0
rdb_last_cow_size:0
aof_enabled:1
aof_rewrite_in_progress:0
aof_rewrite_scheduled:0
aof_last_rewrite_time_sec:0
aof_current_rewrite_time_sec:-1
aof_last_bgrewrite_status:ok
aof_last_write_status:ok
aof_last_cow_size:0
aof_base_size:100
aof_pending_rewrite:0
aof_buffer_length:0
aof_rewrite_buffer_length:0
aof_pending_bio_fsync:0
aof_last_active_write_time_usec:1234567890123
aof_last_write_time_usec:1234567890123
has_active_aof_file:1
loading_start_time:0
loading_total_bytes:0
loading_loaded_bytes:0
loading_loaded_perc:0
loading_eta_seconds:0
loading_started:0
loading_is_async:0
loading_loading:0
loading_finished:0
module_fork_in_progress:0
module_fork_last_cow_size:0
process_fork_children:5
process_fork_children_wait_time_sec:0.1
process_fork_children_sum_processor_time_sec:0.5
process_fork_children_sum_page_faults:1000
process_fork_children_sum_page_faults_perc:0.1
copy_on_write_memory:100000
copy_on_write_memory_perc:0.1

# Stats
total_connections_received:1000
total_commands_processed:50000
instantaneous_ops_per_sec:10
total_net_input_bytes:100000
total_net_output_bytes:500000
instantaneous_input_kbps:0.1
instantaneous_output_kbps:0.5
rejected_connections:5
sync_full:0
sync_partial_ok:0
sync_partial_err:0
expired_keys:100
expired_stale_perc:0.1
expired_time_cap_reached_count:0
expire_cycle_cpu_milliseconds:10
evicted_keys:50
keyspace_hits:20000
keyspace_misses:5000
pubsub_channels:3
pubsub_patterns:5
latest_fork_usec:1500
total_forks:5
migrate_cached_sockets:0
slave_expires_tracked_keys:0
active_defrag_hits:0
active_defrag_misses:0
active_defrag_key_hits:0
active_defrag_key_misses:0
total_active_defrag_time:0
current_active_defrag_time:0
tracking_total_keys:0
tracking_total_items:0
tracking_total_prefixes:0
unexpected_error_replies:0
total_reads_processed:5000
total_writes_processed:45000
io_threaded_reads_processed:0
io_threaded_writes_processed:0
reply_buffer_shrinks:0
reply_buffer_expands:0

# Replication
role:master
connected_slaves:2
slave0:ip=192.168.1.10,port=6379,state=online,offset=1000,lag=1
slave1:ip=192.168.1.11,port=6379,state=online,offset=1000,lag=0
master_failover_state:no-failover
master_replid:abcd1234efgh5678
master_replid2:0000000000000000
master_repl_offset:1000
second_repl_offset:-1
repl_backlog_active:1
repl_backlog_size:1048576
repl_backlog_first_byte_offset:0
repl_backlog_histlen:1000

# CPU
used_cpu_sys:10.5
used_cpu_user:20.3
used_cpu_sys_children:5.0
used_cpu_user_children:15.0
used_cpu_sys_main_thread:10.0
used_cpu_user_main_thread:20.0

# Modules

# Errorstats
errorstat_ERR:count=10
errorstat_WRONGTYPE:count=5

# Cluster
cluster_enabled:0

# Keyspace
db0:keys=1000,expires=100,avg_ttl=3600000
db1:keys=500,expires=50,avg_ttl=1800000

# Commandstats
cmdstat_get:calls=10000,usec=50000,usec_per_call=5.00
cmdstat_set:calls=5000,usec=25000,usec_per_call=5.00
cmdstat_del:calls=1000,usec=10000,usec_per_call=10.00,rejected_calls=0,failed_calls=0

# Latencystats

# Eventloop
eventloop_duration_aof_fsync_avg:100
eventloop_cmd_getsets_processed:20
eventloop_cmd_all_processed:50

# Slowlog
slowlog_count:10
slowlog_last_id:1

# Latency
latency_latest_sum_score:100
latency_stats_readers_count:0
"""


def create_sample_info_dict() -> Dict[str, Any]:
    """
    Create sample Redis INFO output as dictionary
    
    Returns:
        Sample INFO as dictionary
    """
    return {
        "redis_version": "7.0.0",
        "redis_mode": "standalone",
        "os": "Linux 6.0.0",
        "process_id": 12345,
        "run_id": "abcd1234efgh5678",
        "tcp_port": 6379,
        "uptime_in_seconds": 86400,
        "connected_clients": 10,
        "maxclients": 10000,
        "blocked_clients": 0,
        "used_memory": 1048576,
        "used_memory_rss": 2097152,
        "used_memory_peak": 2097152,
        "maxmemory": 0,
        "mem_fragmentation_ratio": 2.0,
        "loading": 0,
        "rdb_changes_since_last_save": 0,
        "rdb_bgsave_in_progress": 0,
        "aof_enabled": 1,
        "aof_rewrite_in_progress": 0,
        "total_connections_received": 1000,
        "total_commands_processed": 50000,
        "instantaneous_ops_per_sec": 10,
        "rejected_connections": 5,
        "expired_keys": 100,
        "evicted_keys": 50,
        "keyspace_hits": 20000,
        "keyspace_misses": 5000,
        "pubsub_channels": 3,
        "pubsub_patterns": 5,
        "latest_fork_usec": 1500,
        "role": "master",
        "connected_slaves": 2,
        "master_repl_offset": 1000,
        "db0": {"keys": 1000, "expires": 100, "avg_ttl": 3600000},
    }


def create_mock_redis_client():
    """
    Create a mock Redis client for testing
    
    Returns:
        Mock Redis client
    """
    import fakeredis
    
    return fakeredis.FakeStrictRedis(decode_responses=False)

