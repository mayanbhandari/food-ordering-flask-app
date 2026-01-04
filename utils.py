"""
Utility functions for JustEat application
"""

from datetime import datetime, date, timedelta
from flask import current_app
import logging

logger = logging.getLogger(__name__)


def generate_order_number(user_id):
    """Generate unique order number"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    return f"ORD{timestamp}{user_id}"


def calculate_order_total(order_items):
    """Calculate total amount for order items"""
    return sum(item.price * item.quantity for item in order_items)


def format_currency(amount):
    """Format amount as currency"""
    return f"${amount:.2f}"


def get_popular_items(restaurant_id, limit=5):
    """Get popular menu items for a restaurant"""
    from models import MenuItem, OrderItem, Order

    today = date.today()
    popular_items = current_app.db.session.query(
        MenuItem,
        current_app.db.func.count(OrderItem.id).label('order_count')
    ).join(OrderItem).join(Order).filter(
        MenuItem.restaurant_id == restaurant_id,
        current_app.db.func.date(Order.created_at) == today
    ).group_by(MenuItem.id).order_by(
        current_app.db.func.count(OrderItem.id).desc()
    ).limit(limit).all()

    return popular_items


def get_user_recommendations(user_id):
    """Get personalized recommendations for user"""
    from models import User, Order, Restaurant, MenuItem

    # Get user's favorite cuisines
    favorite_cuisines = current_app.db.session.query(Restaurant.cuisine_type)\
        .join(Order)\
        .filter(Order.customer_id == user_id)\
        .group_by(Restaurant.cuisine_type)\
        .order_by(current_app.db.func.count(Order.id).desc())\
        .limit(3).all()

    # Get recommended restaurants
    recommended_restaurants = []
    for cuisine in favorite_cuisines:
        restaurants = Restaurant.query.filter(
            Restaurant.cuisine_type == cuisine[0],
            Restaurant.is_active
        ).limit(2).all()
        recommended_restaurants.extend(restaurants)

    return recommended_restaurants


def send_notification(user_id, message, notification_type='info'):
    """Send notification to user (placeholder for future implementation)"""
    logger.info(
        f"Notification to user {user_id}: {message} ({notification_type})")
    # Future implementation could include email, SMS, or push notifications


def validate_business_hours(restaurant):
    """Validate if restaurant is currently open"""
    now = datetime.now().time()
    return restaurant.opening_time <= now <= restaurant.closing_time


def get_order_status_progress(status):
    """Get progress percentage for order status"""
    progress_map = {
        'pending': 20,
        'confirmed': 40,
        'preparing': 60,
        'ready': 80,
        'delivered': 100,
        'cancelled': 0
    }
    return progress_map.get(status, 0)


def format_time_duration(minutes):
    """Format duration in minutes to human readable format"""
    if minutes < 60:
        return f"{minutes} min"
    else:
        hours = minutes // 60
        remaining_minutes = minutes % 60
        if remaining_minutes == 0:
            return f"{hours} hour{'s' if hours > 1 else ''}"
        else:
            return f"{hours}h {remaining_minutes}m"


def sanitize_input(text):
    """Sanitize user input to prevent XSS"""
    if not text:
        return ""

    # Basic HTML escaping
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&#x27;')

    return text


def calculate_rating_average(restaurant_id):
    """Calculate average rating for restaurant"""
    from models import Review

    avg_rating = current_app.db.session.query(
        current_app.db.func.avg(Review.rating)
    ).filter_by(restaurant_id=restaurant_id).scalar()

    return round(avg_rating, 1) if avg_rating else 0


def get_recent_orders(user_id, limit=5):
    """Get recent orders for user"""
    from models import Order

    return Order.query.filter_by(customer_id=user_id)\
        .order_by(Order.created_at.desc())\
        .limit(limit).all()


def get_restaurant_stats(restaurant_id):
    """Get statistics for restaurant"""
    from models import Order, Review

    stats = {
        'total_orders': Order.query.filter_by(
            restaurant_id=restaurant_id).count(),
        'total_revenue': current_app.db.session.query(
            current_app.db.func.sum(
                Order.total_amount)).filter_by(
                    restaurant_id=restaurant_id).scalar() or 0,
        'total_reviews': Review.query.filter_by(
                        restaurant_id=restaurant_id).count(),
        'average_rating': calculate_rating_average(restaurant_id)}

    return stats


def is_item_popular(menu_item_id):
    """Check if menu item is popular (ordered more than 10 times today)"""
    from models import MenuItem, OrderItem, Order

    today = date.today()
    order_count = current_app.db.session.query(OrderItem)\
        .join(Order)\
        .filter(
            OrderItem.menu_item_id == menu_item_id,
            current_app.db.func.date(Order.created_at) == today
    ).count()

    return order_count > 10


def get_cart_total(user_id):
    """Calculate total amount in user's cart"""
    from models import Cart

    cart_items = Cart.query.filter_by(user_id=user_id).all()
    return sum(item.menu_item.price * item.quantity for item in cart_items)


def clear_user_cart(user_id):
    """Clear all items from user's cart"""
    from models import Cart

    Cart.query.filter_by(user_id=user_id).delete()
    current_app.db.session.commit()


def log_user_activity(user_id, activity, details=None):
    """Log user activity for analytics"""
    logger.info(f"User {user_id} performed {activity}" +
                (f" - {details}" if details else ""))


def validate_email_format(email):
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone_format(phone):
    """Validate phone number format"""
    import re
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    # Check if it's a valid length (10-15 digits)
    return 10 <= len(digits) <= 15


def get_time_ago(datetime_obj):
    """Get human readable time ago string"""
    now = datetime.now()
    diff = now - datetime_obj

    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"


def generate_recommendation_score(user_id, restaurant_id):
    """Generate recommendation score for restaurant based on user preferences"""
    from models import Order, Restaurant

    # Get user's order history
    user_orders = Order.query.filter_by(customer_id=user_id).all()

    if not user_orders:
        return 0.5  # Default score for new users

    # Calculate score based on cuisine preferences
    favorite_cuisines = {}
    for order in user_orders:
        cuisine = order.restaurant.cuisine_type
        favorite_cuisines[cuisine] = favorite_cuisines.get(cuisine, 0) + 1

    # Get restaurant cuisine
    restaurant = Restaurant.query.get(restaurant_id)
    if not restaurant:
        return 0

    # Calculate score
    total_orders = len(user_orders)
    cuisine_orders = favorite_cuisines.get(restaurant.cuisine_type, 0)

    return min(1.0, (cuisine_orders / total_orders) + 0.3)  # Base score of 0.3
