"""
Seed data for JustEat application
"""

from models import db, User, Restaurant, MenuItem, Order, OrderItem, Review, Feedback
from werkzeug.security import generate_password_hash
from datetime import time


def seed_data():
    if Restaurant.query.first():
        return False

    # insert data
    db.session.commit()
    return True



        # Create admin
        admin = User(
            username="admin_user",
            email="admin@justeat.com",
            password_hash=generate_password_hash("password123"),
            first_name="Admin",
            last_name="User",
            role="admin",
            is_active=True,
            security_answer="Delhi",
            profile_image="uploads/profile_images/profile_photo.jpeg"
        )
        db.session.add(admin)

        # Create customers
        customers = [
            User(
                username="mayan_bhandari",
                email="mayan@example.com",
                password_hash=generate_password_hash("password123"),
                first_name="Mayan",
                last_name="Bhandari",
                role="customer",
                is_active=True,
                security_answer="Delhi",
                profile_image="uploads/profile_images/profile_photo.jpeg"
            ),
            User(
                username="priya_mehta",
                email="priya@example.com",
                password_hash=generate_password_hash("password123"),
                first_name="Priya",
                last_name="Mehta",
                role="customer",
                is_active=True,
                security_answer="Gurugram",
                profile_image="uploads/profile_images/profile_photo.jpeg"
            ),
            User(
                username="rahul_gupta",
                email="rahul@example.com",
                password_hash=generate_password_hash("password123"),
                first_name="Rahul",
                last_name="Gupta",
                role="customer",
                is_active=True,
                security_answer="Faridabad",
                profile_image="uploads/profile_images/profile_photo.jpeg"
            )
        ]
        for customer in customers:
            db.session.add(customer)

        # Create restaurant owners
        owners = [
            User(
                username="vikram_owner",
                email="vikram@tajmahal.com",
                password_hash=generate_password_hash("password123"),
                first_name="Vikram",
                last_name="Singh",
                role="restaurant_owner",
                is_active=True,
                security_answer="Delhi",
                profile_image="uploads/profile_images/profile_photo.jpeg"
            ),
            User(
                username="anita_owner",
                email="anita@shangrila.com",
                password_hash=generate_password_hash("password123"),
                first_name="Anita",
                last_name="Rao",
                role="restaurant_owner",
                is_active=True,
                security_answer="Gurugram",
                profile_image="uploads/profile_images/profile_photo.jpeg"
            ),
            User(
                username="raj_owner",
                email="raj@spicehut.com",
                password_hash=generate_password_hash("password123"),
                first_name="Raj",
                last_name="Patel",
                role="restaurant_owner",
                is_active=True,
                security_answer="Faridabad",
                profile_image="uploads/profile_images/profile_photo.jpeg"
            ),
            User(
                username="meera_owner",
                email="meera@sofra.com",
                password_hash=generate_password_hash("password123"),
                first_name="Meera",
                last_name="Joshi",
                role="restaurant_owner",
                is_active=True,
                security_answer="Delhi",
                profile_image="uploads/profile_images/profile_photo.jpeg"
            ),
            User(
                username="arvind_owner",
                email="arvind@burgerbazaar.com",
                password_hash=generate_password_hash("password123"),
                first_name="Arvind",
                last_name="Kumar",
                role="restaurant_owner",
                is_active=True,
                security_answer="Gurugram",
                profile_image="uploads/profile_images/profile_photo.jpeg"
            ),
            User(
                username="neha_owner",
                email="neha@sushiwala.com",
                password_hash=generate_password_hash("password123"),
                first_name="Neha",
                last_name="Shah",
                role="restaurant_owner",
                is_active=True,
                security_answer="Faridabad",
                profile_image="uploads/profile_images/profile_photo.jpeg"
            )
        ]
        for owner in owners:
            db.session.add(owner)

        db.session.flush()

        restaurants_data = [{"name": "Spice Route",
                             "description": "Authentic North Indian flavors with traditional recipes",
                             "cuisine_type": "North Indian",
                             "address": "12 Connaught Street",
                             "city": "New Delhi",
                             "state": "Delhi",
                             "zip_code": "110001",
                             "phone": "+91 11 2345 6789",
                             "owner_id": owners[0].id,
                             "opening_time": time(10,
                                                  0),
                             "closing_time": time(22,
                                                  0),
                             "image_url": "uploads/restaurants/spice-route.jpeg",
                             "menu_items": [{"name": "Butter Chicken",
                                             "price": 499,
                                             "category": "Main Course",
                                             "diet_type": "non-veg",
                                             "is_special": True,
                                             "image_url": "uploads/menu_items/butter-chicken.jpeg"},
                                            {"name": "Paneer Tikka",
                                             "price": 299,
                                             "category": "Appetizers",
                                             "diet_type": "veg",
                                             "image_url": "uploads/menu_items/paneer-tikka.jpg"},
                                            {"name": "Dal Makhani",
                                             "price": 349,
                                             "category": "Main Course",
                                             "diet_type": "veg",
                                             "image_url": "uploads/menu_items/dal-mahani.jpeg"},
                                            {"name": "Naan",
                                             "price": 99,
                                             "category": "Sides",
                                             "diet_type": "veg",
                                             "image_url": "uploads/menu_items/naan.jpg"},
                                            {"name": "Gulab Jamun",
                                             "price": 149,
                                             "category": "Desserts",
                                             "diet_type": "veg",
                                             "is_deal_of_day": True,
                                             "image_url": "uploads/menu_items/gulap-jamun.jpeg"},
                                            ]},
                            {"name": "Curry Leaf",
                             "description": "South Indian delicacies and traditional dishes",
                             "cuisine_type": "South Indian",
                             "address": "45 Brigade Road",
                             "city": "Bengaluru",
                             "state": "Karnataka",
                             "zip_code": "560001",
                             "phone": "+91 80 2345 6789",
                             "owner_id": owners[1].id,
                             "opening_time": time(8,
                                                  0),
                             "closing_time": time(21,
                                                  0),
                             "image_url": "uploads/restaurants/curry-leaf.jpeg",
                             "menu_items": [{"name": "Masala Dosa",
                                             "price": 199,
                                             "category": "Main Course",
                                             "diet_type": "veg",
                                             "is_special": True,
                                             "image_url": "uploads/menu_items/masala-dosa.jpeg"},
                                            {"name": "Idli Sambhar",
                                             "price": 149,
                                             "category": "Breakfast",
                                             "diet_type": "veg",
                                             "image_url": "uploads/menu_items/idli-sambhar.jpeg"},
                                            {"name": "Vada",
                                             "price": 129,
                                             "category": "Snacks",
                                             "diet_type": "veg",
                                             "image_url": "uploads/menu_items/vada.jpeg"},
                                            {"name": "Coconut Chutney",
                                             "price": 49,
                                             "category": "Sides",
                                             "diet_type": "veg",
                                             "image_url": "uploads/menu_items/coconut-chutney.jpeg"},
                                            {"name": "Filter Coffee",
                                             "price": 99,
                                             "category": "Beverages",
                                             "diet_type": "veg",
                                             "image_url": "uploads/menu_items/filter-coffee.jpg"},
                                            ]},
                            {"name": "Rasoi Magic",
                             "description": "Rajasthani and Gujarati traditional cuisine",
                             "cuisine_type": "Rajasthani/Gujarati",
                             "address": "123 MG Road",
                             "city": "Ahmedabad",
                             "state": "Gujarat",
                             "zip_code": "380001",
                             "phone": "+91 79 2345 6789",
                             "owner_id": owners[2].id,
                             "opening_time": time(9,
                                                  0),
                             "closing_time": time(22,
                                                  0),
                             "image_url": "uploads/restaurants/rasoi-magic.jpeg",
                             "menu_items": [{"name": "Dal Baati Churma",
                                             "price": 399,
                                             "category": "Main Course",
                                             "diet_type": "veg",
                                             "is_special": True,
                                             "image_url": "uploads/menu_items/dal-bhati.jpeg"},
                                            {"name": "Gatte Ki Sabzi",
                                             "price": 299,
                                             "category": "Main Course",
                                             "diet_type": "veg",
                                             "image_url": "uploads/menu_items/gatte.jpeg"},
                                            {"name": "Kachori",
                                             "price": 99,
                                             "category": "Snacks",
                                             "diet_type": "veg",
                                             "image_url": "uploads/menu_items/kachori.jpeg"},
                                            {"name": "Thepla",
                                             "price": 149,
                                             "category": "Snacks",
                                             "diet_type": "veg",
                                             "image_url": "uploads/menu_items/thepla.jpeg"},
                                            {"name": "Shrikhand",
                                             "price": 199,
                                             "category": "Desserts",
                                             "diet_type": "veg",
                                             "image_url": "uploads/menu_items/shrikhand.jpg"},
                                            ]},
                            {"name": "Tandoori Tales",
                             "description": "North Indian tandoori dishes and kebabs",
                             "cuisine_type": "North Indian",
                             "address": "56 Park Street",
                             "city": "Kolkata",
                             "state": "West Bengal",
                             "zip_code": "700016",
                             "phone": "+91 33 2345 6789",
                             "owner_id": owners[3].id,
                             "opening_time": time(11,
                                                  0),
                             "closing_time": time(23,
                                                  0),
                             "image_url": "uploads/restaurants/tandoor-tales.jpg",
                             "menu_items": [{"name": "Tandoori Chicken",
                                             "price": 499,
                                             "category": "Main Course",
                                             "diet_type": "non-veg",
                                             "is_special": True,
                                             "image_url": "uploads/menu_items/tandoori-chicken.jpg"},
                                            {"name": "Paneer Tikka Masala",
                                             "price": 349,
                                             "category": "Main Course",
                                             "diet_type": "veg",
                                             "image_url": "uploads/menu_items/panner-tikka-masala.jpg"},
                                            {"name": "Rogan Josh",
                                             "price": 399,
                                             "category": "Main Course",
                                             "diet_type": "non-veg",
                                             "image_url": "uploads/menu_items/rogan-josh.jpg"},
                                            {"name": "Butter Naan",
                                             "price": 99,
                                             "category": "Sides",
                                             "diet_type": "veg",
                                             "image_url": "uploads/menu_items/butter-naan.jpg"},
                                            {"name": "Kulfi Falooda",
                                             "price": 199,
                                             "category": "Desserts",
                                             "diet_type": "veg",
                                             "image_url": "uploads/menu_items/kulfi-falooda.jpg"},
                                            ]},
                            {"name": "Biryani House",
                             "description": "Delicious Hyderabadi biryanis and Mughlai dishes",
                             "cuisine_type": "Mughlai",
                             "address": "78 MG Road",
                             "city": "Hyderabad",
                             "state": "Telangana",
                             "zip_code": "500001",
                             "phone": "+91 40 2345 6789",
                             "owner_id": owners[4].id,
                             "opening_time": time(11,
                                                  0),
                             "closing_time": time(23,
                                                  0),
                             "image_url": "uploads/restaurants/biryani-house.jpg",
                             "menu_items": [{"name": "Hyderabadi Chicken Biryani",
                                             "price": 499,
                                             "category": "Main Course",
                                             "diet_type": "non-veg",
                                             "is_special": True,
                                             "image_url": "uploads/menu_items/hyderabadi-chicken-biryani.jpg"},
                                            {"name": "Mutton Biryani",
                                             "price": 599,
                                             "category": "Main Course",
                                             "diet_type": "non-veg",
                                             "image_url": "uploads/menu_items/mutton-biryani.jpg"},
                                            {"name": "Paneer Biryani",
                                             "price": 399,
                                             "category": "Main Course",
                                             "diet_type": "veg",
                                             "image_url": "uploads/menu_items/paneer-biryani.jpg"},
                                            {"name": "Mirchi Ka Salan",
                                             "price": 199,
                                             "category": "Sides",
                                             "diet_type": "veg",
                                             "image_url": "uploads/menu_items/mirchi-ka-salan.jpg"},
                                            {"name": "Double Ka Meetha",
                                             "price": 149,
                                             "category": "Desserts",
                                             "diet_type": "veg",
                                             "image_url": "uploads/menu_items/double-ka-meetha.jpg"},
                                            ]},
                            {"name": "Curry & Co.",
                             "description": "Street-style Indian fast food and chaats",
                             "cuisine_type": "Street Food",
                             "address": "101 Brigade Road",
                             "city": "Bengaluru",
                             "state": "Karnataka",
                             "zip_code": "560001",
                             "phone": "+91 80 3456 7890",
                             "owner_id": owners[5].id,
                             "opening_time": time(12,
                                                  0),
                             "closing_time": time(22,
                                                  0),
                             "image_url": "uploads/restaurants/curry-co.jpg",
                             "menu_items": [{"name": "Pani Puri",
                                             "price": 99,
                                             "category": "Snacks",
                                             "diet_type": "veg",
                                             "is_special": True,
                                             "image_url": "uploads/menu_items/pani-puri.jpg"},
                                            {"name": "Aloo Tikki",
                                             "price": 129,
                                             "category": "Snacks",
                                             "diet_type": "veg",
                                             "image_url": "uploads/menu_items/aloo-tikki.jpg"},
                                            {"name": "Pav Bhaji",
                                             "price": 199,
                                             "category": "Main Course",
                                             "diet_type": "veg",
                                             "image_url": "uploads/menu_items/pav-bhaji.jpg"},
                                            {"name": "Vada Pav",
                                             "price": 149,
                                             "category": "Snacks",
                                             "diet_type": "veg",
                                             "image_url": "uploads/menu_items/vada-pav.jpg"},
                                            {"name": "Masala Chai",
                                             "price": 49,
                                             "category": "Beverages",
                                             "diet_type": "veg",
                                             "image_url": "uploads/menu_items/masala-chai.jpg"},
                                            ]},
                            ]

        # create restaurants
        for restaurant_data in restaurants_data:
            restaurant = Restaurant(
                name=restaurant_data["name"],
                description=restaurant_data["description"],
                cuisine_type=restaurant_data["cuisine_type"],
                address=restaurant_data["address"],
                city=restaurant_data["city"],
                state=restaurant_data["state"],
                zip_code=restaurant_data["zip_code"],
                phone=restaurant_data["phone"],
                owner_id=restaurant_data["owner_id"],
                opening_time=restaurant_data["opening_time"],
                closing_time=restaurant_data["closing_time"],
                image_url=restaurant_data["image_url"],
                is_active=True,
            )
            db.session.add(restaurant)
            db.session.flush()

            # Create menu items for this restaurant
            for item_data in restaurant_data["menu_items"]:
                menu_item = MenuItem(
                    name=item_data["name"],
                    price=item_data["price"],
                    category=item_data["category"],
                    restaurant_id=restaurant.id,
                    is_available=True,
                    is_special=item_data.get("is_special", False),
                    is_deal_of_day=item_data.get("is_deal_of_day", False),
                    preparation_time=15,  # Default preparation time
                    description=f"Delicious {
                        item_data['name'].lower()} made with fresh ingredients",
                    diet_type=item_data["diet_type"],
                    image_url=item_data["image_url"]
                )
                db.session.add(menu_item)

        # Create sample orders
        # Create sample orders (prices updated to INR as per restaurants_data)
        # Revised sample orders based on current restaurants_data
        sample_orders = [
            {
                "customer_username": "mayan_bhandari",
                "restaurant_name": "Spice Route",
                "items": [
                    {"name": "Butter Chicken", "quantity": 1, "price": 499},
                    {"name": "Naan", "quantity": 2, "price": 99}
                ],
                "status": "delivered"
            },
            {
                "customer_username": "priya_mehta",
                "restaurant_name": "Curry Leaf",
                "items": [
                    {"name": "Masala Dosa", "quantity": 2, "price": 199},
                    {"name": "Filter Coffee", "quantity": 1, "price": 99}
                ],
                "status": "ready"
            },
            {
                "customer_username": "rahul_gupta",
                "restaurant_name": "Rasoi Magic",
                "items": [
                    {"name": "Dal Baati Churma", "quantity": 1, "price": 399},
                    {"name": "Kachori", "quantity": 2, "price": 99}
                ],
                "status": "preparing"
            },
            {
                "customer_username": "mayan_bhandari",
                "restaurant_name": "Tandoori Tales",
                "items": [
                    {"name": "Tandoori Chicken", "quantity": 1, "price": 499},
                    {"name": "Butter Naan", "quantity": 2, "price": 99}
                ],
                "status": "confirmed"
            },
            {
                "customer_username": "priya_mehta",
                "restaurant_name": "Biryani House",
                "items": [
                    {"name": "Hyderabadi Chicken Biryani",
                        "quantity": 1, "price": 499},
                    {"name": "Mirchi Ka Salan", "quantity": 1, "price": 199}
                ],
                "status": "pending"
            },
            {
                "customer_username": "rahul_gupta",
                "restaurant_name": "Curry & Co.",
                "items": [
                    {"name": "Pani Puri", "quantity": 1, "price": 99},
                    {"name": "Pav Bhaji", "quantity": 1, "price": 199}
                ],
                "status": "delivered"
            }
        ]

        # Seeding logic remains the same
        for order_data in sample_orders:
            # Find customer and restaurant
            customer = User.query.filter_by(
                username=order_data["customer_username"]).first()
            restaurant = Restaurant.query.filter_by(
                name=order_data["restaurant_name"]).first()

            if customer and restaurant:
                from datetime import datetime
                import random
                order_number = f"ORD{random.randint(100000, 999999)}"
                total_amount = sum(item["price"] * item["quantity"]
                                   for item in order_data["items"])

                order = Order(
                    order_number=order_number,
                    total_amount=total_amount,
                    customer_id=customer.id,
                    restaurant_id=restaurant.id,
                    status=order_data["status"]
                )
                db.session.add(order)
                db.session.flush()

                # Create order items
                for item_data in order_data["items"]:
                    menu_item = MenuItem.query.filter_by(
                        name=item_data["name"],
                        restaurant_id=restaurant.id
                    ).first()

                    if menu_item:
                        order_item = OrderItem(
                            order_id=order.id,
                            menu_item_id=menu_item.id,
                            quantity=item_data["quantity"],
                            price=item_data["price"]  # Already in INR
                        )
                        db.session.add(order_item)

        # Create sample reviews
        # Revised sample reviews based on current restaurants_data
        sample_reviews = [{"customer_username": "mayan_bhandari",
                           "restaurant_name": "Spice Route",
                           "rating": 5,
                           "comment": "The Butter Chicken was rich and creamy, naan was soft and fresh!"},
                          {"customer_username": "priya_mehta",
                           "restaurant_name": "Curry Leaf",
                           "rating": 4,
                           "comment": "Crispy Masala Dosa and authentic filter coffee. Loved it!"},
                          {"customer_username": "rahul_gupta",
                           "restaurant_name": "Rasoi Magic",
                           "rating": 5,
                           "comment": "Dal Baati Churma had authentic Rajasthani flavor. Kachori was perfect too."},
                          {"customer_username": "mayan_bhandari",
                           "restaurant_name": "Tandoori Tales",
                           "rating": 4,
                           "comment": "Juicy Tandoori Chicken and fluffy butter naan. Great combo."},
                          {"customer_username": "priya_mehta",
                           "restaurant_name": "Biryani House",
                           "rating": 5,
                           "comment": "Hyderabadi Biryani was aromatic and the Mirchi Ka Salan balanced it well."},
                          {"customer_username": "rahul_gupta",
                           "restaurant_name": "Curry & Co.",
                           "rating": 4,
                           "comment": "Pani Puri was tangy and fresh, Pav Bhaji was flavorful and filling."}]

        for review_data in sample_reviews:
            customer = User.query.filter_by(
                username=review_data["customer_username"]).first()
            restaurant = Restaurant.query.filter_by(
                name=review_data["restaurant_name"]).first()

            if customer and restaurant:
                review = Review(
                    rating=review_data["rating"],
                    comment=review_data["comment"],
                    user_id=customer.id,
                    restaurant_id=restaurant.id
                )
                db.session.add(review)

        # Create sample feedback
        # Revised sample feedback based on current restaurants_data
        sample_feedback = [{"customer_username": "mayan_bhandari",
                            "restaurant_name": "Spice Route",
                            "subject": "Delicious North Indian",
                            "message": "Loved the Butter Chicken and naan combo. Very authentic taste!"},
                           {"customer_username": "priya_mehta",
                            "restaurant_name": "Curry Leaf",
                            "subject": "Authentic South Indian",
                            "message": "Masala Dosa reminded me of home. Filter Coffee was excellent."}]

        for feedback_data in sample_feedback:
            customer = User.query.filter_by(
                username=feedback_data["customer_username"]).first()
            restaurant = Restaurant.query.filter_by(
                name=feedback_data["restaurant_name"]).first()

            if customer and restaurant:
                feedback = Feedback(
                    subject=feedback_data["subject"],
                    message=feedback_data["message"],
                    user_id=customer.id,
                    restaurant_id=restaurant.id
                )
                db.session.add(feedback)

        db.session.commit()
        print(" Seed data created successfully with 6 restaurants, sample orders, reviews, and feedback!")


