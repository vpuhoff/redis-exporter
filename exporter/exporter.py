"""Main Redis Exporter implementation"""

import logging
import time
from typing import Any, Dict, List, Optional

import redis
from prometheus_client.core import CounterMetricFamily, GaugeMetricFamily

from .config import Options
from .info import extract_info_metrics
from .keys import extract_check_key_metrics
from .redis_client import connect_to_redis

logger = logging.getLogger(__name__)


class RedisCollector:
    """Prometheus collector for Redis metrics"""

    def __init__(self, redis_addr: str, options: Options):
        self.redis_addr = redis_addr
        self.options = options
        self.client: Optional[redis.Redis] = None
        
        # Metric maps (subset of Go version)
        self.metric_map_gauges = {
            # Server
            "uptime_in_seconds": "uptime_in_seconds",
            "process_id": "process_id",
            
            # Clients
            "connected_clients": "connected_clients",
            "blocked_clients": "blocked_clients",
            "maxclients": "max_clients",
            
            # Memory
            "used_memory": "memory_used_bytes",
            "used_memory_rss": "memory_used_rss_bytes",
            "used_memory_peak": "memory_used_peak_bytes",
            "maxmemory": "memory_max_bytes",
            "mem_fragmentation_ratio": "mem_fragmentation_ratio",
            
            # Stats
            "instantaneous_ops_per_sec": "instantaneous_ops_per_sec",
            "pubsub_channels": "pubsub_channels",
            "pubsub_patterns": "pubsub_patterns",
            
            # Replication
            "connected_slaves": "connected_slaves",
            "master_repl_offset": "master_repl_offset",
            
            # Persistence
            "loading": "loading_dump_file",
            "rdb_changes_since_last_save": "rdb_changes_since_last_save",
            "rdb_bgsave_in_progress": "rdb_bgsave_in_progress",
            "aof_enabled": "aof_enabled",
            "aof_rewrite_in_progress": "aof_rewrite_in_progress",
        }
        
        self.metric_map_counters = {
            "total_connections_received": "connections_received_total",
            "total_commands_processed": "commands_processed_total",
            "rejected_connections": "rejected_connections_total",
            "expired_keys": "expired_keys_total",
            "evicted_keys": "evicted_keys_total",
            "keyspace_hits": "keyspace_hits_total",
            "keyspace_misses": "keyspace_misses_total",
        }
        
        # Storage for metrics in current collection
        self._current_metrics: Dict[str, List[Dict[str, Any]]] = {}
    
    def _connect(self) -> redis.Redis:
        """Connect to Redis"""
        if self.client is not None:
            try:
                self.client.ping()
                return self.client
            except:
                pass
        
        self.client = connect_to_redis(
            self.redis_addr,
            password=self.options.password,
            user=self.options.user,
            connection_timeout=self.options.connection_timeout,
            set_client_name=self.options.set_client_name,
        )
        return self.client
    
    def collect(self):
        """
        Collect metrics from Redis
        
        Yields:
            MetricFamily objects
        """
        # Reset metrics
        self._current_metrics = {}
        
        start_time = time.time()
        error_msg = ""
        
        try:
            client = self._connect()
            
            # Get INFO
            info_result = client.info()
            
            # Convert to string if needed
            if isinstance(info_result, dict):
                # redis-py returns dict when decode_responses=False
                # Convert to string format
                info_string = ""
                for key, value in info_result.items():
                    if isinstance(key, bytes):
                        key = key.decode('utf-8')
                    
                    # Handle special case: db0 is a dict
                    if key.startswith('db') and isinstance(value, dict):
                        # Format as db0:keys=1,expires=0,avg_ttl=0
                        value_parts = [f"{k}={v}" for k, v in value.items()]
                        value = ",".join(value_parts)
                    
                    if isinstance(value, bytes):
                        value = value.decode('utf-8')
                    
                    info_string += f"{key}:{value}\n"
            elif isinstance(info_result, bytes):
                info_string = info_result.decode('utf-8')
            else:
                info_string = info_result
            
            # Extract INFO metrics
            extract_info_metrics(
                info_string,
                self.metric_map_gauges,
                self.metric_map_counters,
                self,
            )
            
            # Extract key metrics if configured
            if self.options.check_keys or self.options.check_single_keys:
                extract_check_key_metrics(
                    client,
                    self.options.check_keys,
                    self.options.check_single_keys,
                    self,
                )
            
            # Mark as up
            self._register_metric("up", 1.0)
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            error_msg = str(e)
            self._register_metric("up", 0.0)
        
        # Record scrape duration
        duration = time.time() - start_time
        self._register_metric("exporter_scrape_duration_seconds", duration)
        
        # Record error
        self._register_metric("exporter_last_scrape_error", 1.0 if error_msg else 0.0,
                             labels={"error": error_msg if error_msg else ""})
        
        # Yield all collected metrics
        for metric_name, metrics_list in self._current_metrics.items():
            if not metrics_list:
                continue
                
            # Determine if counter or gauge
            is_counter = metric_name.endswith("_total")
            
            # Get label names from first metric
            first_metric = metrics_list[0]
            label_names = list(first_metric['labels'].keys())
            
            # Create metric family
            if is_counter:
                family = CounterMetricFamily(
                    f"{self.options.namespace}_{metric_name}",
                    metric_name,
                    labels=label_names
                )
            else:
                family = GaugeMetricFamily(
                    f"{self.options.namespace}_{metric_name}",
                    metric_name,
                    labels=label_names
                )
            
            # Add all metrics
            for metric in metrics_list:
                label_values = list(metric['labels'].values())
                family.add_metric(label_values, metric['value'])
            
            yield family
    
    def _create_metric_descr(self, metric_name: str, labels: Optional[list] = None):
        """Create metric description if not exists (for compatibility)"""
        pass
    
    def _register_metric(self, metric_name: str, value: float, 
                        is_counter: bool = False, labels: Optional[dict] = None):
        """Register a metric value"""
        if labels is None:
            labels = {}
        
        if metric_name not in self._current_metrics:
            self._current_metrics[metric_name] = []
        
        self._current_metrics[metric_name].append({
            'labels': labels,
            'value': value,
            'is_counter': is_counter
        })
