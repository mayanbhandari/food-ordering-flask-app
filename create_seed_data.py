"""
Comprehensive seed data for JustEat application
Creates all 10 restaurants with complete data as required
"""

from app import create_app
from models import db, User, Restaurant, MenuItem, Review, Feedback, UserPreference
from werkzeug.security import generate_password_hash
from datetime import datetime, time


def create_comprehensive_seed_data():
    """Create comprehensive seed data with all 10 restaurants"""

    app = create_app()

    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()

        print("🌱 Creating comprehensive seed data...")

        # Create admin user
        admin_user = User(
            username='admin_user',
            email='admin@justeat.com',
            password_hash=generate_password_hash('password123'),
            first_name='Admin',
            last_name='User',
            phone='(555) 000-0000',
            address='Admin Office, JustEat HQ',
            role='admin',
            is_active=True
        )
        db.session.add(admin_user)

        # Create comprehensive restaurant data
        restaurants_data = [
            {
                'owner': {
                    'username': 'mario_owner',
                    'email': 'mario@marios.com',
                    'first_name': 'Mario',
                    'last_name': 'Rossi',
                    'phone': '(555) 111-1111',
                    'address': '123 Italian Street, Little Italy'
                },
                'restaurant': {
                    'name': "Mario's Italian Kitchen",
                    'description': 'Authentic Italian cuisine with fresh ingredients and traditional recipes passed down through generations.',
                    'cuisine_type': 'Italian',
                    'address': '123 Italian Street, Little Italy, NY 10013',
                    'phone': '(555) 111-1111',
                    'email': 'info@marios.com',
                    'opening_time': time(11, 0),
                    'closing_time': time(22, 0)
                },
                'menu_items': [
                    {'name': 'Margherita Pizza', 'description': 'Classic pizza with tomato sauce, mozzarella, and fresh basil',
                        'price': 16.99, 'category': 'Pizza', 'preparation_time': 20, 'is_special': False, 'is_deal_of_day': True},
                    {'name': 'Spaghetti Carbonara', 'description': 'Traditional Roman pasta with eggs, cheese, and pancetta',
                        'price': 18.99, 'category': 'Pasta', 'preparation_time': 15, 'is_special': True, 'is_deal_of_day': False},
                    {'name': 'Chicken Parmigiana', 'description': 'Breaded chicken breast with marinara sauce and mozzarella',
                        'price': 22.99, 'category': 'Main Course', 'preparation_time': 25, 'is_special': False, 'is_deal_of_day': False},
                    {'name': 'Tiramisu', 'description': 'Classic Italian dessert with coffee and mascarpone', 'price': 8.99,
                        'category': 'Desserts', 'preparation_time': 5, 'is_special': False, 'is_deal_of_day': False},
                    {'name': 'Caesar Salad', 'description': 'Fresh romaine lettuce with parmesan and croutons', 'price': 12.99,
                        'category': 'Salads', 'preparation_time': 10, 'is_special': False, 'is_deal_of_day': False},
                    {'name': 'Garlic Bread', 'description': 'Toasted bread with garlic butter and herbs', 'price': 6.99,
                        'category': 'Appetizers', 'preparation_time': 8, 'is_special': False, 'is_deal_of_day': False}
                ]
            },
            {
                'owner': {
                    'username': 'dragon_owner',
                    'email': 'dragon@dragon.com',
                    'first_name': 'Li',
                    'last_name': 'Wei',
                    'phone': '(555) 222-2222',
                    'address': '456 Chinatown Avenue, Chinatown'
                },
                'restaurant': {
                    'name': 'Dragon Palace',
                    'description': 'Authentic Chinese cuisine featuring traditional dishes from various regions of China.',
                    'cuisine_type': 'Chinese',
                    'address': '456 Chinatown Avenue, Chinatown, NY 10013',
                    'phone': '(555) 222-2222',
                    'email': 'info@dragon.com',
                    'opening_time': time(10, 30),
                    'closing_time': time(23, 0)
                },
                'menu_items': [
                    {'name': 'Kung Pao Chicken', 'description': 'Spicy chicken with peanuts and vegetables', 'price': 15.99,
                        'category': 'Main Course', 'preparation_time': 18, 'is_special': True, 'is_deal_of_day': False},
                    {'name': 'Sweet and Sour Pork', 'description': 'Crispy pork with bell peppers in tangy sauce', 'price': 16.99,
                        'category': 'Main Course', 'preparation_time': 20, 'is_special': False, 'is_deal_of_day': True},
                    {'name': 'Vegetable Lo Mein', 'description': 'Stir-fried noodles with mixed vegetables', 'price': 13.99,
                        'category': 'Noodles', 'preparation_time': 12, 'is_special': False, 'is_deal_of_day': False},
                    {'name': 'Spring Rolls', 'description': 'Crispy vegetable spring rolls with sweet chili sauce', 'price': 7.99,
                        'category': 'Appetizers', 'preparation_time': 8, 'is_special': False, 'is_deal_of_day': False},
                    {'name': 'Fortune Cookies', 'description': 'Traditional fortune cookies with messages', 'price': 2.99,
                        'category': 'Desserts', 'preparation_time': 3, 'is_special': False, 'is_deal_of_day': False},
                    {'name': 'Hot and Sour Soup', 'description': 'Traditional Chinese soup with tofu and mushrooms',
                        'price': 9.99, 'category': 'Soups', 'preparation_time': 10, 'is_special': False, 'is_deal_of_day': False}
                ]
            },
            {
                'owner': {
                    'username': 'spice_owner',
                    'email': 'spice@spice.com',
                    'first_name': 'Raj',
                    'last_name': 'Patel',
                    'phone': '(555) 333-3333',
                    'address': '789 Curry Lane, Curry Hill'
                },
                'restaurant': {
                    'name': 'Spice Garden',
                    'description': 'Authentic Indian cuisine with aromatic spices and traditional cooking methods.',
                    'cuisine_type': 'Indian',
                    'address': '789 Curry Lane, Curry Hill, NY 10016',
                    'phone': '(555) 333-3333',
                    'email': 'info@spice.com',
                    'opening_time': time(11, 30),
                    'closing_time': time(22, 30)
                },
                'menu_items': [
                    {'name': 'Chicken Tikka Masala', 'description': 'Tender chicken in creamy tomato sauce', 'price': 17.99,
                        'category': 'Main Course', 'preparation_time': 22, 'is_special': True, 'is_deal_of_day': False},
                    {'name': 'Lamb Biryani', 'description': 'Fragrant basmati rice with spiced lamb', 'price': 19.99,
                        'category': 'Rice', 'preparation_time': 25, 'is_special': False, 'is_deal_of_day': True},
                    {'name': 'Samosas', 'description': 'Crispy pastries filled with spiced potatoes', 'price': 6.99,
                        'category': 'Appetizers', 'preparation_time': 10, 'is_special': False, 'is_deal_of_day': False},
                    {'name': 'Naan Bread', 'description': 'Fresh baked Indian bread', 'price': 4.99,
                        'category': 'Bread', 'preparation_time': 5, 'is_special': False, 'is_deal_of_day': False},
                    {'name': 'Mango Lassi', 'description': 'Refreshing yogurt drink with mango', 'price': 5.99,
                        'category': 'Beverages', 'preparation_time': 3, 'is_special': False, 'is_deal_of_day': False},
                    {'name': 'Dal Makhani', 'description': 'Creamy black lentils with butter', 'price': 14.99,
                        'category': 'Main Course', 'preparation_time': 20, 'is_special': False, 'is_deal_of_day': False}
                ]
            },
            {
                'owner': {
                    'username': 'soeze_owner',
                    'email': 'soeze@soeze.com',
                    'first_name': 'Sarah',
                    'last_name': 'Johnson',
                    'phone': '(555) 444-4444',
                    'address': '321 Healthy Street, Green District'
                },
                'restaurant': {
                    'name': 'So\'Eze Healthy Bites',
                    'description': 'Fresh, healthy, and delicious meals made with organic ingredients and sustainable practices.',
                    'cuisine_type': 'Healthy',
                    'address': '321 Healthy Street, Green District, NY 10001',
                    'phone': '(555) 444-4444',
                    'email': 'info@soeze.com',
                    'opening_time': time(7, 0),
                    'closing_time': time(21, 0)
                },
                'menu_items': [
                    {'name': 'Quinoa Buddha Bowl', 'description': 'Quinoa with roasted vegetables, avocado, and tahini dressing',
                        'price': 14.99, 'category': 'Bowls', 'preparation_time': 15, 'is_special': True, 'is_deal_of_day': False},
                    {'name': 'Green Smoothie Bowl', 'description': 'Acai bowl with fresh fruits and granola', 'price': 12.99,
                        'category': 'Breakfast', 'preparation_time': 8, 'is_special': False, 'is_deal_of_day': True},
                    {'name': 'Grilled Salmon Salad', 'description': 'Fresh salmon with mixed greens and lemon vinaigrette',
                        'price': 18.99, 'category': 'Salads', 'preparation_time': 20, 'is_special': False, 'is_deal_of_day': False},
                    {'name': 'Veggie Wrap', 'description': 'Fresh vegetables wrapped in whole wheat tortilla', 'price': 10.99,
                        'category': 'Wraps', 'preparation_time': 12, 'is_special': False, 'is_deal_of_day': False},
                    {'name': 'Kale Chips', 'description': 'Crispy baked kale with sea salt', 'price': 6.99,
                        'category': 'Snacks', 'preparation_time': 5, 'is_special': False, 'is_deal_of_day': False},
                    {'name': 'Protein Smoothie', 'description': 'Plant-based protein smoothie with berries', 'price': 8.99,
                        'category': 'Beverages', 'preparation_time': 5, 'is_special': False, 'is_deal_of_day': False}
                ]
            },
            {
                'owner': {
                    'username': 'taco_owner',
                    'email': 'taco@taco.com',
                    'first_name': 'Carlos',
                    'last_name': 'Rodriguez',
                    'phone': '(555) 555-5555',
                    'address': '654 Mexican Way, Taco Town'
                },
                'restaurant': {
                    'name': 'Taco Fiesta',
                    'description': 'Authentic Mexican street food with fresh ingredients and bold flavors.',
                    'cuisine_type': 'Mexican',
                    'address': '654 Mexican Way, Taco Town, NY 10014',
                    'phone': '(555) 555-5555',
                    'email': 'info@taco.com',
                    'opening_time': time(11, 0),
                    'closing_time': time(23, 30)
                },
                'menu_items': [
                    {'name': 'Carnitas Tacos', 'description': 'Slow-cooked pork with onions and cilantro', 'price': 12.99,
                        'category': 'Tacos', 'preparation_time': 15, 'is_special': True, 'is_deal_of_day': False},
                    {'name': 'Chicken Burrito', 'description': 'Grilled chicken with rice, beans, and cheese', 'price': 13.99,
                        'category': 'Burritos', 'preparation_time': 18, 'is_special': False, 'is_deal_of_day': True},
                    {'name': 'Guacamole', 'description': 'Fresh avocado dip with lime and cilantro', 'price': 8.99,
                        'category': 'Appetizers', 'preparation_time': 8, 'is_special': False, 'is_deal_of_day': False},
                    {'name': 'Churros', 'description': 'Crispy fried dough with cinnamon sugar', 'price': 6.99,
                        'category': 'Desserts', 'preparation_time': 10, 'is_special': False, 'is_deal_of_day': False},
                    {'name': 'Horchata', 'description': 'Traditional rice milk drink with cinnamon', 'price': 4.99,
                        'category': 'Beverages', 'preparation_time': 3, 'is_special': False, 'is_deal_of_day': False},
                    {'name': 'Quesadilla', 'description': 'Grilled tortilla with cheese and vegetables', 'price': 11.99,
                        'category': 'Main Course', 'preparation_time': 12, 'is_special': False, 'is_deal_of_day': False}
                ]
            },
            {
                'owner': {
                    'username': 'burger_owner',
                    'email': 'burger@burger.com',
                    'first_name': 'Mike',
                    'last_name': 'Thompson',
                    'phone': '(555) 666-6666',
                    'address': '987 Burger Boulevard, Meat District'
                },
                'restaurant': {
                    'name': 'Burger Junction',
                    'description': 'Gourmet burgers made with premium beef and fresh ingredients.',
                    'cuisine_type': 'American',
                    'address': '987 Burger Boulevard, Meat District, NY 10018',
                    'phone': '(555) 666-6666',
                    'email': 'info@burger.com',
                    'opening_time': time(10, 0),
                    'closing_time': time(22, 0)
                },
                'menu_items': [
                    {'name': 'Classic Cheeseburger', 'description': 'Beef patty with cheese, lettuce, tomato, and onion',
                        'price': 14.99, 'category': 'Burgers', 'preparation_time': 15, 'is_special': False, 'is_deal_of_day': True},
                    {'name': 'BBQ Bacon Burger', 'description': 'Beef patty with BBQ sauce, bacon, and onion rings',
                        'price': 17.99, 'category': 'Burgers', 'preparation_time': 18, 'is_special': True, 'is_deal_of_day': False},
                    {'name': 'Chicken Wings', 'description': 'Crispy wings with your choice of sauce', 'price': 12.99,
                        'category': 'Appetizers', 'preparation_time': 20, 'is_special': False, 'is_deal_of_day': False},
                    {'name': 'French Fries', 'description': 'Crispy golden fries with sea salt', 'price': 6.99,
                        'category': 'Sides', 'preparation_time': 8, 'is_special': False, 'is_deal_of_day': False},
                    {'name': 'Chocolate Milkshake', 'description': 'Rich chocolate milkshake with whipped cream', 'price': 7.99,
                        'category': 'Beverages', 'preparation_time': 5, 'is_special': False, 'is_deal_of_day': False},
                    {'name': 'Veggie Burger', 'description': 'Plant-based patty with fresh vegetables', 'price': 13.99,
                        'category': 'Burgers', 'preparation_time': 12, 'is_special': False, 'is_deal_of_day': False}
                ]
            },
            {
                'owner': {
                    'username': 'sushi_owner',
                    'email': 'sushi@sushi.com',
                    'first_name': 'Yuki',
                    'last_name': 'Tanaka',
                    'phone': '(555) 777-7777',
                    'address': '147 Sushi Street, Fish Market'
                },
                'restaurant': {
                    'name': 'Sakura Sushi',
                    'description': 'Fresh sushi and sashimi made with the finest ingredients and traditional techniques.',
                    'cuisine_type': 'Japanese',
                    'address': '147 Sushi Street, Fish Market, NY 10019',
                    'phone': '(555) 777-7777',
                    'email': 'info@sushi.com',
                    'opening_time': time(11, 30),
                    'closing_time': time(22, 0)
                },
                'menu_items': [
                    {'name': 'California Roll', 'description': 'Crab, avocado, and cucumber roll', 'price': 11.99,
                        'category': 'Sushi', 'preparation_time': 12, 'is_special': False, 'is_deal_of_day': True},
                    {'name': 'Salmon Sashimi', 'description': 'Fresh salmon slices', 'price': 16.99,
                        'category': 'Sashimi', 'preparation_time': 8, 'is_special': True, 'is_deal_of_day': False},
                    {'name': 'Dragon Roll', 'description': 'Eel and cucumber topped with avocado', 'price': 18.99,
                        'category': 'Sushi', 'preparation_time': 15, 'is_special': False, 'is_deal_of_day': False},
                    {'name': 'Miso Soup', 'description': 'Traditional Japanese soup with tofu and seaweed', 'price': 4.99,
                        'category': 'Soups', 'preparation_time': 5, 'is_special': False, 'is_deal_of_day': False},
                    {'name': 'Green Tea Ice Cream', 'description': 'Traditional Japanese dessert', 'price': 6.99,
                        'category': 'Desserts', 'preparation_time': 3, 'is_special': False, 'is_deal_of_day': False},
                    {'name': 'Tempura Shrimp', 'description': 'Lightly battered and fried shrimp', 'price': 14.99,
                        'category': 'Appetizers', 'preparation_time': 12, 'is_special': False, 'is_deal_of_day': False}
                ]
            },
            {
                'owner': {
                    'username': 'thai_owner',
                    'email': 'thai@thai.com',
                    'first_name': 'Somchai',
                    'last_name': 'Wong',
                    'phone': '(555) 888-8888',
                    'address': '258 Thai Temple, Spice Quarter'
                },
                'restaurant': {
                    'name': 'Thai Spice House',
                    'description': 'Authentic Thai cuisine with perfect balance of sweet, sour, salty, and spicy flavors.',
                    'cuisine_type': 'Thai',
                    'address': '258 Thai Temple, Spice Quarter, NY 10020',
                    'phone': '(555) 888-8888',
                    'email': 'info@thai.com',
                    'opening_time': time(11, 0),
                    'closing_time': time(22, 30)
                },
                'menu_items': [
                    {'name': 'Pad Thai', 'description': 'Stir-fried rice noodles with shrimp and peanuts', 'price': 15.99,
                        'category': 'Noodles', 'preparation_time': 18, 'is_special': True, 'is_deal_of_day': False},
                    {'name': 'Green Curry', 'description': 'Spicy coconut curry with chicken and vegetables', 'price': 16.99,
                        'category': 'Curry', 'preparation_time': 20, 'is_special': False, 'is_deal_of_day': True},
                    {'name': 'Tom Yum Soup', 'description': 'Spicy and sour soup with shrimp and mushrooms', 'price': 12.99,
                        'category': 'Soups', 'preparation_time': 15, 'is_special': False, 'is_deal_of_day': False},
                    {'name': 'Mango Sticky Rice', 'description': 'Sweet sticky rice with fresh mango', 'price': 8.99,
                        'category': 'Desserts', 'preparation_time': 10, 'is_special': False, 'is_deal_of_day': False},
                    {'name': 'Thai Iced Tea', 'description': 'Sweet and creamy traditional Thai tea', 'price': 4.99,
                        'category': 'Beverages', 'preparation_time': 3, 'is_special': False, 'is_deal_of_day': False},
                    {'name': 'Papaya Salad', 'description': 'Fresh green papaya salad with lime dressing', 'price': 11.99,
                        'category': 'Salads', 'preparation_time': 12, 'is_special': False, 'is_deal_of_day': False}
                ]
            },
            {
                'owner': {
                    'username': 'pizza_owner',
                    'email': 'pizza@pizza.com',
                    'first_name': 'Giuseppe',
                    'last_name': 'Bianchi',
                    'phone': '(555) 999-9999',
                    'address': '369 Pizza Plaza, Little Italy'
                },
                'restaurant': {
                    'name': 'Pizza Corner',
                    'description': 'New York style pizza with thin crust and fresh toppings.',
                    'cuisine_type': 'Pizza',
                    'address': '369 Pizza Plaza, Little Italy, NY 10021',
                    'phone': '(555) 999-9999',
                    'email': 'info@pizza.com',
                    'opening_time': time(10, 0),
                    'closing_time': time(23, 0)
                },
                'menu_items': [
                    {'name': 'Pepperoni Pizza', 'description': 'Classic pizza with pepperoni and mozzarella', 'price': 18.99,
                        'category': 'Pizza', 'preparation_time': 20, 'is_special': False, 'is_deal_of_day': True},
                    {'name': 'Supreme Pizza', 'description': 'Pizza with pepperoni, sausage, peppers, and onions',
                        'price': 22.99, 'category': 'Pizza', 'preparation_time': 25, 'is_special': True, 'is_deal_of_day': False},
                    {'name': 'Caesar Salad', 'description': 'Fresh romaine with parmesan and croutons', 'price': 11.99,
                        'category': 'Salads', 'preparation_time': 10, 'is_special': False, 'is_deal_of_day': False},
                    {'name': 'Garlic Bread', 'description': 'Toasted bread with garlic butter', 'price': 6.99,
                        'category': 'Appetizers', 'preparation_time': 8, 'is_special': False, 'is_deal_of_day': False},
                    {'name': 'Cannoli', 'description': 'Italian pastry with sweet ricotta filling', 'price': 7.99,
                        'category': 'Desserts', 'preparation_time': 5, 'is_special': False, 'is_deal_of_day': False},
                    {'name': 'Buffalo Wings', 'description': 'Spicy chicken wings with blue cheese dip', 'price': 13.99,
                        'category': 'Appetizers', 'preparation_time': 15, 'is_special': False, 'is_deal_of_day': False}
                ]
            },
            {
                'owner': {
                    'username': 'mediterranean_owner',
                    'email': 'med@med.com',
                    'first_name': 'Ahmed',
                    'last_name': 'Hassan',
                    'phone': '(555) 000-1111',
                    'address': '741 Olive Street, Mediterranean Quarter'
                },
                'restaurant': {
                    'name': 'Mediterranean Delight',
                    'description': 'Fresh Mediterranean cuisine with olive oil, herbs, and fresh vegetables.',
                    'cuisine_type': 'Mediterranean',
                    'address': '741 Olive Street, Mediterranean Quarter, NY 10022',
                    'phone': '(555) 000-1111',
                    'email': 'info@med.com',
                    'opening_time': time(11, 0),
                    'closing_time': time(22, 0)
                },
                'menu_items': [
                    {'name': 'Chicken Shawarma', 'description': 'Marinated chicken with tahini and vegetables', 'price': 15.99,
                        'category': 'Main Course', 'preparation_time': 20, 'is_special': True, 'is_deal_of_day': False},
                    {'name': 'Hummus Plate', 'description': 'Creamy hummus with pita bread and olives', 'price': 10.99,
                        'category': 'Appetizers', 'preparation_time': 8, 'is_special': False, 'is_deal_of_day': True},
                    {'name': 'Greek Salad', 'description': 'Fresh vegetables with feta cheese and olive oil', 'price': 12.99,
                        'category': 'Salads', 'preparation_time': 10, 'is_special': False, 'is_deal_of_day': False},
                    {'name': 'Baklava', 'description': 'Sweet pastry with nuts and honey', 'price': 8.99,
                        'category': 'Desserts', 'preparation_time': 5, 'is_special': False, 'is_deal_of_day': False},
                    {'name': 'Turkish Coffee', 'description': 'Traditional strong coffee', 'price': 4.99,
                        'category': 'Beverages', 'preparation_time': 5, 'is_special': False, 'is_deal_of_day': False},
                    {'name': 'Falafel Wrap', 'description': 'Crispy falafel with vegetables and tahini', 'price': 11.99,
                        'category': 'Wraps', 'preparation_time': 12, 'is_special': False, 'is_deal_of_day': False}
                ]
            }
        ]

        # Create restaurant owners and restaurants
        for restaurant_data in restaurants_data:
            # Create owner
            owner = User(
                username=restaurant_data['owner']['username'],
                email=restaurant_data['owner']['email'],
                password_hash=generate_password_hash('password123'),
                first_name=restaurant_data['owner']['first_name'],
                last_name=restaurant_data['owner']['last_name'],
                phone=restaurant_data['owner']['phone'],
                address=restaurant_data['owner']['address'],
                role='restaurant_owner',
                is_active=True
            )
            db.session.add(owner)
            db.session.flush()  # Get the ID

            # Create restaurant
            restaurant = Restaurant(
                name=restaurant_data['restaurant']['name'],
                description=restaurant_data['restaurant']['description'],
                cuisine_type=restaurant_data['restaurant']['cuisine_type'],
                address=restaurant_data['restaurant']['address'],
                phone=restaurant_data['restaurant']['phone'],
                email=restaurant_data['restaurant']['email'],
                opening_time=restaurant_data['restaurant']['opening_time'],
                closing_time=restaurant_data['restaurant']['closing_time'],
                owner_id=owner.id,
                is_active=True
            )
            db.session.add(restaurant)
            db.session.flush()  # Get the ID

            # Create menu items
            for item_data in restaurant_data['menu_items']:
                menu_item = MenuItem(
                    name=item_data['name'],
                    description=item_data['description'],
                    price=item_data['price'],
                    category=item_data['category'],
                    preparation_time=item_data['preparation_time'],
                    is_special=item_data['is_special'],
                    is_deal_of_day=item_data['is_deal_of_day'],
                    restaurant_id=restaurant.id,
                    is_available=True
                )
                db.session.add(menu_item)

        # Create sample customers
        customers_data = [
            {
                'username': 'john_doe',
                'email': 'john@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'phone': '(555) 100-1000',
                'address': '123 Main Street, Downtown'
            },
            {
                'username': 'jane_smith',
                'email': 'jane@example.com',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'phone': '(555) 200-2000',
                'address': '456 Oak Avenue, Uptown'
            },
            {
                'username': 'bob_wilson',
                'email': 'bob@example.com',
                'first_name': 'Bob',
                'last_name': 'Wilson',
                'phone': '(555) 300-3000',
                'address': '789 Pine Street, Midtown'
            }
        ]

        for customer_data in customers_data:
            customer = User(
                username=customer_data['username'],
                email=customer_data['email'],
                password_hash=generate_password_hash('password123'),
                first_name=customer_data['first_name'],
                last_name=customer_data['last_name'],
                phone=customer_data['phone'],
                address=customer_data['address'],
                role='customer',
                is_active=True
            )
            db.session.add(customer)

        # Commit all data
        db.session.commit()

        print("✅ Seed data created successfully!")
        print(f"📊 Created {len(restaurants_data)} restaurants with owners")
        print(f"👥 Created {len(customers_data)} customers")
        print("🔑 Created 1 admin user")
        print("\n🔐 Login credentials:")
        print("Admin: admin_user / password123")
        print("Customers: john_doe, jane_smith, bob_wilson / password123")
        print("Restaurant Owners: mario_owner, dragon_owner, spice_owner, soeze_owner, taco_owner, burger_owner, sushi_owner, thai_owner, pizza_owner, mediterranean_owner / password123")


if __name__ == '__main__':
    create_comprehensive_seed_data()
