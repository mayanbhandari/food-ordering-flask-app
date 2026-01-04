"""
Analytics and reporting functions for JustEat application
"""

from datetime import datetime, date, timedelta
from flask import current_app
from sqlalchemy import func, desc
import logging

logger = logging.getLogger(__name__)


class Analytics:
    """Analytics class for generating reports and insights"""

    @staticmethod
    def get_restaurant_performance(restaurant_id, days=30):
        """Get performance metrics for a restaurant"""
        from models import Order, Review, MenuItem, OrderItem

        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        # Total orders
        total_orders = Order.query.filter(
            Order.restaurant_id == restaurant_id,
            func.date(Order.created_at) >= start_date,
            func.date(Order.created_at) <= end_date
        ).count()

        # Total revenue
        total_revenue = current_app.db.session.query(
            func.sum(Order.total_amount)
        ).filter(
            Order.restaurant_id == restaurant_id,
            func.date(Order.created_at) >= start_date,
            func.date(Order.created_at) <= end_date
        ).scalar() or 0

        # Average order value
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

        # Total reviews
        total_reviews = Review.query.filter(
            Review.restaurant_id == restaurant_id,
            func.date(Review.created_at) >= start_date,
            func.date(Review.created_at) <= end_date
        ).count()

        # Average rating
        avg_rating = current_app.db.session.query(
            func.avg(Review.rating)
        ).filter(
            Review.restaurant_id == restaurant_id,
            func.date(Review.created_at) >= start_date,
            func.date(Review.created_at) <= end_date
        ).scalar() or 0

        return {
            'total_orders': total_orders,
            'total_revenue': float(total_revenue),
            'avg_order_value': float(avg_order_value),
            'total_reviews': total_reviews,
            'avg_rating': round(avg_rating, 1),
            'period_days': days
        }

    @staticmethod
    def get_popular_menu_items(restaurant_id, days=7, limit=10):
        """Get most popular menu items for a restaurant"""
        from models import MenuItem, OrderItem, Order

        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        popular_items = current_app.db.session.query(
            MenuItem,
            func.count(OrderItem.id).label('order_count'),
            func.sum(OrderItem.quantity).label('total_quantity'),
            func.sum(OrderItem.price * OrderItem.quantity).label('total_revenue')
        ).join(OrderItem).join(Order).filter(
            MenuItem.restaurant_id == restaurant_id,
            func.date(Order.created_at) >= start_date,
            func.date(Order.created_at) <= end_date
        ).group_by(MenuItem.id).order_by(
            desc('order_count')
        ).limit(limit).all()

        return [
            {
                'menu_item': item[0],
                'order_count': item[1],
                'total_quantity': item[2],
                'total_revenue': float(item[3])
            }
            for item in popular_items
        ]

    @staticmethod
    def get_daily_revenue(restaurant_id, days=30):
        """Get daily revenue for a restaurant"""
        from models import Order

        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        daily_revenue = current_app.db.session.query(
            func.date(Order.created_at).label('date'),
            func.sum(Order.total_amount).label('revenue'),
            func.count(Order.id).label('order_count')
        ).filter(
            Order.restaurant_id == restaurant_id,
            func.date(Order.created_at) >= start_date,
            func.date(Order.created_at) <= end_date
        ).group_by(
            func.date(Order.created_at)
        ).order_by(
            func.date(Order.created_at)
        ).all()

        return [
            {
                'date': str(day[0]),
                'revenue': float(day[1]),
                'order_count': day[2]
            }
            for day in daily_revenue
        ]

    @staticmethod
    def get_customer_insights(restaurant_id, days=30):
        """Get customer insights for a restaurant"""
        from models import Order, User

        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        # New customers
        new_customers = current_app.db.session.query(User).join(Order).filter(
            Order.restaurant_id == restaurant_id,
            func.date(Order.created_at) >= start_date,
            func.date(Order.created_at) <= end_date
        ).distinct().count()

        # Returning customers
        returning_customers = current_app.db.session.query(
            Order.customer_id,
            func.count(Order.id).label('order_count')
        ).filter(
            Order.restaurant_id == restaurant_id,
            func.date(Order.created_at) >= start_date,
            func.date(Order.created_at) <= end_date
        ).group_by(Order.customer_id).having(
            func.count(Order.id) > 1
        ).count()

        # Average orders per customer
        total_orders = Order.query.filter(
            Order.restaurant_id == restaurant_id,
            func.date(Order.created_at) >= start_date,
            func.date(Order.created_at) <= end_date
        ).count()

        avg_orders_per_customer = total_orders / \
            new_customers if new_customers > 0 else 0

        return {
            'new_customers': new_customers,
            'returning_customers': returning_customers,
            'total_customers': new_customers + returning_customers,
            'avg_orders_per_customer': round(avg_orders_per_customer, 2)
        }

    @staticmethod
    def get_order_status_distribution(restaurant_id, days=30):
        """Get distribution of order statuses"""
        from models import Order

        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        status_distribution = current_app.db.session.query(
            Order.status,
            func.count(Order.id).label('count')
        ).filter(
            Order.restaurant_id == restaurant_id,
            func.date(Order.created_at) >= start_date,
            func.date(Order.created_at) <= end_date
        ).group_by(Order.status).all()

        return {
            status[0]: status[1]
            for status in status_distribution
        }

    @staticmethod
    def get_peak_hours(restaurant_id, days=30):
        """Get peak ordering hours"""
        from models import Order

        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        peak_hours = current_app.db.session.query(
            func.hour(Order.created_at).label('hour'),
            func.count(Order.id).label('order_count')
        ).filter(
            Order.restaurant_id == restaurant_id,
            func.date(Order.created_at) >= start_date,
            func.date(Order.created_at) <= end_date
        ).group_by(
            func.hour(Order.created_at)
        ).order_by(
            desc('order_count')
        ).limit(5).all()

        return [
            {
                'hour': hour[0],
                'order_count': hour[1]
            }
            for hour in peak_hours
        ]

    @staticmethod
    def get_review_insights(restaurant_id, days=30):
        """Get review insights for a restaurant"""
        from models import Review

        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        # Rating distribution
        rating_distribution = current_app.db.session.query(
            Review.rating,
            func.count(Review.id).label('count')
        ).filter(
            Review.restaurant_id == restaurant_id,
            func.date(Review.created_at) >= start_date,
            func.date(Review.created_at) <= end_date
        ).group_by(Review.rating).all()

        # Recent reviews
        recent_reviews = Review.query.filter(
            Review.restaurant_id == restaurant_id,
            func.date(Review.created_at) >= start_date,
            func.date(Review.created_at) <= end_date
        ).order_by(desc(Review.created_at)).limit(10).all()

        return {
            'rating_distribution': {
                rating[0]: rating[1]
                for rating in rating_distribution
            },
            'recent_reviews': recent_reviews
        }

    @staticmethod
    def get_platform_analytics(days=30):
        """Get platform-wide analytics"""
        from models import Order, Restaurant, User, Review

        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        # Total orders
        total_orders = Order.query.filter(
            func.date(Order.created_at) >= start_date,
            func.date(Order.created_at) <= end_date
        ).count()

        # Total revenue
        total_revenue = current_app.db.session.query(
            func.sum(Order.total_amount)
        ).filter(
            func.date(Order.created_at) >= start_date,
            func.date(Order.created_at) <= end_date
        ).scalar() or 0

        # Active restaurants
        active_restaurants = Restaurant.query.filter_by(is_active=True).count()

        # Total customers
        total_customers = User.query.filter_by(role='customer').count()

        # Total reviews
        total_reviews = Review.query.filter(
            func.date(Review.created_at) >= start_date,
            func.date(Review.created_at) <= end_date
        ).count()

        return {
            'total_orders': total_orders,
            'total_revenue': float(total_revenue),
            'active_restaurants': active_restaurants,
            'total_customers': total_customers,
            'total_reviews': total_reviews,
            'avg_order_value': float(
                total_revenue /
                total_orders) if total_orders > 0 else 0}

    @staticmethod
    def get_customer_behavior(user_id, days=30):
        """Get customer behavior insights"""
        from models import Order, Restaurant, Review

        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        # Order history
        orders = Order.query.filter(
            Order.customer_id == user_id,
            func.date(Order.created_at) >= start_date,
            func.date(Order.created_at) <= end_date
        ).all()

        # Favorite cuisines
        favorite_cuisines = current_app.db.session.query(
            Restaurant.cuisine_type,
            func.count(Order.id).label('order_count')
        ).join(Order).filter(
            Order.customer_id == user_id,
            func.date(Order.created_at) >= start_date,
            func.date(Order.created_at) <= end_date
        ).group_by(Restaurant.cuisine_type).order_by(
            desc('order_count')
        ).limit(5).all()

        # Favorite restaurants
        favorite_restaurants = current_app.db.session.query(
            Restaurant,
            func.count(Order.id).label('order_count')
        ).join(Order).filter(
            Order.customer_id == user_id,
            func.date(Order.created_at) >= start_date,
            func.date(Order.created_at) <= end_date
        ).group_by(Restaurant.id).order_by(
            desc('order_count')
        ).limit(5).all()

        # Review activity
        reviews = Review.query.filter(
            Review.user_id == user_id,
            func.date(Review.created_at) >= start_date,
            func.date(Review.created_at) <= end_date
        ).count()

        return {
            'total_orders': len(orders),
            'total_spent': sum(order.total_amount for order in orders),
            'favorite_cuisines': [
                {'cuisine': cuisine[0], 'order_count': cuisine[1]}
                for cuisine in favorite_cuisines
            ],
            'favorite_restaurants': [
                {'restaurant': restaurant[0], 'order_count': restaurant[1]}
                for restaurant in favorite_restaurants
            ],
            'reviews_written': reviews,
            'avg_order_value': sum(order.total_amount for order in orders) / len(orders) if orders else 0
        }
