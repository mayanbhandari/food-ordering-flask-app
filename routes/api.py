from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import Restaurant, MenuItem, Order, OrderItem
from models import db
from datetime import date
from sqlalchemy import or_
from math import ceil
import logging

api_bp = Blueprint('api', __name__)
logger = logging.getLogger(__name__)


@api_bp.route('/restaurants')
def get_restaurants():
    """API endpoint to get restaurants"""
    try:
        search = request.args.get('search', '')
        cuisine = request.args.get('cuisine', '')

        query = Restaurant.query.filter_by(is_active=True)

        if search:
            query = query.filter(Restaurant.name.contains(search))
        if cuisine:
            query = query.filter(Restaurant.cuisine_type == cuisine)

        restaurants = query.all()

        return jsonify({
            'success': True,
            'restaurants': [{
                'id': r.id,
                'name': r.name,
                'cuisine_type': r.cuisine_type,
                'description': r.description,
                'address': r.address,
                'phone': r.phone
            } for r in restaurants]
        })
    except Exception as e:
        logger.error(f"API restaurants error: {str(e)}")
        return jsonify({'success': False,
                        'message': 'Error fetching restaurants'})


@api_bp.route('/restaurant/<int:restaurant_id>/menu')
def get_menu(restaurant_id):
    """API endpoint to get restaurant menu"""
    try:
        restaurant = Restaurant.query.get_or_404(restaurant_id)
        menu_items = MenuItem.query.filter_by(
            restaurant_id=restaurant_id,
            is_available=True
        ).all()

        return jsonify({
            'success': True,
            'restaurant': {
                'id': restaurant.id,
                'name': restaurant.name,
                'cuisine_type': restaurant.cuisine_type
            },
            'menu_items': [{
                'id': item.id,
                'name': item.name,
                'description': item.description,
                'price': float(item.price),
                'category': item.category,
                'is_special': item.is_special,
                'is_deal_of_day': item.is_deal_of_day,
                'is_mostly_ordered': item.is_mostly_ordered
            } for item in menu_items]
        })
    except Exception as e:
        logger.error(f"API menu error: {str(e)}")
        return jsonify({'success': False, 'message': 'Error fetching menu'})


@api_bp.route('/recommendations')
@login_required
def get_recommendations():
    """API endpoint to get personalized recommendations"""
    try:
        if current_user.role != 'customer':
            return jsonify({'success': False,
                            'message': 'Customer access required'})

        # Get user's order history
        user_orders = Order.query.filter_by(customer_id=current_user.id).all()

        # Get favorite cuisines
        favorite_cuisines = db.session.query(Restaurant.cuisine_type)\
            .join(Order)\
            .filter(Order.customer_id == current_user.id)\
            .group_by(Restaurant.cuisine_type)\
            .order_by(db.func.count(Order.id).desc())\
            .limit(3).all()

        # Get recommended restaurants
        recommended_restaurants = []
        for cuisine in favorite_cuisines:
            restaurants = Restaurant.query.filter(
                Restaurant.cuisine_type == cuisine[0],
                Restaurant.is_active
            ).limit(2).all()
            recommended_restaurants.extend(restaurants)

        # Get popular items from favorite restaurants
        popular_items = []
        for restaurant in recommended_restaurants[:3]:  # Top 3 restaurants
            items = MenuItem.query.filter(
                MenuItem.restaurant_id == restaurant.id,
                MenuItem.is_available
            ).limit(3).all()
            popular_items.extend(items)

        return jsonify({
            'success': True,
            'recommended_restaurants': [{
                'id': r.id,
                'name': r.name,
                'cuisine_type': r.cuisine_type,
                'description': r.description
            } for r in recommended_restaurants],
            'popular_items': [{
                'id': item.id,
                'name': item.name,
                'price': float(item.price),
                'restaurant_name': item.restaurant.name,
                'is_special': item.is_special,
                'is_deal_of_day': item.is_deal_of_day
            } for item in popular_items]
        })
    except Exception as e:
        logger.error(f"API recommendations error: {str(e)}")
        return jsonify({'success': False,
                        'message': 'Error fetching recommendations'})


@api_bp.route('/order-status/<int:order_id>')
@login_required
def get_order_status(order_id):
    """API endpoint to get order status"""
    try:
        order = Order.query.get_or_404(order_id)

        if current_user.role == 'customer' and order.customer_id != current_user.id:
            return jsonify({'success': False, 'message': 'Unauthorized'})
        elif current_user.role == 'restaurant_owner' and order.restaurant.owner_id != current_user.id:
            return jsonify({'success': False, 'message': 'Unauthorized'})

        return jsonify({
            'success': True,
            'order': {
                'id': order.id,
                'order_number': order.order_number,
                'status': order.status,
                'total_amount': float(order.total_amount),
                'created_at': order.created_at.isoformat(),
                'restaurant_name': order.restaurant.name
            }
        })
    except Exception as e:
        logger.error(f"API order status error: {str(e)}")
        return jsonify({'success': False,
                        'message': 'Error fetching order status'})
