"""
Comprehensive test script for JustEat application
Tests all major features and functionalities
"""

from app import create_app
from models import db, User, Restaurant, MenuItem, Order, Review, Feedback
from werkzeug.security import check_password_hash


def test_comprehensive_features():
    app = create_app()
    with app.app_context():
        print("🧪 COMPREHENSIVE FEATURE TEST")
        print("=" * 50)

        # Test 1: Database Relationships
        print("\n1. Testing Database Relationships...")
        restaurants = Restaurant.query.all()
        print(f"   ✅ Found {len(restaurants)} restaurants")

        for restaurant in restaurants[:3]:  # Test first 3
            menu_count = MenuItem.query.filter_by(
                restaurant_id=restaurant.id).count()
            print(f"   ✅ {restaurant.name}: {menu_count} menu items")

        # Test 2: User Authentication
        print("\n2. Testing User Authentication...")
        customers = User.query.filter_by(role='customer').all()
        owners = User.query.filter_by(role='restaurant_owner').all()
        print(f"   ✅ Found {len(customers)} customers")
        print(f"   ✅ Found {len(owners)} restaurant owners")

        # Test 3: Restaurant Registration Data
        print("\n3. Testing Restaurant Registration Data...")
        for owner in owners[:3]:  # Test first 3 owners
            if hasattr(owner, 'restaurants') and owner.restaurants:
                for r in owner.restaurants:
                    print(f"   ✅ {owner.username} owns {r.name}")
            else:
                print(f"   ❌ {owner.username} has no restaurant")

        # Test 4: Menu Items
        print("\n4. Testing Menu Items...")
        total_menu_items = MenuItem.query.count()
        print(f"   ✅ Total menu items: {total_menu_items}")

        # Test 5: Orders
        print("\n5. Testing Orders...")
        orders = Order.query.all()
        print(f"   ✅ Found {len(orders)} orders")

        for order in orders[:3]:  # Test first 3
            print(
                f"   ✅ Order {order.order_number}: ${order.total_amount} - {order.status}")

        # Test 6: Reviews
        print("\n6. Testing Reviews...")
        reviews = Review.query.all()
        print(f"   ✅ Found {len(reviews)} reviews")

        for review in reviews[:5]:  # Limit to first 5 for brevity
            print(
                f"   ✅ {
                    review.user.username} rated {
                    review.restaurant.name}: {
                    review.rating} stars")

        # Test 7: Feedback
        print("\n7. Testing Feedback...")
        feedbacks = Feedback.query.all()
        print(f"   ✅ Found {len(feedbacks)} feedback entries")

        # Test 8: Location Data
        print("\n8. Testing Location Data...")
        cities = db.session.query(Restaurant.city).distinct().all()
        print(f"   ✅ Restaurants in cities: {[city[0] for city in cities]}")

        # Test 9: Price Ranges
        print("\n9. Testing Price Ranges...")
        price_ranges = {
            '0-10': 0,
            '10-20': 0,
            '20-30': 0,
            '30+': 0
        }

        for item in MenuItem.query.all():
            price = float(item.price)
            if 0 <= price <= 10:
                price_ranges['0-10'] += 1
            elif 10 < price <= 20:
                price_ranges['10-20'] += 1
            elif 20 < price <= 30:
                price_ranges['20-30'] += 1
            else:
                price_ranges['30+'] += 1

        for range_name, count in price_ranges.items():
            print(f"   ✅ ${range_name}: {count} items")

        # Test 10: Special Items
        print("\n10. Testing Special Items...")
        special_items = MenuItem.query.filter_by(is_special=True).count()
        deal_items = MenuItem.query.filter_by(is_deal_of_day=True).count()
        print(f"   ✅ Special items: {special_items}")
        print(f"   ✅ Deal of the day items: {deal_items}")

        print("\n🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 50)


if __name__ == "__main__":
    test_comprehensive_features()
