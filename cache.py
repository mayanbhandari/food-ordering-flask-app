"""
Caching system for JustEat application
"""

import json
import pickle
from datetime import datetime, timedelta
from flask import current_app
import logging

logger = logging.getLogger(__name__)


class Cache:
    """Simple in-memory cache implementation"""

    def __init__(self):
        self._cache = {}
        self._expiry = {}

    def get(self, key):
        """Get value from cache"""
        if key in self._cache:
            if key in self._expiry and datetime.now() > self._expiry[key]:
                # Expired, remove from cache
                del self._cache[key]
                del self._expiry[key]
                return None
            return self._cache[key]
        return None

    def set(self, key, value, expiry_seconds=300):
        """Set value in cache with expiry"""
        self._cache[key] = value
        if expiry_seconds > 0:
            self._expiry[key] = datetime.now(
            ) + timedelta(seconds=expiry_seconds)
        else:
            # Remove from expiry if it exists
            self._expiry.pop(key, None)

    def delete(self, key):
        """Delete key from cache"""
        self._cache.pop(key, None)
        self._expiry.pop(key, None)

    def clear(self):
        """Clear all cache"""
        self._cache.clear()
        self._expiry.clear()

    def keys(self):
        """Get all cache keys"""
        return list(self._cache.keys())

    def size(self):
        """Get cache size"""
        return len(self._cache)


# Global cache instance
cache = Cache()


def cache_key(*args, **kwargs):
    """Generate cache key from arguments"""
    key_parts = []
    for arg in args:
        if hasattr(arg, 'id'):
            key_parts.append(f"{arg.__class__.__name__}_{arg.id}")
        else:
            key_parts.append(str(arg))

    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}_{v}")

    return "_".join(key_parts)


def cached(expiry_seconds=300):
    """Decorator to cache function results"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generate cache key
            key = f"{func.__name__}_{cache_key(*args, **kwargs)}"

            # Try to get from cache
            result = cache.get(key)
            if result is not None:
                logger.debug(f"Cache hit for {key}")
                return result

            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(key, result, expiry_seconds)
            logger.debug(f"Cached result for {key}")

            return result
        return wrapper
    return decorator


def invalidate_cache(pattern=None):
    """Invalidate cache entries matching pattern"""
    if pattern is None:
        cache.clear()
        return

    keys_to_delete = []
    for key in cache.keys():
        if pattern in key:
            keys_to_delete.append(key)

    for key in keys_to_delete:
        cache.delete(key)

    logger.info(
        f"Invalidated {
            len(keys_to_delete)} cache entries matching '{pattern}'")

# Cache decorators for specific use cases

def cache_restaurant_data(expiry_seconds=600):
    """Cache restaurant data"""
    return cached(expiry_seconds)


def cache_menu_data(expiry_seconds=300):
    """Cache menu data"""
    return cached(expiry_seconds)


def cache_user_data(expiry_seconds=1800):
    """Cache user data"""
    return cached(expiry_seconds)


def cache_analytics_data(expiry_seconds=3600):
    """Cache analytics data"""
    return cached(expiry_seconds)

# Cache management functions


def get_cache_stats():
    """Get cache statistics"""
    return {
        'size': cache.size(),
        'keys': cache.keys(),
        'memory_usage': len(pickle.dumps(cache._cache))
    }


def warm_cache():
    """Warm up cache with frequently accessed data"""
    logger.info("Warming up cache...")

    try:
        from models import Restaurant, MenuItem

        # Cache active restaurants
        restaurants = Restaurant.query.filter_by(is_active=True).all()
        for restaurant in restaurants:
            key = f"restaurant_{restaurant.id}"
            cache.set(key, restaurant, 600)

        # Cache popular menu items
        for restaurant in restaurants:
            menu_items = MenuItem.query.filter_by(
                restaurant_id=restaurant.id,
                is_available=True
            ).all()
            key = f"menu_items_{restaurant.id}"
            cache.set(key, menu_items, 300)

        logger.info(f"Cache warmed up with {len(restaurants)} restaurants")

    except Exception as e:
        logger.error(f"Error warming up cache: {str(e)}")


def clear_restaurant_cache(restaurant_id):
    """Clear cache for specific restaurant"""
    patterns = [
        f"restaurant_{restaurant_id}",
        f"menu_items_{restaurant_id}",
        f"analytics_{restaurant_id}",
        f"reviews_{restaurant_id}"
    ]

    for pattern in patterns:
        invalidate_cache(pattern)


def clear_user_cache(user_id):
    """Clear cache for specific user"""
    patterns = [
        f"user_{user_id}",
        f"orders_{user_id}",
        f"cart_{user_id}",
        f"recommendations_{user_id}"
    ]

    for pattern in patterns:
        invalidate_cache(pattern)

# Redis integration (for production)


class RedisCache:
    """Redis-based cache implementation"""

    def __init__(self, redis_client=None):
        self.redis = redis_client
        self.default_expiry = 300

    def get(self, key):
        """Get value from Redis cache"""
        if not self.redis:
            return None

        try:
            value = self.redis.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error(f"Redis get error: {str(e)}")

        return None

    def set(self, key, value, expiry_seconds=None):
        """Set value in Redis cache"""
        if not self.redis:
            return False

        try:
            expiry = expiry_seconds or self.default_expiry
            self.redis.setex(key, expiry, json.dumps(value, default=str))
            return True
        except Exception as e:
            logger.error(f"Redis set error: {str(e)}")
            return False

    def delete(self, key):
        """Delete key from Redis cache"""
        if not self.redis:
            return False

        try:
            self.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis delete error: {str(e)}")
            return False

    def clear(self):
        """Clear all cache"""
        if not self.redis:
            return False

        try:
            self.redis.flushdb()
            return True
        except Exception as e:
            logger.error(f"Redis clear error: {str(e)}")
            return False

# Cache configuration


def configure_cache(use_redis=False, redis_url=None):
    """Configure cache system"""
    global cache

    if use_redis and redis_url:
        try:
            import redis
            redis_client = redis.from_url(redis_url)
            cache = RedisCache(redis_client)
            logger.info("Using Redis cache")
        except ImportError:
            logger.warning("Redis not available, using in-memory cache")
        except Exception as e:
            logger.error(f"Redis connection failed: {str(e)}")
            logger.info("Falling back to in-memory cache")
    else:
        logger.info("Using in-memory cache")

# Cache middleware


def cache_middleware(expiry_seconds=300):
    """Flask middleware for caching responses"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generate cache key from request
            from flask import request
            key = f"response_{
                func.__name__}_{
                hash(
                    str(
                        request.args) + str(
                        request.json))}"

            # Try to get from cache
            result = cache.get(key)
            if result is not None:
                return result

            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(key, result, expiry_seconds)

            return result
        return wrapper
    return decorator
