"""
Performance monitoring and metrics collection for JustEat application
"""

import time
import psutil
import logging
from datetime import datetime, timedelta
from flask import request, g, current_app
from functools import wraps
from collections import defaultdict, deque
import threading

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Performance monitoring system"""

    def __init__(self):
        self.metrics = defaultdict(list)
        self.request_times = deque(maxlen=1000)
        self.error_counts = defaultdict(int)
        self.active_connections = 0
        self.lock = threading.Lock()

    def record_request_time(self, endpoint, method, duration):
        """Record request duration"""
        with self.lock:
            self.request_times.append({
                'endpoint': endpoint,
                'method': method,
                'duration': duration,
                'timestamp': datetime.utcnow()
            })

    def record_error(self, endpoint, error_type):
        """Record error occurrence"""
        with self.lock:
            self.error_counts[f"{endpoint}_{error_type}"] += 1

    def get_system_metrics(self):
        """Get system performance metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)

            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used = memory.used / (1024**3)  # GB
            memory_total = memory.total / (1024**3)  # GB

            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            disk_used = disk.used / (1024**3)  # GB
            disk_total = disk.total / (1024**3)  # GB

            # Network I/O
            network = psutil.net_io_counters()
            bytes_sent = network.bytes_sent / (1024**2)  # MB
            bytes_recv = network.bytes_recv / (1024**2)  # MB

            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'memory_used_gb': round(memory_used, 2),
                'memory_total_gb': round(memory_total, 2),
                'disk_percent': round(disk_percent, 2),
                'disk_used_gb': round(disk_used, 2),
                'disk_total_gb': round(disk_total, 2),
                'network_sent_mb': round(bytes_sent, 2),
                'network_recv_mb': round(bytes_recv, 2),
                'active_connections': self.active_connections,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {str(e)}")
            return {}

    def get_request_metrics(self, minutes=60):
        """Get request performance metrics"""
        with self.lock:
            cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
            recent_requests = [
                req for req in self.request_times
                if req['timestamp'] > cutoff_time
            ]

            if not recent_requests:
                return {
                    'total_requests': 0,
                    'avg_response_time': 0,
                    'max_response_time': 0,
                    'min_response_time': 0,
                    'requests_per_minute': 0
                }

            durations = [req['duration'] for req in recent_requests]

            return {
                'total_requests': len(recent_requests),
                'avg_response_time': round(sum(durations) / len(durations), 3),
                'max_response_time': round(max(durations), 3),
                'min_response_time': round(min(durations), 3),
                'requests_per_minute': round(len(recent_requests) / minutes, 2)
            }

    def get_error_metrics(self):
        """Get error metrics"""
        with self.lock:
            return dict(self.error_counts)

    def get_endpoint_metrics(self, minutes=60):
        """Get metrics by endpoint"""
        with self.lock:
            cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
            recent_requests = [
                req for req in self.request_times
                if req['timestamp'] > cutoff_time
            ]

            endpoint_stats = defaultdict(lambda: {
                'count': 0,
                'total_time': 0,
                'avg_time': 0,
                'max_time': 0,
                'min_time': float('inf')
            })

            for req in recent_requests:
                endpoint = req['endpoint']
                duration = req['duration']

                stats = endpoint_stats[endpoint]
                stats['count'] += 1
                stats['total_time'] += duration
                stats['max_time'] = max(stats['max_time'], duration)
                stats['min_time'] = min(stats['min_time'], duration)

            # Calculate averages
            for stats in endpoint_stats.values():
                if stats['count'] > 0:
                    stats['avg_time'] = round(
                        stats['total_time'] / stats['count'], 3)
                    stats['max_time'] = round(stats['max_time'], 3)
                    stats['min_time'] = round(stats['min_time'], 3)
                else:
                    stats['min_time'] = 0

            return dict(endpoint_stats)

    def get_health_status(self):
        """Get overall system health status"""
        system_metrics = self.get_system_metrics()
        request_metrics = self.get_request_metrics()

        health_status = {
            'status': 'healthy',
            'issues': [],
            'timestamp': datetime.utcnow().isoformat()
        }

        # Check CPU usage
        if system_metrics.get('cpu_percent', 0) > 80:
            health_status['status'] = 'warning'
            health_status['issues'].append('High CPU usage')

        # Check memory usage
        if system_metrics.get('memory_percent', 0) > 85:
            health_status['status'] = 'warning'
            health_status['issues'].append('High memory usage')

        # Check disk usage
        if system_metrics.get('disk_percent', 0) > 90:
            health_status['status'] = 'critical'
            health_status['issues'].append('High disk usage')

        # Check response times
        if request_metrics.get('avg_response_time', 0) > 2.0:
            health_status['status'] = 'warning'
            health_status['issues'].append('Slow response times')

        # Check error rate
        error_metrics = self.get_error_metrics()
        total_errors = sum(error_metrics.values())
        if total_errors > 10:
            health_status['status'] = 'warning'
            health_status['issues'].append('High error rate')

        return health_status


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


def monitor_performance(f):
    """Decorator to monitor function performance"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()

        try:
            result = f(*args, **kwargs)
            duration = time.time() - start_time

            # Record successful request
            endpoint = request.endpoint or 'unknown'
            method = request.method
            performance_monitor.record_request_time(endpoint, method, duration)

            return result

        except Exception as e:
            duration = time.time() - start_time

            # Record error
            endpoint = request.endpoint or 'unknown'
            error_type = type(e).__name__
            performance_monitor.record_error(endpoint, error_type)

            logger.error(f"Error in {endpoint}: {str(e)}")
            raise

    return decorated_function


def track_database_queries(f):
    """Decorator to track database query performance"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()

        try:
            result = f(*args, **kwargs)
            duration = time.time() - start_time

            # Log slow queries
            if duration > 1.0:  # Queries taking more than 1 second
                logger.warning(
                    f"Slow database query in {f.__name__}: {duration:.3f}s")

            return result

        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Database error in {
                    f.__name__}: {
                    str(e)} (took {
                    duration:.3f}s)")
            raise

    return decorated_function


class DatabaseMonitor:
    """Database performance monitoring"""

    def __init__(self):
        self.query_times = deque(maxlen=1000)
        self.slow_queries = []
        self.query_counts = defaultdict(int)

    def record_query(self, query, duration):
        """Record database query performance"""
        self.query_times.append({
            'query': str(query),
            'duration': duration,
            'timestamp': datetime.utcnow()
        })

        self.query_counts[query] += 1

        # Track slow queries
        if duration > 1.0:
            self.slow_queries.append({
                'query': str(query),
                'duration': duration,
                'timestamp': datetime.utcnow()
            })

    def get_query_metrics(self, minutes=60):
        """Get database query metrics"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        recent_queries = [
            q for q in self.query_times
            if q['timestamp'] > cutoff_time
        ]

        if not recent_queries:
            return {
                'total_queries': 0,
                'avg_query_time': 0,
                'max_query_time': 0,
                'slow_queries': 0
            }

        durations = [q['duration'] for q in recent_queries]
        slow_count = len([d for d in durations if d > 1.0])

        return {
            'total_queries': len(recent_queries),
            'avg_query_time': round(sum(durations) / len(durations), 3),
            'max_query_time': round(max(durations), 3),
            'slow_queries': slow_count,
            'queries_per_minute': round(len(recent_queries) / minutes, 2)
        }

    def get_slow_queries(self, limit=10):
        """Get recent slow queries"""
        return sorted(
            self.slow_queries,
            key=lambda x: x['duration'],
            reverse=True
        )[:limit]


# Global database monitor instance
db_monitor = DatabaseMonitor()


class CacheMonitor:
    """Cache performance monitoring"""

    def __init__(self):
        self.hit_counts = defaultdict(int)
        self.miss_counts = defaultdict(int)
        self.cache_operations = deque(maxlen=1000)

    def record_cache_hit(self, key):
        """Record cache hit"""
        self.hit_counts[key] += 1
        self.cache_operations.append({
            'operation': 'hit',
            'key': key,
            'timestamp': datetime.utcnow()
        })

    def record_cache_miss(self, key):
        """Record cache miss"""
        self.miss_counts[key] += 1
        self.cache_operations.append({
            'operation': 'miss',
            'key': key,
            'timestamp': datetime.utcnow()
        })

    def get_cache_metrics(self, minutes=60):
        """Get cache performance metrics"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        recent_operations = [
            op for op in self.cache_operations
            if op['timestamp'] > cutoff_time
        ]

        hits = len([op for op in recent_operations if op['operation'] == 'hit'])
        misses = len(
            [op for op in recent_operations if op['operation'] == 'miss'])
        total = hits + misses

        hit_rate = (hits / total * 100) if total > 0 else 0

        return {
            'total_operations': total,
            'hits': hits,
            'misses': misses,
            'hit_rate': round(hit_rate, 2),
            'operations_per_minute': round(total / minutes, 2)
        }


# Global cache monitor instance
cache_monitor = CacheMonitor()


def get_comprehensive_metrics():
    """Get comprehensive system metrics"""
    return {
        'system': performance_monitor.get_system_metrics(),
        'requests': performance_monitor.get_request_metrics(),
        'errors': performance_monitor.get_error_metrics(),
        'endpoints': performance_monitor.get_endpoint_metrics(),
        'database': db_monitor.get_query_metrics(),
        'cache': cache_monitor.get_cache_metrics(),
        'health': performance_monitor.get_health_status(),
        'timestamp': datetime.utcnow().isoformat()
    }


def log_performance_metrics():
    """Log performance metrics (for scheduled tasks)"""
    metrics = get_comprehensive_metrics()

    logger.info(f"Performance Metrics: {metrics}")

    # Log warnings for critical metrics
    if metrics['health']['status'] != 'healthy':
        logger.warning(f"System Health Issues: {metrics['health']['issues']}")

    if metrics['system'].get('cpu_percent', 0) > 80:
        logger.warning(f"High CPU usage: {metrics['system']['cpu_percent']}%")

    if metrics['system'].get('memory_percent', 0) > 85:
        logger.warning(
            f"High memory usage: {metrics['system']['memory_percent']}%")

    if metrics['requests'].get('avg_response_time', 0) > 2.0:
        logger.warning(
            f"Slow response times: {
                metrics['requests']['avg_response_time']}s")

# Flask middleware for automatic performance monitoring


def init_performance_monitoring(app):
    """Initialize performance monitoring for Flask app"""

    @app.before_request
    def before_request():
        g.start_time = time.time()
        performance_monitor.active_connections += 1

    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            endpoint = request.endpoint or 'unknown'
            method = request.method

            performance_monitor.record_request_time(endpoint, method, duration)

            # Add performance headers
            response.headers['X-Response-Time'] = f"{duration:.3f}s"

        performance_monitor.active_connections = max(
            0, performance_monitor.active_connections - 1)
        return response

    @app.errorhandler(Exception)
    def handle_exception(e):
        endpoint = request.endpoint or 'unknown'
        error_type = type(e).__name__
        performance_monitor.record_error(endpoint, error_type)

        logger.error(f"Unhandled exception in {endpoint}: {str(e)}")
        raise e
