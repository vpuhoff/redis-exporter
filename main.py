"""Redis Exporter for Prometheus - Main entry point"""

import argparse
import logging
import signal
import sys
import time
from http.server import HTTPServer
from threading import Thread
from typing import Optional

from prometheus_client import REGISTRY, start_http_server

from exporter.config import Options
from exporter.exporter import RedisCollector


# Build info
BUILD_VERSION = "1.0.0"
BUILD_DATE = "<<< filled in by build >>>"
BUILD_COMMIT_SHA = "<<< filled in by build >>>"


def setup_logging(log_level: str, log_format: str = "txt"):
    """
    Setup logging configuration
    
    Args:
        log_level: Log level (DEBUG, INFO, WARNING, ERROR)
        log_format: Log format (txt or json)
    """
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    if log_format == "json":
        logging.basicConfig(
            level=numeric_level,
            format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}',
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    else:
        logging.basicConfig(
            level=numeric_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Prometheus Exporter for Redis")
    
    # Redis connection
    parser.add_argument(
        "--redis.addr",
        dest="redis_addr",
        default=Options.from_env().redis_addr,
        help="Address of the Redis instance to scrape",
    )
    parser.add_argument(
        "--redis.user",
        dest="redis_user",
        default=Options.from_env().user,
        help="User name to use for authentication (Redis ACL for Redis 6.0 and newer)",
    )
    parser.add_argument(
        "--redis.password",
        dest="redis_password",
        default=Options.from_env().password,
        help="Password of the Redis instance to scrape",
    )
    
    # Metrics configuration
    parser.add_argument(
        "--namespace",
        dest="namespace",
        default=Options.from_env().namespace,
        help="Namespace for metrics",
    )
    
    # Key checking
    parser.add_argument(
        "--check-keys",
        dest="check_keys",
        default=Options.from_env().check_keys,
        help="Comma separated list of key-patterns to export value and length/size",
    )
    parser.add_argument(
        "--check-single-keys",
        dest="check_single_keys",
        default=Options.from_env().check_single_keys,
        help="Comma separated list of single keys to export value and length/size",
    )
    
    # Connection settings
    parser.add_argument(
        "--connection-timeout",
        dest="connection_timeout",
        type=float,
        default=Options.from_env().connection_timeout,
        help="Timeout for connection to Redis instance in seconds",
    )
    parser.add_argument(
        "--set-client-name",
        dest="set_client_name",
        action="store_true",
        default=True,
        help="Whether to set client name to redis_exporter",
    )
    parser.add_argument(
        "--no-set-client-name",
        dest="set_client_name",
        action="store_false",
        help="Disable setting client name",
    )
    
    # HTTP server
    parser.add_argument(
        "--web.listen-address",
        dest="web_listen_address",
        default=Options.from_env().web_listen_address,
        help="Address to listen on for web interface and telemetry",
    )
    
    # Logging
    parser.add_argument(
        "--log-level",
        dest="log_level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Set log level",
    )
    parser.add_argument(
        "--log-format",
        dest="log_format",
        default="txt",
        choices=["txt", "json"],
        help="Log format",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output (sets log level to DEBUG)",
    )
    
    # Version
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version information and exit",
    )
    
    args = parser.parse_args()
    
    # Override log level if debug is set
    if args.debug:
        args.log_level = "DEBUG"
    
    return args


def main():
    """Main entry point"""
    args = parse_args()
    
    # Show version
    if args.version:
        print(f"Redis Metrics Exporter {BUILD_VERSION}")
        print(f"build date: {BUILD_DATE}")
        print(f"sha1: {BUILD_COMMIT_SHA}")
        print(f"Python: {sys.version}")
        return 0
    
    # Setup logging
    setup_logging(args.log_level, args.log_format)
    logger = logging.getLogger(__name__)
    
    if args.debug:
        logger.debug("Enabling debug output")
    logger.info(f"Setting log level to {args.log_level}")
    
    # Log build info
    logger.info(f"Redis Metrics Exporter {BUILD_VERSION}")
    logger.info(f"build date: {BUILD_DATE}")
    logger.info(f"sha1: {BUILD_COMMIT_SHA}")
    logger.info(f"Python: {sys.version}")
    
    # Create options
    options = Options(
        redis_addr=args.redis_addr,
        user=args.redis_user,
        password=args.redis_password,
        namespace=args.namespace,
        check_keys=args.check_keys,
        check_single_keys=args.check_single_keys,
        connection_timeout=args.connection_timeout,
        set_client_name=args.set_client_name,
        web_listen_address=args.web_listen_address,
    )
    
    logger.debug(f"Options: {options}")
    logger.info(f"Configured redis addr: {options.redis_addr}")
    
    # Create exporter
    collector = RedisCollector(options.redis_addr, options)
    
    # Register collector with Prometheus
    REGISTRY.register(collector)
    
    # Parse listen address
    listen_addr = options.web_listen_address
    if listen_addr.startswith(":"):
        # Just port specified
        host = "0.0.0.0"
        port = int(listen_addr[1:]) if listen_addr[1:] else 9121
    else:
        # Host:port specified
        if ":" in listen_addr:
            host, port_str = listen_addr.rsplit(":", 1)
            port = int(port_str)
        else:
            host = listen_addr
            port = 9121
    
    # Start HTTP server
    logger.info(f"Providing metrics at http://{host}:{port}/metrics")
    start_http_server(port, addr=host)
    
    # Wait for interrupt signal
    try:
        while True:
            signal.pause()
    except KeyboardInterrupt:
        logger.info("Received SIGINT, exiting")
    except SystemExit:
        logger.info("Received SIGTERM, exiting")
    finally:
        logger.info("Server shut down gracefully")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

