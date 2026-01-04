"""
Admin routes for JustEat application
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import User, Restaurant, MenuItem, Order, OrderItem, Review, Feedback, InAppNotification, Promotion, UserPreference
from forms import PromotionForm
from models import db
from datetime import datetime, date, timedelta
from analytics import Analytics
import logging

admin_bp = Blueprint('admin', __name__)
logger = logging.getLogger(__name__)


def admin_required(f):
    """Decorator to ensure only admin users can access"""
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with platform analytics"""
    try:
        # Get platform-wide analytics
        analytics = Analytics.get_platform_analytics(days=30)

        # Get recent activity
        recent_orders = Order.query.order_by(
            Order.created_at.desc()).limit(10).all()
        recent_restaurants = Restaurant.query.order_by(
            Restaurant.created_at.desc()).limit(5).all()
        recent_users = User.query.order_by(
            User.created_at.desc()).limit(5).all()

        # Get system stats
        total_users = User.query.count()
        total_restaurants = Restaurant.query.count()
        total_orders = Order.query.count()
        total_revenue = db.session.query(
            db.func.sum(Order.total_amount)).scalar() or 0

        # Get pending feedback
        pending_feedback = Feedback.query.filter_by(status='open').count()

        return render_template('admin/dashboard.html',
                               analytics=analytics,
                               recent_orders=recent_orders,
                               recent_restaurants=recent_restaurants,
                               recent_users=recent_users,
                               total_users=total_users,
                               total_restaurants=total_restaurants,
                               total_orders=total_orders,
                               total_revenue=total_revenue,
                               pending_feedback=pending_feedback)
    except Exception as e:
        logger.error(f"Admin dashboard error: {str(e)}")
        flash('Error loading admin dashboard.', 'error')
        return redirect(url_for('index'))


@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    """Manage users"""
    try:
        page = request.args.get('page', 1, type=int)
        role_filter = request.args.get('role', '')
        search = request.args.get('search', '')

        query = User.query

        if role_filter:
            query = query.filter_by(role=role_filter)
        if search:
            query = query.filter(
                db.or_(
                    User.username.contains(search),
                    User.email.contains(search),
                    User.first_name.contains(search),
                    User.last_name.contains(search)
                )
            )

        users = query.order_by(User.created_at.desc())\
            .paginate(page=page, per_page=20, error_out=False)

        return render_template('admin/users.html',
                               users=users,
                               role_filter=role_filter,
                               search=search)
    except Exception as e:
        logger.error(f"Manage users error: {str(e)}")
        flash('Error loading users.', 'error')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route('/restaurants')
@login_required
@admin_required
def manage_restaurants():
    """Manage restaurants"""
    try:
        page = request.args.get('page', 1, type=int)
        status_filter = request.args.get('status', '')
        search = request.args.get('search', '')

        query = Restaurant.query

        if status_filter == 'active':
            query = query.filter_by(is_active=True)
        elif status_filter == 'inactive':
            query = query.filter_by(is_active=False)

        if search:
            query = query.filter(
                db.or_(
                    Restaurant.name.contains(search),
                    Restaurant.cuisine_type.contains(search),
                    Restaurant.address.contains(search)
                )
            )

        restaurants = query.order_by(Restaurant.created_at.desc())\
            .paginate(page=page, per_page=20, error_out=False)

        return render_template('admin/restaurants.html',
                               restaurants=restaurants,
                               status_filter=status_filter,
                               search=search)
    except Exception as e:
        logger.error(f"Manage restaurants error: {str(e)}")
        flash('Error loading restaurants.', 'error')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route('/orders')
@login_required
@admin_required
def manage_orders():
    """Manage all orders"""
    try:
        page = request.args.get('page', 1, type=int)
        status_filter = request.args.get('status', '')
        date_filter = request.args.get('date', '')

        query = Order.query

        if status_filter:
            query = query.filter_by(status=status_filter)

        if date_filter:
            try:
                filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                query = query.filter(db.func.date(
                    Order.created_at) == filter_date)
            except ValueError:
                pass

        orders = query.order_by(Order.created_at.desc())\
            .paginate(page=page, per_page=20, error_out=False)

        return render_template('admin/orders.html',
                               orders=orders,
                               status_filter=status_filter,
                               date_filter=date_filter)
    except Exception as e:
        logger.error(f"Manage orders error: {str(e)}")
        flash('Error loading orders.', 'error')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route('/feedback')
@login_required
@admin_required
def manage_feedback():
    """Manage customer feedback"""
    try:
        page = request.args.get('page', 1, type=int)
        status_filter = request.args.get('status', '')

        query = Feedback.query

        if status_filter:
            query = query.filter_by(status=status_filter)

        feedbacks = query.order_by(Feedback.created_at.desc())\
            .paginate(page=page, per_page=20, error_out=False)

        return render_template('admin/feedback.html',
                               feedbacks=feedbacks,
                               status_filter=status_filter)
    except Exception as e:
        logger.error(f"Manage feedback error: {str(e)}")
        flash('Error loading feedback.', 'error')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route('/promotions')
@login_required
@admin_required
def manage_promotions():
    """Manage promotions"""
    try:
        page = request.args.get('page', 1, type=int)
        status_filter = request.args.get('status', '')

        query = Promotion.query

        if status_filter == 'active':
            query = query.filter_by(is_active=True)
        elif status_filter == 'inactive':
            query = query.filter_by(is_active=False)

        promotions = query.order_by(Promotion.created_at.desc())\
            .paginate(page=page, per_page=20, error_out=False)

        return render_template('admin/promotions.html',
                               promotions=promotions,
                               status_filter=status_filter)
    except Exception as e:
        logger.error(f"Manage promotions error: {str(e)}")
        flash('Error loading promotions.', 'error')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route('/promotions/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_promotion():
    """Create new promotion"""
    form = PromotionForm()

    if form.validate_on_submit():
        try:
            promotion = Promotion(
                title=form.title.data,
                description=form.description.data,
                discount_percentage=form.discount_percentage.data,
                discount_amount=form.discount_amount.data,
                min_order_amount=form.min_order_amount.data,
                max_discount_amount=form.max_discount_amount.data,
                code=form.code.data,
                valid_from=form.valid_from.data,
                valid_until=form.valid_until.data,
                usage_limit=form.usage_limit.data,
                created_by=current_user.id
            )

            db.session.add(promotion)
            db.session.commit()

            logger.info(f"Promotion created: {promotion.title}")
            flash('Promotion created successfully!', 'success')
            return redirect(url_for('admin.manage_promotions'))
        except Exception as e:
            logger.error(f"Create promotion error: {str(e)}")
            flash('Error creating promotion.', 'error')

    return render_template('admin/create_promotion.html', form=form)


@admin_bp.route('/analytics')
@login_required
@admin_required
def analytics():
    """Platform analytics"""
    try:
        days = request.args.get('days', 30, type=int)

        # Get platform analytics
        platform_analytics = Analytics.get_platform_analytics(days=days)

        # Get top restaurants by revenue
        top_restaurants = db.session.query(
            Restaurant,
            db.func.sum(Order.total_amount).label('total_revenue'),
            db.func.count(Order.id).label('total_orders')
        ).join(Order).filter(
            db.func.date(Order.created_at) >= date.today() -
            timedelta(days=days)
        ).group_by(Restaurant.id).order_by(
            db.func.sum(Order.total_amount).desc()
        ).limit(10).all()

        # Get daily revenue for chart
        daily_revenue = []
        for i in range(days):
            day = date.today() - timedelta(days=i)
            revenue = db.session.query(db.func.sum(Order.total_amount))\
                .filter(db.func.date(Order.created_at) == day).scalar() or 0
            daily_revenue.append(
                {'date': day.isoformat(), 'revenue': float(revenue)})

        # Get user growth
        user_growth = []
        for i in range(days):
            day = date.today() - timedelta(days=i)
            new_users = User.query.filter(
                db.func.date(User.created_at) == day
            ).count()
            user_growth.append({'date': day.isoformat(), 'users': new_users})

        return render_template('admin/analytics.html',
                               platform_analytics=platform_analytics,
                               top_restaurants=top_restaurants,
                               daily_revenue=daily_revenue,
                               user_growth=user_growth,
                               days=days)
    except Exception as e:
        logger.error(f"Analytics error: {str(e)}")
        flash('Error loading analytics.', 'error')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route('/notifications')
@login_required
@admin_required
def manage_notifications():
    """Manage system notifications"""
    try:
        page = request.args.get('page', 1, type=int)
        unread_only = request.args.get('unread_only', False, type=bool)

        query = InAppNotification.query

        if unread_only:
            query = query.filter_by(read=False)

        notifications = query.order_by(InAppNotification.created_at.desc())\
            .paginate(page=page, per_page=20, error_out=False)

        return render_template('admin/notifications.html',
                               notifications=notifications,
                               unread_only=unread_only)
    except Exception as e:
        logger.error(f"Manage notifications error: {str(e)}")
        flash('Error loading notifications.', 'error')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route('/user/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    """Toggle user active status"""
    try:
        user = User.query.get_or_404(user_id)
        user.is_active = not user.is_active
        db.session.commit()

        status = "activated" if user.is_active else "deactivated"
        logger.info(f"User {user.username} {status}")

        return jsonify({
            'success': True,
            'message': f'User {status} successfully',
            'is_active': user.is_active
        })
    except Exception as e:
        logger.error(f"Toggle user status error: {str(e)}")
        return jsonify({'success': False,
                        'message': 'Error updating user status'})


@admin_bp.route('/restaurant/<int:restaurant_id>/toggle-status',
                methods=['POST'])
@login_required
@admin_required
def toggle_restaurant_status(restaurant_id):
    """Toggle restaurant active status"""
    try:
        restaurant = Restaurant.query.get_or_404(restaurant_id)
        restaurant.is_active = not restaurant.is_active
        db.session.commit()

        status = "activated" if restaurant.is_active else "deactivated"
        logger.info(f"Restaurant {restaurant.name} {status}")

        return jsonify({
            'success': True,
            'message': f'Restaurant {status} successfully',
            'is_active': restaurant.is_active
        })
    except Exception as e:
        logger.error(f"Toggle restaurant status error: {str(e)}")
        return jsonify({'success': False,
                        'message': 'Error updating restaurant status'})


@admin_bp.route('/promotion/<int:promotion_id>/toggle-status',
                methods=['POST'])
@login_required
@admin_required
def toggle_promotion_status(promotion_id):
    """Toggle promotion active status"""
    try:
        promotion = Promotion.query.get_or_404(promotion_id)
        promotion.is_active = not promotion.is_active
        db.session.commit()

        status = "activated" if promotion.is_active else "deactivated"
        logger.info(f"Promotion {promotion.title} {status}")

        return jsonify({
            'success': True,
            'message': f'Promotion {status} successfully',
            'is_active': promotion.is_active
        })
    except Exception as e:
        logger.error(f"Toggle promotion status error: {str(e)}")
        return jsonify({'success': False,
                        'message': 'Error updating promotion status'})


@admin_bp.route('/feedback/<int:feedback_id>/respond', methods=['POST'])
@login_required
@admin_required
def respond_to_feedback(feedback_id):
    """Respond to customer feedback"""
    try:
        feedback = Feedback.query.get_or_404(feedback_id)

        response = request.json.get('response', '')
        status = request.json.get('status', 'in_progress')

        feedback.response = response
        feedback.status = status
        feedback.updated_at = datetime.utcnow()

        db.session.commit()

        logger.info(f"Response added to feedback {feedback_id}")
        return jsonify({'success': True,
                        'message': 'Response added successfully!'})
    except Exception as e:
        logger.error(f"Feedback response error: {str(e)}")
        return jsonify({'success': False, 'message': 'Error adding response'})


@admin_bp.route('/send-bulk-notification', methods=['POST'])
@login_required
@admin_required
def send_bulk_notification():
    """Send bulk notification to users"""
    try:
        title = request.json.get('title', '')
        message = request.json.get('message', '')
        # all, customers, restaurant_owners
        user_type = request.json.get('user_type', 'all')

        if not title or not message:
            return jsonify({'success': False,
                            'message': 'Title and message are required'})

        # Get target users
        if user_type == 'customers':
            users = User.query.filter_by(role='customer', is_active=True).all()
        elif user_type == 'restaurant_owners':
            users = User.query.filter_by(
                role='restaurant_owner', is_active=True).all()
        else:
            users = User.query.filter_by(is_active=True).all()

        # Send notifications
        from notifications import send_bulk_notification, NotificationType
        send_bulk_notification(
            user_ids=[user.id for user in users],
            title=title,
            message=message,
            notification_type=NotificationType.INFO
        )

        logger.info(f"Bulk notification sent to {len(users)} users")
        return jsonify({
            'success': True,
            'message': f'Notification sent to {len(users)} users'
        })
    except Exception as e:
        logger.error(f"Bulk notification error: {str(e)}")
        return jsonify({'success': False,
                        'message': 'Error sending notification'})


@admin_bp.route('/system-health')
@login_required
@admin_required
def system_health():
    """System health check"""
    try:
        health_status = {
            'database': 'healthy',
            'cache': 'healthy',
            'email': 'healthy',
            'disk_space': 'healthy',
            'memory': 'healthy'
        }

        # Check database connection
        try:
            db.session.execute('SELECT 1')
        except Exception:
            health_status['database'] = 'unhealthy'

        # Check cache (if using Redis)
        try:
            from cache import cache
            cache.get('health_check')
        except Exception:
            health_status['cache'] = 'unhealthy'

        # Check email service
        try:
            from email_service import email_service
            # Test email configuration
            if not email_service.smtp_username:
                health_status['email'] = 'not_configured'
        except Exception:
            health_status['email'] = 'unhealthy'

        return render_template(
            'admin/system_health.html',
            health_status=health_status)
    except Exception as e:
        logger.error(f"System health check error: {str(e)}")
        flash('Error checking system health.', 'error')
        return redirect(url_for('admin.dashboard'))
