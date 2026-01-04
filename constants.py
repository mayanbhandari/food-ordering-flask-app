"""
Constants for JustEat application
"""

# Application Constants
APP_NAME = "JustEat"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Food Delivery Application"

# User Roles
CUSTOMER_ROLE = "customer"
RESTAURANT_OWNER_ROLE = "restaurant_owner"
ADMIN_ROLE = "admin"

# Order Statuses
ORDER_STATUS_PENDING = "pending"
ORDER_STATUS_CONFIRMED = "confirmed"
ORDER_STATUS_PREPARING = "preparing"
ORDER_STATUS_READY = "ready"
ORDER_STATUS_DELIVERED = "delivered"
ORDER_STATUS_CANCELLED = "cancelled"

# Order Status Options
ORDER_STATUS_CHOICES = [
    (ORDER_STATUS_PENDING, "Pending"),
    (ORDER_STATUS_CONFIRMED, "Confirmed"),
    (ORDER_STATUS_PREPARING, "Preparing"),
    (ORDER_STATUS_READY, "Ready"),
    (ORDER_STATUS_DELIVERED, "Delivered"),
    (ORDER_STATUS_CANCELLED, "Cancelled")
]

# Feedback Statuses
FEEDBACK_STATUS_OPEN = "open"
FEEDBACK_STATUS_IN_PROGRESS = "in_progress"
FEEDBACK_STATUS_RESOLVED = "resolved"

# Feedback Status Options
FEEDBACK_STATUS_CHOICES = [
    (FEEDBACK_STATUS_OPEN, "Open"),
    (FEEDBACK_STATUS_IN_PROGRESS, "In Progress"),
    (FEEDBACK_STATUS_RESOLVED, "Resolved")
]

# Cuisine Types
CUISINE_TYPES = [
    "Italian",
    "Chinese",
    "Indian",
    "Mexican",
    "American",
    "Japanese",
    "Thai",
    "Mediterranean",
    "Fast Food",
    "Desserts"
]

# Menu Item Categories
MENU_CATEGORIES = [
    "Appetizers",
    "Main Course",
    "Desserts",
    "Beverages",
    "Salads",
    "Soups",
    "Pizza",
    "Pasta",
    "Sandwiches",
    "Sides"
]

# Rating Scale
MIN_RATING = 1
MAX_RATING = 5
DEFAULT_RATING = 0

# Price Limits
MIN_PRICE = 0.01
MAX_PRICE = 999.99

# Quantity Limits
MIN_QUANTITY = 1
MAX_QUANTITY = 99

# Preparation Time Limits
MIN_PREPARATION_TIME = 1  # minutes
MAX_PREPARATION_TIME = 120  # minutes

# Popular Item Threshold
POPULAR_ITEM_THRESHOLD = 10  # orders per day

# Pagination
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 50

# String Length Limits
MAX_USERNAME_LENGTH = 20
MIN_USERNAME_LENGTH = 4
MAX_EMAIL_LENGTH = 120
MAX_PHONE_LENGTH = 20
MAX_RESTAURANT_NAME_LENGTH = 100
MAX_MENU_ITEM_NAME_LENGTH = 100
MAX_DESCRIPTION_LENGTH = 500
MAX_COMMENT_LENGTH = 1000
MAX_SUBJECT_LENGTH = 200
MAX_MESSAGE_LENGTH = 2000
MAX_ADDRESS_LENGTH = 500

# File Upload Limits
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Time Formats
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DISPLAY_DATE_FORMAT = "%B %d, %Y"
DISPLAY_TIME_FORMAT = "%I:%M %p"
DISPLAY_DATETIME_FORMAT = "%B %d, %Y at %I:%M %p"

# Business Hours
DEFAULT_OPENING_TIME = "09:00"
DEFAULT_CLOSING_TIME = "22:00"

# Currency
CURRENCY_SYMBOL = "$"
CURRENCY_CODE = "USD"

# Order Number Prefix
ORDER_NUMBER_PREFIX = "ORD"

# Cache Timeouts (in seconds)
CACHE_TIMEOUT_SHORT = 300  # 5 minutes
CACHE_TIMEOUT_MEDIUM = 1800  # 30 minutes
CACHE_TIMEOUT_LONG = 3600  # 1 hour

# Rate Limiting
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_WINDOW = 3600  # 1 hour

# Security
PASSWORD_MIN_LENGTH = 6
SESSION_TIMEOUT = 3600  # 1 hour
CSRF_TOKEN_TIMEOUT = 3600  # 1 hour

# Email Templates
EMAIL_TEMPLATES = {
    'welcome': 'emails/welcome.html',
    'order_confirmation': 'emails/order_confirmation.html',
    'order_status_update': 'emails/order_status_update.html',
    'password_reset': 'emails/password_reset.html'
}

# Notification Types
NOTIFICATION_TYPES = {
    'INFO': 'info',
    'SUCCESS': 'success',
    'WARNING': 'warning',
    'ERROR': 'error'
}

# API Response Codes
API_SUCCESS = 200
API_CREATED = 201
API_BAD_REQUEST = 400
API_UNAUTHORIZED = 401
API_FORBIDDEN = 403
API_NOT_FOUND = 404
API_METHOD_NOT_ALLOWED = 405
API_RATE_LIMITED = 429
API_INTERNAL_ERROR = 500

# Database Query Limits
MAX_QUERY_RESULTS = 1000
DEFAULT_QUERY_LIMIT = 50

# Search
MIN_SEARCH_LENGTH = 2
MAX_SEARCH_LENGTH = 100

# File Paths
UPLOAD_FOLDER = "uploads"
STATIC_FOLDER = "static"
TEMPLATE_FOLDER = "templates"

# Logging
LOG_LEVELS = {
    'DEBUG': 10,
    'INFO': 20,
    'WARNING': 30,
    'ERROR': 40,
    'CRITICAL': 50
}

# Error Messages
ERROR_MESSAGES = {
    'GENERIC_ERROR': 'An unexpected error occurred. Please try again.',
    'VALIDATION_ERROR': 'Please check your input and try again.',
    'AUTHENTICATION_ERROR': 'Please log in to access this feature.',
    'AUTHORIZATION_ERROR': 'You do not have permission to perform this action.',
    'NOT_FOUND_ERROR': 'The requested resource was not found.',
    'RATE_LIMIT_ERROR': 'Too many requests. Please try again later.',
    'DATABASE_ERROR': 'A database error occurred. Please try again.',
    'NETWORK_ERROR': 'A network error occurred. Please check your connection.'
}

# Success Messages
SUCCESS_MESSAGES = {
    'LOGIN_SUCCESS': 'Login successful!',
    'LOGOUT_SUCCESS': 'You have been logged out successfully.',
    'REGISTRATION_SUCCESS': 'Registration successful!',
    'PROFILE_UPDATE_SUCCESS': 'Profile updated successfully!',
    'PASSWORD_RESET_SUCCESS': 'Password reset successful!',
    'ORDER_PLACED_SUCCESS': 'Order placed successfully!',
    'ORDER_UPDATED_SUCCESS': 'Order updated successfully!',
    'REVIEW_SUBMITTED_SUCCESS': 'Review submitted successfully!',
    'FEEDBACK_SUBMITTED_SUCCESS': 'Feedback submitted successfully!',
    'MENU_ITEM_ADDED_SUCCESS': 'Menu item added successfully!',
    'MENU_ITEM_UPDATED_SUCCESS': 'Menu item updated successfully!',
    'MENU_ITEM_DELETED_SUCCESS': 'Menu item deleted successfully!',
    'RESTAURANT_REGISTERED_SUCCESS': 'Restaurant registered successfully!'
}

# Default Values
DEFAULT_VALUES = {
    'USER_IS_ACTIVE': True,
    'RESTAURANT_IS_ACTIVE': True,
    'MENU_ITEM_IS_AVAILABLE': True,
    'MENU_ITEM_IS_SPECIAL': False,
    'MENU_ITEM_IS_DEAL_OF_DAY': False,
    'ORDER_STATUS': ORDER_STATUS_PENDING,
    'FEEDBACK_STATUS': FEEDBACK_STATUS_OPEN,
    'CART_QUANTITY': 1
}

# Feature Flags
FEATURES = {
    'ENABLE_REVIEWS': True,
    'ENABLE_FEEDBACK': True,
    'ENABLE_RECOMMENDATIONS': True,
    'ENABLE_ANALYTICS': True,
    'ENABLE_NOTIFICATIONS': True,
    'ENABLE_CACHING': True,
    'ENABLE_RATE_LIMITING': True
}

# API Endpoints
API_ENDPOINTS = {
    'RESTAURANTS': '/api/restaurants',
    'RESTAURANT_MENU': '/api/restaurant/<int:restaurant_id>/menu',
    'RECOMMENDATIONS': '/api/recommendations',
    'ORDER_STATUS': '/api/order-status/<int:order_id>',
    'CART_COUNT': '/api/cart-count'
}

# Social Media Links (placeholder)
SOCIAL_LINKS = {
    'FACEBOOK': 'https://facebook.com/justeat',
    'TWITTER': 'https://twitter.com/justeat',
    'INSTAGRAM': 'https://instagram.com/justeat',
    'LINKEDIN': 'https://linkedin.com/company/justeat'
}

# Contact Information
CONTACT_INFO = {
    'EMAIL': 'support@justeat.com',
    'PHONE': '+1 (555) 123-4567',
    'ADDRESS': '123 Food Street, City, State 12345',
    'HOURS': 'Monday - Friday: 9:00 AM - 6:00 PM'
}
