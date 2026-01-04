#!/usr/bin/env python3
"""
FoodDelivery Application Setup Script
This script helps you set up the application quickly
"""

import os
import sys
import subprocess
import mysql.connector
from mysql.connector import Error


def print_header():
    """Print application header"""
    print("=" * 60)
    print("🍔 FoodDelivery Application Setup")
    print("=" * 60)
    print("This script will help you set up the FoodDelivery application")
    print("Make sure you have MySQL installed and running")
    print("=" * 60)


def check_python_version():
    """Check if Python version is compatible"""
    print("Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True


def install_requirements():
    """Install Python requirements"""
    print("\nInstalling Python requirements...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False


def get_mysql_credentials():
    """Get MySQL credentials from user"""
    print("\nMySQL Database Setup")
    print("Please provide your MySQL credentials:")

    host = input("MySQL Host (default: localhost): ").strip() or "localhost"
    port = input("MySQL Port (default: 3306): ").strip() or "3306"
    username = input("MySQL Username (default: root): ").strip() or "root"
    password = input("MySQL Password: ").strip()

    return {
        'host': host,
        'port': int(port),
        'username': username,
        'password': password
    }


def test_mysql_connection(credentials):
    """Test MySQL connection"""
    print("\nTesting MySQL connection...")
    try:
        connection = mysql.connector.connect(
            host=credentials['host'],
            port=credentials['port'],
            user=credentials['username'],
            password=credentials['password']
        )
        if connection.is_connected():
            print("✅ MySQL connection successful")
            connection.close()
            return True
    except Error as e:
        print(f"❌ MySQL connection failed: {e}")
        return False


def create_database(credentials):
    """Create the fooddelivery database"""
    print("\nCreating fooddelivery database...")
    try:
        connection = mysql.connector.connect(
            host=credentials['host'],
            port=credentials['port'],
            user=credentials['username'],
            password=credentials['password']
        )
        cursor = connection.cursor()

        cursor.execute("CREATE DATABASE IF NOT EXISTS fooddelivery")
        print("✅ Database 'fooddelivery' created successfully")

        cursor.close()
        connection.close()
        return True
    except Error as e:
        print(f"❌ Error creating database: {e}")
        return False


def update_env(credentials):
    """Update .env file with database credentials"""
    print("\nUpdating .env configuration...")

    env_content = f"""SECRET_KEY=dev-secret-key-change-in-production
DATABASE_URL=mysql+pymysql://{credentials['username']}:{credentials['password']}@{credentials['host']}:{credentials['port']}/fooddelivery
"""

    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ .env updated successfully")
        return True
    except Exception as e:
        print(f"❌ Error updating .env: {e}")
        return False


def run_database_setup():
    """Run database setup and seeding"""
    print("\nSetting up database tables and seeding data...")
    try:
        from app import create_app
        from models import db
        from seed_data import create_seed_data

        app = create_app()
        with app.app_context():
            db.create_all()
            print("✅ Database tables created")

            print("Seeding database with sample data...")
            create_seed_data()
            print("✅ Database seeded with sample data")

        return True
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False


def print_success_message():
    """Print success message with instructions"""
    print("\n" + "=" * 60)
    print("🎉 Setup Complete!")
    print("=" * 60)
    print("Your FoodDelivery application is ready to run!")
    print("\nTo start the application:")
    print("  python run.py")
    print("\nOr:")
    print("  python app.py")
    print("\nAccess the application at: http://localhost:5000")
    print("\nSample login credentials:")
    print("  Customer: john_doe / password123")
    print("  Restaurant: mario_owner / password123")
    print("  Admin: admin_user / password123")
    print("\nFor MySQL Workbench:")
    print("  Database: fooddelivery")
    print("  Run the setup_database.sql script for reference (optional)")
    print("=" * 60)


def main():
    """Main setup function"""
    print_header()

    if not check_python_version():
        return

    if not install_requirements():
        return

    credentials = get_mysql_credentials()

    if not test_mysql_connection(credentials):
        print("\nPlease check your MySQL credentials and try again.")
        return

    if not create_database(credentials):
        return

    if not update_env(credentials):
        return

    if not run_database_setup():
        return

    print_success_message()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
    except Exception as e:
        print(f"\nUnexpected error during setup: {e}")
        print("Please check the error and try again.")
