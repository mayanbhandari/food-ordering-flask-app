from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, date
from sqlalchemy import func

# Initialize db here to avoid circular imports
db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for both customers and restaurant owners"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(
        db.Enum('customer', 'restaurant_owner', 'admin'), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    profile_image = db.Column(db.String(255), default='default_profile.png')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    security_answer = db.Column(db.String(120), nullable=False)

    # Relationships
    restaurants = db.relationship(
        'Restaurant',
        backref='owner',
        lazy='dynamic',
        cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='customer', lazy='dynamic')
    reviews = db.relationship('Review', backref='user', lazy='dynamic')
    feedbacks = db.relationship('Feedback', backref='user', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'


class Restaurant(db.Model):
    """Restaurant model"""
    __tablename__ = 'restaurants'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    cuisine_type = db.Column(db.String(50), nullable=False)
    address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(100), nullable=False, default='Downtown')
    state = db.Column(db.String(50), nullable=False, default='CA')
    zip_code = db.Column(db.String(10), nullable=False, default='90210')
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    opening_time = db.Column(db.Time)
    closing_time = db.Column(db.Time)
    image_url = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationships
    menu_items = db.relationship(
        'MenuItem',
        backref='restaurant',
        lazy='dynamic',
        cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='restaurant', lazy='dynamic')
    reviews = db.relationship('Review', backref='restaurant', lazy='dynamic')

    def __repr__(self):
        return f'<Restaurant {self.name}>'


class MenuItem(db.Model):
    """Menu item model"""
    __tablename__ = 'menu_items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(255))
    is_available = db.Column(db.Boolean, default=True)
    is_special = db.Column(db.Boolean, default=False)
    is_deal_of_day = db.Column(db.Boolean, default=False)
    preparation_time = db.Column(db.Integer)  # in minutes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    restaurant_id = db.Column(db.Integer, db.ForeignKey(
        'restaurants.id'), nullable=False)
    diet_type = db.Column(db.Enum('veg', 'non-veg'),
                          nullable=False, default='veg')

    # Relationships
    order_items = db.relationship(
        'OrderItem', backref='menu_item', lazy='dynamic')

    def __repr__(self):
        return f'<MenuItem {self.name} ({self.diet_type})>'

    @property
    def order_quantity_today(self):
        """Total quantity of this item ordered today (sum across all orders)"""
        today = date.today()
        return db.session.query(
            func.sum(
                OrderItem.quantity)).join(Order).filter(
            OrderItem.menu_item_id == self.id,
            func.date(
                Order.created_at) == today).scalar() or 0

    @property
    def has_large_single_order_today(self):
        """Check if this item has any single order with quantity > 10 today"""
        today = date.today()
        return db.session.query(OrderItem).join(Order).filter(
            OrderItem.menu_item_id == self.id,
            func.date(Order.created_at) == today,
            OrderItem.quantity > 10
        ).first() is not None

    @property
    def is_mostly_ordered(self):
        """Item is 'Mostly Ordered' if >10 quantity overall today or any single order >10 today"""
        return self.order_quantity_today > 10 or self.has_large_single_order_today


class Order(db.Model):
    """Order model"""
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    status = db.Column(
        db.Enum(
            'pending',
            'confirmed',
            'preparing',
            'ready',
            'delivered',
            'cancelled'),
        default='pending')
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    customer_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey(
        'restaurants.id'), nullable=False)

    # Relationships
    order_items = db.relationship(
        'OrderItem',
        backref='order',
        lazy='dynamic',
        cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Order {self.order_number}>'


class OrderItem(db.Model):
    """Order item model"""
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    # Price at time of order
    price = db.Column(db.Numeric(10, 2), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey(
        'orders.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey(
        'menu_items.id'), nullable=False)

    def __repr__(self):
        return f'<OrderItem {self.quantity}x {self.menu_item.name}>'


class Cart(db.Model):
    """Shopping cart model"""
    __tablename__ = 'cart'

    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey(
        'menu_items.id'), nullable=False)

    # Relationships
    user = db.relationship('User', backref='cart_items')
    menu_item = db.relationship('MenuItem', backref='cart_items')

    def __repr__(self):
        return f'<Cart {
            self.user.username}: {
            self.quantity}x {
            self.menu_item.name}>'


class Review(db.Model):
    """Review model for restaurants and menu items"""
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey(
        'restaurants.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey(
        'menu_items.id'), nullable=True)

    # Relationships
    menu_item = db.relationship('MenuItem', backref='reviews')

    def __repr__(self):
        return f'<Review {self.rating} stars by {self.user.username}>'


class Feedback(db.Model):
    """Feedback model for customer experience"""
    __tablename__ = 'feedbacks'

    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum('open', 'in_progress',
                       'resolved'), default='open')
    response = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey(
        'restaurants.id'), nullable=True)

    # Relationships
    restaurant = db.relationship('Restaurant', backref='feedbacks')

    def __repr__(self):
        return f'<Feedback {self.subject}>'


class InAppNotification(db.Model):
    """In-app notification model"""
    __tablename__ = 'in_app_notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(
        db.String(50), nullable=False, default='info')
    data = db.Column(db.JSON)  # Additional data for the notification
    read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)

    # Relationships
    user = db.relationship('User', backref='notifications')

    def __repr__(self):
        return f'<InAppNotification {self.title}>'


class Promotion(db.Model):
    """Promotion model for special offers"""
    __tablename__ = 'promotions'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    discount_percentage = db.Column(db.Numeric(5, 2), nullable=False)
    discount_amount = db.Column(db.Numeric(10, 2))  # Fixed discount amount
    # Minimum order for discount
    min_order_amount = db.Column(db.Numeric(10, 2))
    max_discount_amount = db.Column(db.Numeric(10, 2))  # Maximum discount cap
    code = db.Column(db.String(50), unique=True)  # Promo code
    is_active = db.Column(db.Boolean, default=True)
    valid_from = db.Column(db.DateTime, nullable=False)
    valid_until = db.Column(db.DateTime, nullable=False)
    usage_limit = db.Column(db.Integer)  # Total usage limit
    usage_count = db.Column(db.Integer, default=0)  # Current usage count
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationships
    creator = db.relationship('User', backref='created_promotions')

    def __repr__(self):
        return f'<Promotion {self.title}>'

    @property
    def is_valid(self):
        """Check if promotion is currently valid"""
        now = datetime.utcnow()
        return (self.is_active and
                self.valid_from <= now <= self.valid_until and
                (self.usage_limit is None or self.usage_count < self.usage_limit))


class UserPreference(db.Model):
    """User preferences model"""
    __tablename__ = 'user_preferences'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # 'cuisine', 'dietary', 'notification'
    preference_type = db.Column(
        db.String(50),
        nullable=False,
        doc="Type of preference: cuisine, dietary, restaurant, notification")
    preference_value = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='preferences')

    def __repr__(self):
        return f'<UserPreference {
            self.preference_type}: {
            self.preference_value}>'


class OrderTracking(db.Model):
    """Order tracking model for detailed order history"""
    __tablename__ = 'order_tracking'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey(
        'orders.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey(
        'users.id'))  # Who updated the status

    # Relationships
    order = db.relationship('Order', backref='tracking_history')
    updater = db.relationship('User', backref='order_updates')

    def __repr__(self):
        return f'<OrderTracking {self.order.order_number}: {self.status}>'
