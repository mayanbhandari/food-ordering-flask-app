from werkzeug.security import generate_password_hash
from models import User, Restaurant, MenuItem, Order, OrderItem, Cart, Review, Feedback
from models import db
from app import create_app
import unittest
import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class JustEatTestCase(unittest.TestCase):
    """Test cases for JustEat application"""

    def setUp(self):
        """Set up test environment"""
        self.app = create_app('testing')
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False

        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

        # Create test user
        self.test_user = User(
            username='testuser',
            email='test@example.com',
            password_hash=generate_password_hash('password123'),
            role='customer',
            first_name='Test',
            last_name='User',
            profile_image="default_profile.png",
            is_active=True,
            security_answer="Test Answer"
        )
        db.session.add(self.test_user)
        db.session.commit()

    def tearDown(self):
        """Clean up after tests"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        """Test home page loads correctly"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'JustEat', response.data)

    def test_login_page(self):
        """Test login page loads correctly"""
        response = self.client.get('/auth/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)

    def test_restaurants_page(self):
        """Test restaurants page loads correctly"""
        response = self.client.get('/restaurants')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Restaurants', response.data)

    def test_user_creation(self):
        """Test user creation"""
        user = User(
            username='newuser',
            email='new@example.com',
            password_hash=generate_password_hash('newpass'),
            role='customer',
            first_name='New',
            last_name='User',
            security_answer='Test Answer'
        )
        db.session.add(user)
        db.session.commit()

        retrieved_user = User.query.filter_by(username='newuser').first()
        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user.email, 'new@example.com')

    def test_restaurant_creation(self):
        """Test restaurant creation"""
        restaurant = Restaurant(
            name='Test Restaurant',
            description='A test restaurant',
            cuisine_type='Italian',
            address='123 Test St',
            phone='555-0123',
            owner_id=self.test_user.id
        )
        db.session.add(restaurant)
        db.session.commit()

        retrieved_restaurant = Restaurant.query.filter_by(
            name='Test Restaurant').first()
        self.assertIsNotNone(retrieved_restaurant)
        self.assertEqual(retrieved_restaurant.cuisine_type, 'Italian')

    def test_menu_item_creation(self):
        """Test menu item creation"""
        # First create a restaurant
        restaurant = Restaurant(
            name='Test Restaurant',
            description='A test restaurant',
            cuisine_type='Italian',
            address='123 Test St',
            phone='555-0123',
            owner_id=self.test_user.id
        )
        db.session.add(restaurant)
        db.session.commit()

        # Create menu item
        menu_item = MenuItem(
            name='Test Pizza',
            description='A delicious test pizza',
            price=15.99,
            category='Pizza',
            restaurant_id=restaurant.id
        )
        db.session.add(menu_item)
        db.session.commit()

        retrieved_item = MenuItem.query.filter_by(name='Test Pizza').first()
        self.assertIsNotNone(retrieved_item)
        self.assertEqual(float(retrieved_item.price), 15.99)

    def test_order_creation(self):
        """Test order creation"""
        # Create restaurant and menu item first
        restaurant = Restaurant(
            name='Test Restaurant',
            description='A test restaurant',
            cuisine_type='Italian',
            address='123 Test St',
            phone='555-0123',
            owner_id=self.test_user.id
        )
        db.session.add(restaurant)
        db.session.commit()

        menu_item = MenuItem(
            name='Test Pizza',
            description='A delicious test pizza',
            price=15.99,
            category='Pizza',
            restaurant_id=restaurant.id
        )
        db.session.add(menu_item)
        db.session.commit()

        # Create order
        order = Order(
            order_number='TEST001',
            total_amount=15.99,
            customer_id=self.test_user.id,
            restaurant_id=restaurant.id
        )
        db.session.add(order)
        db.session.commit()

        # Create order item
        order_item = OrderItem(
            order_id=order.id,
            menu_item_id=menu_item.id,
            quantity=1,
            price=15.99
        )
        db.session.add(order_item)
        db.session.commit()

        retrieved_order = Order.query.filter_by(order_number='TEST001').first()
        self.assertIsNotNone(retrieved_order)
        self.assertEqual(float(retrieved_order.total_amount), 15.99)
        self.assertEqual(retrieved_order.order_items.count(), 1)

    def test_cart_functionality(self):
        """Test cart functionality"""
        # Create restaurant and menu item first
        restaurant = Restaurant(
            name='Test Restaurant',
            description='A test restaurant',
            cuisine_type='Italian',
            address='123 Test St',
            phone='555-0123',
            owner_id=self.test_user.id
        )
        db.session.add(restaurant)
        db.session.commit()

        menu_item = MenuItem(
            name='Test Pizza',
            description='A delicious test pizza',
            price=15.99,
            category='Pizza',
            restaurant_id=restaurant.id
        )
        db.session.add(menu_item)
        db.session.commit()

        # Add to cart
        cart_item = Cart(
            user_id=self.test_user.id,
            menu_item_id=menu_item.id,
            quantity=2
        )
        db.session.add(cart_item)
        db.session.commit()

        retrieved_cart = Cart.query.filter_by(
            user_id=self.test_user.id).first()
        self.assertIsNotNone(retrieved_cart)
        self.assertEqual(retrieved_cart.quantity, 2)

    def test_review_creation(self):
        """Test review creation"""
        # Create restaurant first
        restaurant = Restaurant(
            name='Test Restaurant',
            description='A test restaurant',
            cuisine_type='Italian',
            address='123 Test St',
            phone='555-0123',
            owner_id=self.test_user.id
        )
        db.session.add(restaurant)
        db.session.commit()

        # Create review
        review = Review(
            rating=5,
            comment='Excellent food!',
            user_id=self.test_user.id,
            restaurant_id=restaurant.id
        )
        db.session.add(review)
        db.session.commit()

        retrieved_review = Review.query.filter_by(
            user_id=self.test_user.id).first()
        self.assertIsNotNone(retrieved_review)
        self.assertEqual(retrieved_review.rating, 5)
        self.assertEqual(retrieved_review.comment, 'Excellent food!')

    def test_feedback_creation(self):
        """Test feedback creation"""
        # Create restaurant first
        restaurant = Restaurant(
            name='Test Restaurant',
            description='A test restaurant',
            cuisine_type='Italian',
            address='123 Test St',
            phone='555-0123',
            owner_id=self.test_user.id
        )
        db.session.add(restaurant)
        db.session.commit()

        # Create feedback
        feedback = Feedback(
            subject='Great service',
            message='The food was amazing and delivery was fast!',
            user_id=self.test_user.id,
            restaurant_id=restaurant.id
        )
        db.session.add(feedback)
        db.session.commit()

        retrieved_feedback = Feedback.query.filter_by(
            user_id=self.test_user.id).first()
        self.assertIsNotNone(retrieved_feedback)
        self.assertEqual(retrieved_feedback.subject, 'Great service')
        self.assertEqual(retrieved_feedback.status, 'open')


if __name__ == '__main__':
    unittest.main()
