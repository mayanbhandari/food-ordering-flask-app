"""
Custom validators for JustEat application
"""

from wtforms.validators import ValidationError
import re
from datetime import datetime, time


class UniqueUsername:
    """Validator to ensure username is unique"""

    def __init__(self, message=None):
        self.message = message or 'Username already exists'

    def __call__(self, form, field):
        from models import User
        user = User.query.filter_by(username=field.data).first()
        if user:
            raise ValidationError(self.message)


class UniqueEmail:
    """Validator to ensure email is unique"""

    def __init__(self, message=None):
        self.message = message or 'Email already exists'

    def __call__(self, form, field):
        from models import User
        user = User.query.filter_by(email=field.data).first()
        if user:
            raise ValidationError(self.message)


class ValidPhoneNumber:
    """Validator for phone number format"""

    def __init__(self, message=None):
        self.message = message or 'Invalid phone number format'

    def __call__(self, form, field):
        if field.data:
            # Remove all non-digit characters
            digits = re.sub(r'\D', '', field.data)
            # Check if it's a valid length (10-15 digits)
            if not (10 <= len(digits) <= 15):
                raise ValidationError(self.message)


class ValidPassword:
    """Validator for password strength"""

    def __init__(
            self,
            min_length=6,
            require_uppercase=True,
            require_lowercase=True,
            require_digits=True,
            message=None):
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digits = require_digits
        self.message = message or 'Password does not meet requirements'

    def __call__(self, form, field):
        password = field.data

        if len(password) < self.min_length:
            raise ValidationError(
                f'Password must be at least {self.min_length} characters long')

        if self.require_uppercase and not re.search(r'[A-Z]', password):
            raise ValidationError(
                'Password must contain at least one uppercase letter')

        if self.require_lowercase and not re.search(r'[a-z]', password):
            raise ValidationError(
                'Password must contain at least one lowercase letter')

        if self.require_digits and not re.search(r'\d', password):
            raise ValidationError('Password must contain at least one digit')


class ValidPrice:
    """Validator for price values"""

    def __init__(self, min_price=0.01, max_price=999.99, message=None):
        self.min_price = min_price
        self.max_price = max_price
        self.message = message or f'Price must be between ${min_price} and ${max_price}'

    def __call__(self, form, field):
        try:
            price = float(field.data)
            if not (self.min_price <= price <= self.max_price):
                raise ValidationError(self.message)
        except (ValueError, TypeError):
            raise ValidationError('Invalid price format')


class ValidTimeRange:
    """Validator for time range (opening and closing times)"""

    def __init__(self, message=None):
        self.message = message or 'Closing time must be after opening time'

    def __call__(self, form, field):
        opening_time = form.opening_time.data
        closing_time = form.closing_time.data

        if opening_time and closing_time:
            if closing_time <= opening_time:
                raise ValidationError(self.message)


class ValidQuantity:
    """Validator for quantity values"""

    def __init__(self, min_quantity=1, max_quantity=99, message=None):
        self.min_quantity = min_quantity
        self.max_quantity = max_quantity
        self.message = message or f'Quantity must be between {min_quantity} and {max_quantity}'

    def __call__(self, form, field):
        try:
            quantity = int(field.data)
            if not (self.min_quantity <= quantity <= self.max_quantity):
                raise ValidationError(self.message)
        except (ValueError, TypeError):
            raise ValidationError('Invalid quantity format')


class ValidRating:
    """Validator for rating values"""

    def __init__(self, min_rating=1, max_rating=5, message=None):
        self.min_rating = min_rating
        self.max_rating = max_rating
        self.message = message or f'Rating must be between {min_rating} and {max_rating}'

    def __call__(self, form, field):
        try:
            rating = int(field.data)
            if not (self.min_rating <= rating <= self.max_rating):
                raise ValidationError(self.message)
        except (ValueError, TypeError):
            raise ValidationError('Invalid rating format')


class ValidOrderStatus:
    """Validator for order status values"""

    def __init__(self, message=None):
        self.valid_statuses = ['pending', 'confirmed',
                               'preparing', 'ready', 'delivered', 'cancelled']
        self.message = message or f'Status must be one of: {
            ", ".join(
                self.valid_statuses)}'

    def __call__(self, form, field):
        if field.data not in self.valid_statuses:
            raise ValidationError(self.message)


class ValidCuisineType:
    """Validator for cuisine type values"""

    def __init__(self, message=None):
        self.valid_cuisines = [
            'Italian', 'Chinese', 'Indian', 'Mexican', 'American',
            'Japanese', 'Thai', 'Mediterranean', 'Fast Food', 'Desserts'
        ]
        self.message = message or f'Cuisine type must be one of: {
            ", ".join(
                self.valid_cuisines)}'

    def __call__(self, form, field):
        if field.data not in self.valid_cuisines:
            raise ValidationError(self.message)


class ValidMenuItemCategory:
    """Validator for menu item category values"""

    def __init__(self, message=None):
        self.valid_categories = [
            'Appetizers', 'Main Course', 'Desserts', 'Beverages',
            'Salads', 'Soups', 'Pizza', 'Pasta', 'Sandwiches', 'Sides'
        ]
        self.message = message or f'Category must be one of: {
            ", ".join(
                self.valid_categories)}'

    def __call__(self, form, field):
        if field.data not in self.valid_categories:
            raise ValidationError(self.message)


class ValidPreparationTime:
    """Validator for preparation time values"""

    def __init__(self, min_time=1, max_time=120, message=None):
        self.min_time = min_time
        self.max_time = max_time
        self.message = message or f'Preparation time must be between {min_time} and {max_time} minutes'

    def __call__(self, form, field):
        try:
            time = int(field.data)
            if not (self.min_time <= time <= self.max_time):
                raise ValidationError(self.message)
        except (ValueError, TypeError):
            raise ValidationError('Invalid preparation time format')


class ValidRestaurantName:
    """Validator for restaurant name format"""

    def __init__(self, message=None):
        self.message = message or 'Restaurant name contains invalid characters'

    def __call__(self, form, field):
        name = field.data
        # Allow letters, numbers, spaces, hyphens, apostrophes, and periods
        if not re.match(r"^[a-zA-Z0-9\s\-'\.]+$", name):
            raise ValidationError(self.message)


class ValidMenuItemName:
    """Validator for menu item name format"""

    def __init__(self, message=None):
        self.message = message or 'Menu item name contains invalid characters'

    def __call__(self, form, field):
        name = field.data
        # Allow letters, numbers, spaces, hyphens, apostrophes, and periods
        if not re.match(r"^[a-zA-Z0-9\s\-'\.]+$", name):
            raise ValidationError(self.message)


class ValidAddress:
    """Validator for address format"""

    def __init__(self, message=None):
        self.message = message or 'Address contains invalid characters'

    def __call__(self, form, field):
        address = field.data
        # Allow letters, numbers, spaces, hyphens, commas, periods, and common
        # address symbols
        if not re.match(r"^[a-zA-Z0-9\s\-',\.#/]+$", address):
            raise ValidationError(self.message)


class ValidDescription:
    """Validator for description format"""

    def __init__(self, max_length=500, message=None):
        self.max_length = max_length
        self.message = message or f'Description must be less than {max_length} characters'

    def __call__(self, form, field):
        if field.data and len(field.data) > self.max_length:
            raise ValidationError(self.message)


class ValidComment:
    """Validator for comment format"""

    def __init__(self, max_length=1000, message=None):
        self.max_length = max_length
        self.message = message or f'Comment must be less than {max_length} characters'

    def __call__(self, form, field):
        if field.data and len(field.data) > self.max_length:
            raise ValidationError(self.message)


class ValidSubject:
    """Validator for subject format"""

    def __init__(self, max_length=200, message=None):
        self.max_length = max_length
        self.message = message or f'Subject must be less than {max_length} characters'

    def __call__(self, form, field):
        if field.data and len(field.data) > self.max_length:
            raise ValidationError(self.message)


class ValidMessage:
    """Validator for message format"""

    def __init__(self, max_length=2000, message=None):
        self.max_length = max_length
        self.message = message or f'Message must be less than {max_length} characters'

    def __call__(self, form, field):
        if field.data and len(field.data) > self.max_length:
            raise ValidationError(self.message)


class ValidOrderNumber:
    """Validator for order number format"""

    def __init__(self, message=None):
        self.message = message or 'Invalid order number format'

    def __call__(self, form, field):
        order_number = field.data
        # Order number should start with ORD followed by timestamp and user ID
        if not re.match(r"^ORD\d{14}\d+$", order_number):
            raise ValidationError(self.message)


class ValidUsername:
    """Validator for username format"""

    def __init__(self, min_length=4, max_length=20, message=None):
        self.min_length = min_length
        self.max_length = max_length
        self.message = message or f'Username must be {min_length}-{max_length} characters and contain only letters, numbers, and underscores'

    def __call__(self, form, field):
        username = field.data
        if not (self.min_length <= len(username) <= self.max_length):
            raise ValidationError(
                f'Username must be {self.min_length}-{self.max_length} characters')

        if not re.match(r"^[a-zA-Z0-9_]+$", username):
            raise ValidationError(
                'Username can only contain letters, numbers, and underscores')
