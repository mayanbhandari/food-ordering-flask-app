"""
Notification system for JustEat application
"""

from datetime import datetime
from flask import current_app
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """Notification types"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    ORDER_UPDATE = "order_update"
    REVIEW_RECEIVED = "review_received"
    FEEDBACK_RECEIVED = "feedback_received"
    PROMOTION = "promotion"


class NotificationChannel(Enum):
    """Notification channels"""
    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"


class Notification:
    """Notification model"""

    def __init__(
            self,
            user_id,
            title,
            message,
            notification_type=NotificationType.INFO,
            channel=NotificationChannel.IN_APP,
            data=None,
            expires_at=None):
        self.user_id = user_id
        self.title = title
        self.message = message
        self.type = notification_type
        self.channel = channel
        self.data = data or {}
        self.created_at = datetime.utcnow()
        self.expires_at = expires_at
        self.read = False
        self.sent = False


class NotificationService:
    """Notification service for managing notifications"""

    def __init__(self):
        self.notifications = []

    def create_notification(
            self,
            user_id,
            title,
            message,
            notification_type=NotificationType.INFO,
            channel=NotificationChannel.IN_APP,
            data=None,
            expires_at=None):
        """Create a new notification"""
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            channel=channel,
            data=data,
            expires_at=expires_at
        )

        self.notifications.append(notification)
        logger.info(f"Created notification for user {user_id}: {title}")

        return notification

    def send_notification(self, notification):
        """Send notification through appropriate channel"""
        try:
            if notification.channel == NotificationChannel.EMAIL:
                self._send_email_notification(notification)
            elif notification.channel == NotificationChannel.SMS:
                self._send_sms_notification(notification)
            elif notification.channel == NotificationChannel.PUSH:
                self._send_push_notification(notification)
            else:
                # In-app notification (stored in database)
                self._store_in_app_notification(notification)

            notification.sent = True
            logger.info(f"Sent notification to user {notification.user_id}")

        except Exception as e:
            logger.error(f"Failed to send notification: {str(e)}")

    def _send_email_notification(self, notification):
        """Send email notification"""
        from email_service import email_service
        from models import User

        user = User.query.get(notification.user_id)
        if not user:
            return

        subject = notification.title
        html_content = f"""
        <h2>{notification.title}</h2>
        <p>{notification.message}</p>
        """

        if notification.data:
            html_content += "<ul>"
            for key, value in notification.data.items():
                html_content += f"<li><strong>{key}:</strong> {value}</li>"
            html_content += "</ul>"

        email_service.send_email(user.email, subject, html_content)

    def _send_sms_notification(self, notification):
        """Send SMS notification (placeholder)"""
        # Implement SMS service integration
        logger.info(f"SMS notification: {notification.message}")

    def _send_push_notification(self, notification):
        """Send push notification (placeholder)"""
        # Implement push notification service integration
        logger.info(f"Push notification: {notification.message}")

    def _store_in_app_notification(self, notification):
        """Store in-app notification in database"""
        from models import InAppNotification, db

        try:
            in_app_notification = InAppNotification(
                user_id=notification.user_id,
                title=notification.title,
                message=notification.message,
                notification_type=notification.type.value,
                data=notification.data,
                expires_at=notification.expires_at
            )

            db.session.add(in_app_notification)
            db.session.commit()

        except Exception as e:
            logger.error(f"Failed to store in-app notification: {str(e)}")

    def get_user_notifications(self, user_id, limit=20, unread_only=False):
        """Get notifications for a user"""
        from models import InAppNotification

        query = InAppNotification.query.filter_by(user_id=user_id)

        if unread_only:
            query = query.filter_by(read=False)

        notifications = query.order_by(
            InAppNotification.created_at.desc()).limit(limit).all()

        return notifications

    def mark_notification_read(self, notification_id, user_id):
        """Mark notification as read"""
        from models import InAppNotification, db

        notification = InAppNotification.query.filter_by(
            id=notification_id,
            user_id=user_id
        ).first()

        if notification:
            notification.read = True
            notification.read_at = datetime.utcnow()
            db.session.commit()

    def mark_all_notifications_read(self, user_id):
        """Mark all notifications as read for a user"""
        from models import InAppNotification, db

        InAppNotification.query.filter_by(
            user_id=user_id,
            read=False
        ).update({
            'read': True,
            'read_at': datetime.utcnow()
        })

        db.session.commit()

    def delete_expired_notifications(self):
        """Delete expired notifications"""
        from models import InAppNotification, db

        expired_count = InAppNotification.query.filter(
            InAppNotification.expires_at < datetime.utcnow()
        ).delete()

        db.session.commit()
        logger.info(f"Deleted {expired_count} expired notifications")


# Global notification service
notification_service = NotificationService()

# Notification templates


class NotificationTemplates:
    """Predefined notification templates"""

    @staticmethod
    def order_confirmed(order):
        """Order confirmation notification"""
        return {
            'title': 'Order Confirmed!',
            'message': f'Your order #{
                order.order_number} has been confirmed and is being prepared.',
            'type': NotificationType.SUCCESS,
            'data': {
                'order_id': order.id,
                'order_number': order.order_number,
                'restaurant_name': order.restaurant.name,
                'total_amount': float(
                    order.total_amount)}}

    @staticmethod
    def order_status_update(order):
        """Order status update notification"""
        status_messages = {
            'confirmed': 'Your order has been confirmed and is being prepared.',
            'preparing': 'Your order is being prepared by the restaurant.',
            'ready': 'Your order is ready for pickup!',
            'delivered': 'Your order has been delivered. Enjoy your meal!',
            'cancelled': 'Your order has been cancelled.'}

        return {
            'title': f'Order Update - {order.order_number}',
            'message': status_messages.get(order.status, 'Your order status has been updated.'),
            'type': NotificationType.ORDER_UPDATE,
            'data': {
                'order_id': order.id,
                'order_number': order.order_number,
                'status': order.status,
                'restaurant_name': order.restaurant.name
            }
        }

    @staticmethod
    def review_received(review):
        """Review received notification"""
        return {
            'title': f'New Review for {
                review.restaurant.name}', 'message': f'You received a {
                review.rating}-star review from {
                review.user.first_name} {
                    review.user.last_name}.', 'type': NotificationType.REVIEW_RECEIVED, 'data': {
                        'review_id': review.id, 'rating': review.rating, 'customer_name': f"{
                            review.user.first_name} {
                                review.user.last_name}", 'restaurant_name': review.restaurant.name}}

    @staticmethod
    def feedback_received(feedback):
        """Feedback received notification"""
        return {
            'title': f'New Feedback for {feedback.restaurant.name if feedback.restaurant else "JustEat"}',
            'message': f'You received new feedback: {feedback.subject}',
            'type': NotificationType.FEEDBACK_RECEIVED,
            'data': {
                'feedback_id': feedback.id,
                'subject': feedback.subject,
                'customer_name': f"{feedback.user.first_name} {feedback.user.last_name}",
                'restaurant_name': feedback.restaurant.name if feedback.restaurant else 'JustEat'
            }
        }

    @staticmethod
    def welcome_new_user(user):
        """Welcome new user notification"""
        return {
            'title': 'Welcome to JustEat!',
            'message': f'Hi {
                user.first_name}, welcome to JustEat! Start exploring restaurants and place your first order.',
            'type': NotificationType.SUCCESS,
            'data': {
                'user_id': user.id,
                'user_name': f"{
                    user.first_name} {
                    user.last_name}"}}

    @staticmethod
    def restaurant_registered(restaurant):
        """Restaurant registration notification"""
        return {
            'title': 'Restaurant Registration Successful!',
            'message': f'Your restaurant "{
                restaurant.name}" has been successfully registered on JustEat.',
            'type': NotificationType.SUCCESS,
            'data': {
                'restaurant_id': restaurant.id,
                'restaurant_name': restaurant.name,
                'cuisine_type': restaurant.cuisine_type}}

    @staticmethod
    def promotion_notification(user, promotion):
        """Promotion notification"""
        return {
            'title': 'Special Promotion Available!',
            'message': f'{promotion.title}: {promotion.description}',
            'type': NotificationType.PROMOTION,
            'data': {
                'promotion_id': promotion.id,
                'discount_percentage': promotion.discount_percentage,
                'valid_until': promotion.valid_until.isoformat() if promotion.valid_until else None
            }
        }

# Notification helper functions


def send_order_notification(order, notification_type):
    """Send order-related notification"""
    template = None

    if notification_type == 'confirmed':
        template = NotificationTemplates.order_confirmed(order)
    elif notification_type == 'status_update':
        template = NotificationTemplates.order_status_update(order)

    if template:
        notification = notification_service.create_notification(
            user_id=order.customer_id,
            title=template['title'],
            message=template['message'],
            notification_type=template['type'],
            data=template['data']
        )

        notification_service.send_notification(notification)


def send_review_notification(review):
    """Send review notification to restaurant owner"""
    template = NotificationTemplates.review_received(review)

    notification = notification_service.create_notification(
        user_id=review.restaurant.owner_id,
        title=template['title'],
        message=template['message'],
        notification_type=template['type'],
        data=template['data']
    )

    notification_service.send_notification(notification)


def send_feedback_notification(feedback):
    """Send feedback notification"""
    template = NotificationTemplates.feedback_received(feedback)

    # Send to restaurant owner if feedback is for specific restaurant
    user_id = feedback.restaurant.owner_id if feedback.restaurant else None

    if user_id:
        notification = notification_service.create_notification(
            user_id=user_id,
            title=template['title'],
            message=template['message'],
            notification_type=template['type'],
            data=template['data']
        )

        notification_service.send_notification(notification)


def send_welcome_notification(user):
    """Send welcome notification to new user"""
    template = NotificationTemplates.welcome_new_user(user)

    notification = notification_service.create_notification(
        user_id=user.id,
        title=template['title'],
        message=template['message'],
        notification_type=template['type'],
        data=template['data']
    )

    notification_service.send_notification(notification)


def send_restaurant_registration_notification(restaurant):
    """Send restaurant registration notification"""
    template = NotificationTemplates.restaurant_registered(restaurant)

    notification = notification_service.create_notification(
        user_id=restaurant.owner_id,
        title=template['title'],
        message=template['message'],
        notification_type=template['type'],
        data=template['data']
    )

    notification_service.send_notification(notification)

# Bulk notification functions


def send_bulk_notification(
        user_ids,
        title,
        message,
        notification_type=NotificationType.INFO):
    """Send notification to multiple users"""
    for user_id in user_ids:
        notification = notification_service.create_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type
        )

        notification_service.send_notification(notification)


def send_promotion_notification(promotion):
    """Send promotion notification to all active users"""
    from models import User

    active_users = User.query.filter_by(is_active=True, role='customer').all()
    user_ids = [user.id for user in active_users]

    for user_id in user_ids:
        template = NotificationTemplates.promotion_notification(
            User.query.get(user_id), promotion
        )

        notification = notification_service.create_notification(
            user_id=user_id,
            title=template['title'],
            message=template['message'],
            notification_type=template['type'],
            data=template['data']
        )

        notification_service.send_notification(notification)
