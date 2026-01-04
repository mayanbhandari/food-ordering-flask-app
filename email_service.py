"""
Email service for JustEat application
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app, render_template
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Email service for sending notifications"""

    def __init__(self):
        self.smtp_server = current_app.config.get(
            'SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = current_app.config.get('SMTP_PORT', 587)
        self.smtp_username = current_app.config.get('SMTP_USERNAME')
        self.smtp_password = current_app.config.get('SMTP_PASSWORD')
        self.from_email = current_app.config.get(
            'FROM_EMAIL', 'noreply@justeat.com')
        self.from_name = current_app.config.get('FROM_NAME', 'JustEat')

    def send_email(self, to_email, subject, html_content, text_content=None):
        """Send email to recipient"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email

            # Add text content
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)

            # Add HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)

            # Send email
            if self.smtp_username and self.smtp_password:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
                server.quit()
                logger.info(f"Email sent successfully to {to_email}")
                return True
            else:
                logger.warning(
                    "SMTP credentials not configured, email not sent")
                return False

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    def send_welcome_email(self, user):
        """Send welcome email to new user"""
        subject = f"Welcome to {
            current_app.config.get(
                'APP_NAME', 'JustEat')}!"

        html_content = render_template('emails/welcome.html', user=user)
        text_content = f"""
        Welcome to JustEat!

        Hi {user.first_name},

        Thank you for joining JustEat! We're excited to have you on board.

        You can now:
        - Browse restaurants and menus
        - Place orders
        - Track your orders
        - Leave reviews

        If you have any questions, feel free to contact our support team.

        Best regards,
        The JustEat Team
        """

        return self.send_email(user.email, subject, html_content, text_content)

    def send_order_confirmation(self, order):
        """Send order confirmation email"""
        subject = f"Order Confirmation - {order.order_number}"

        html_content = render_template(
            'emails/order_confirmation.html', order=order)
        text_content = f"""
        Order Confirmation

        Hi {order.customer.first_name},

        Your order has been confirmed!

        Order Number: {order.order_number}
        Restaurant: {order.restaurant.name}
        Total Amount: ${order.total_amount:.2f}

        We'll notify you when your order is ready.

        Thank you for choosing JustEat!
        """

        return self.send_email(
            order.customer.email,
            subject,
            html_content,
            text_content)

    def send_order_status_update(self, order):
        """Send order status update email"""
        subject = f"Order Update - {order.order_number}"

        html_content = render_template(
            'emails/order_status_update.html', order=order)
        text_content = f"""
        Order Status Update

        Hi {order.customer.first_name},

        Your order status has been updated:

        Order Number: {order.order_number}
        Restaurant: {order.restaurant.name}
        New Status: {order.status.title()}

        Thank you for choosing JustEat!
        """

        return self.send_email(
            order.customer.email,
            subject,
            html_content,
            text_content)

    def send_password_reset(self, user, reset_token):
        """Send password reset email"""
        subject = "Password Reset Request"

        reset_url = f"{
            current_app.config.get(
                'BASE_URL',
                'http://localhost:5000')}/auth/reset-password?token={reset_token}"

        html_content = render_template('emails/password_reset.html',
                                       user=user, reset_url=reset_url)
        text_content = f"""
        Password Reset Request

        Hi {user.first_name},

        You requested a password reset for your JustEat account.

        Click the link below to reset your password:
        {reset_url}

        If you didn't request this, please ignore this email.

        Best regards,
        The JustEat Team
        """

        return self.send_email(user.email, subject, html_content, text_content)

    def send_restaurant_registration_confirmation(self, restaurant):
        """Send restaurant registration confirmation"""
        subject = "Restaurant Registration Confirmed"

        html_content = render_template('emails/restaurant_confirmation.html',
                                       restaurant=restaurant)
        text_content = f"""
        Restaurant Registration Confirmed

        Hi {restaurant.owner.first_name},

        Your restaurant "{restaurant.name}" has been successfully registered on JustEat!

        You can now:
        - Manage your menu
        - Process orders
        - View analytics
        - Respond to reviews

        Welcome to the JustEat family!
        """

        return self.send_email(
            restaurant.owner.email,
            subject,
            html_content,
            text_content)

    def send_review_notification(self, review):
        """Send notification when restaurant receives a review"""
        subject = f"New Review for {review.restaurant.name}"

        html_content = render_template(
            'emails/review_notification.html', review=review)
        text_content = f"""
        New Review Received
        
        Hi {review.restaurant.owner.first_name},
        
        Your restaurant "{review.restaurant.name}" received a new review:
        
        Rating: {review.rating}/5 stars
        Customer: {review.user.first_name} {review.user.last_name}
        
        {f'Comment: {review.comment}' if review.comment else ''}

        Log in to your restaurant dashboard to respond.
        """

        return self.send_email(
            review.restaurant.owner.email,
            subject,
            html_content,
            text_content)

    def send_feedback_notification(self, feedback):
        """Send notification when restaurant receives feedback"""
        subject = f"New Feedback for {
            feedback.restaurant.name if feedback.restaurant else 'JustEat'}"

        html_content = render_template(
            'emails/feedback_notification.html', feedback=feedback)
        text_content = f"""
        New Feedback Received

        Hi {feedback.restaurant.owner.first_name if feedback.restaurant else 'Admin'},

        {"Your restaurant" if feedback.restaurant else "JustEat"} received new feedback:

        Subject: {feedback.subject}
        From: {feedback.user.first_name} {feedback.user.last_name}

        Message: {feedback.message}

        Log in to respond to the feedback.
        """

        recipient_email = feedback.restaurant.owner.email if feedback.restaurant else current_app.config.get(
            'ADMIN_EMAIL')
        return self.send_email(
            recipient_email,
            subject,
            html_content,
            text_content)


# Global email service instance
email_service = EmailService()


def send_welcome_email(user):
    """Send welcome email to user"""
    return email_service.send_welcome_email(user)


def send_order_confirmation(order):
    """Send order confirmation email"""
    return email_service.send_order_confirmation(order)


def send_order_status_update(order):
    """Send order status update email"""
    return email_service.send_order_status_update(order)


def send_password_reset(user, reset_token):
    """Send password reset email"""
    return email_service.send_password_reset(user, reset_token)


def send_restaurant_registration_confirmation(restaurant):
    """Send restaurant registration confirmation"""
    return email_service.send_restaurant_registration_confirmation(restaurant)


def send_review_notification(review):
    """Send review notification"""
    return email_service.send_review_notification(review)


def send_feedback_notification(feedback):
    """Send feedback notification"""
    return email_service.send_feedback_notification(feedback)
