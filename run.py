#!/usr/bin/env python3
"""
JustEat Food Delivery Application
Run script for easy startup
"""

import os
import sys
from app import app, db


def setup_database():
    """Initialize database and create tables"""
    print("Setting up database...")
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")


def seed_database():
    """Seed database with sample data"""
    print("Seeding database with sample data...")
    try:
        from seed_data import create_seed_data
        create_seed_data()
        print("Database seeded successfully!")
    except Exception as e:
        print(f"Error seeding database: {e}")


def main():
    """Main function to run the application"""
    print("=" * 50)
    print("🍕 JustEat Food Delivery Application")
    print("=" * 50)

    # Check if database needs setup
    if len(sys.argv) > 1 and sys.argv[1] == '--setup':
        setup_database()
        seed_database()
        print("\nSetup complete! You can now run the application.")
        return

    # Check if we need to seed data
    if len(sys.argv) > 1 and sys.argv[1] == '--seed':
        seed_database()
        return

    # Run the application
    print("Starting JustEat application...")
    print("Access the application at: http://localhost:5000")
    print("\nSample login credentials:")
    print("Customer: john_doe / password123")
    print("Restaurant: mario_owner / password123")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 50)

    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n\nApplication stopped by user.")
    except Exception as e:
        print(f"\nError running application: {e}")


if __name__ == '__main__':
    main()
