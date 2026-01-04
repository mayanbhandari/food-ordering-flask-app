"""
Middleware and decorators for JustEat application
"""

import time
from functools import wraps
from flask import request, jsonify, session, redirect, url_for, flash
from flask_login import current_user
import logging

logger = logging.getLogger(__name__)


def customer_required(f):
    """Decorator to ensure only customers can access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))

        if current_user.role != 'customer':
            flash('Access denied. Customer login required.', 'error')
            return redirect(url_for('auth.login'))

        return f(*args, **kwargs)
    return decorated_function


def restaurant_owner_required(f):
    """Decorator to ensure only restaurant owners can access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))

        if current_user.role != 'restaurant_owner':
            flash('Access denied. Restaurant owner login required.', 'error')
            return redirect(url_for('auth.login'))

        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to ensure only admin users can access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))

        if current_user.role != 'admin':
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('auth.login'))

        return f(*args, **kwargs)
    return decorated_function


def json_response(f):
    """Decorator to ensure JSON responses"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            result = f(*args, **kwargs)
            if isinstance(result, dict):
                return jsonify(result)
            return result
        except Exception as e:
            logger.error(f"Error in JSON response: {str(e)}")
            return jsonify(
                {'success': False, 'message': 'Internal server error'}), 500
    return decorated_function


def rate_limit(max_requests=100, window=3600):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Simple rate limiting based on IP
            client_ip = request.remote_addr
            current_time = int(time.time())

            # This is a simplified implementation
            # In production, use Redis or similar for rate limiting
            if not hasattr(rate_limit, 'requests'):
                rate_limit.requests = {}

            if client_ip not in rate_limit.requests:
                rate_limit.requests[client_ip] = []

            # Clean old requests
            rate_limit.requests[client_ip] = [
                req_time for req_time in rate_limit.requests[client_ip]
                if current_time - req_time < window
            ]

            # Check if limit exceeded
            if len(rate_limit.requests[client_ip]) >= max_requests:
                return jsonify({'error': 'Rate limit exceeded'}), 429

            # Add current request
            rate_limit.requests[client_ip].append(current_time)

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def validate_json(required_fields=None):
    """Decorator to validate JSON request data"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify(
                    {'error': 'Content-Type must be application/json'}), 400

            data = request.get_json()
            if not data:
                return jsonify({'error': 'No JSON data provided'}), 400

            if required_fields:
                missing_fields = [
                    field for field in required_fields if field not in data]
                if missing_fields:
                    return jsonify({
                        'error': f'Missing required fields: {", ".join(missing_fields)}'
                    }), 400

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def log_request(f):
    """Decorator to log HTTP requests"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()

        # Log request
        logger.info(
            f"Request: {
                request.method} {
                request.path} from {
                request.remote_addr}")

        # Execute function
        response = f(*args, **kwargs)

        # Log response time
        duration = time.time() - start_time
        logger.info(
            f"Response: {request.method} {request.path} - {duration:.3f}s")

        return response
    return decorated_function


def cache_response(timeout=300):
    """Decorator to cache response (simplified implementation)"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Simple cache key based on function name and arguments
            cache_key = f"{f.__name__}_{hash(str(args) + str(kwargs))}"

            # This is a simplified implementation
            # In production, use Redis or similar for caching
            if not hasattr(cache_response, 'cache'):
                cache_response.cache = {}

            current_time = time.time()

            # Check if cached response exists and is not expired
            if cache_key in cache_response.cache:
                cached_data, cached_time = cache_response.cache[cache_key]
                if current_time - cached_time < timeout:
                    return cached_data

            # Execute function and cache result
            result = f(*args, **kwargs)
            cache_response.cache[cache_key] = (result, current_time)

            return result
        return decorated_function
    return decorator


def handle_errors(f):
    """Decorator to handle common errors"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            logger.error(f"ValueError in {f.__name__}: {str(e)}")
            return jsonify({'error': 'Invalid input data'}), 400
        except PermissionError as e:
            logger.error(f"PermissionError in {f.__name__}: {str(e)}")
            return jsonify({'error': 'Permission denied'}), 403
        except Exception as e:
            logger.error(f"Unexpected error in {f.__name__}: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
    return decorated_function


def require_https(f):
    """Decorator to require HTTPS in production"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.is_secure or request.headers.get(
                'X-Forwarded-Proto') == 'https':
            return f(*args, **kwargs)
        else:
            return redirect(request.url.replace('http://', 'https://'))
    return decorated_function


def track_user_activity(activity_type):
    """Decorator to track user activity"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.is_authenticated:
                from utils import log_user_activity
                log_user_activity(current_user.id, activity_type, request.path)

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def validate_csrf(f):
    """Decorator to validate CSRF token"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            # CSRF validation is handled by Flask-WTF
            # This is just a placeholder for additional validation
            pass

        return f(*args, **kwargs)
    return decorated_function


def sanitize_input(f):
    """Decorator to sanitize input data"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.is_json:
            data = request.get_json()
            if data:
                from utils import sanitize_input
                # Sanitize string values in JSON data
                for key, value in data.items():
                    if isinstance(value, str):
                        data[key] = sanitize_input(value)

        return f(*args, **kwargs)
    return decorated_function


# Import time module for rate limiting and logging
