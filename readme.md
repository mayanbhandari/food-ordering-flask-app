# Food Ordering Application

## 📌 Project Overview

The **Food Ordering Application** is a Flask-based web application designed to manage restaurants, menus, orders, and users.  
It includes features such as:

- User authentication and forms
- Email notifications
- Monitoring and analytics
- Database migrations with Alembic
- Utilities, validators, and middleware
- Comprehensive test suite for app and restaurant features

---

## 📂 Project Structure

```ExitTestAssignment/
│── .env # Environment variables
│── analytics.py # Analytics-related logic
│── app.log # Application logs
│── app.py # Main Flask application
│── cache.py # Caching logic
│── comprehensive_test.py # Full project test script
│── config.py # Configuration settings
│── constants.py # Constants used across app
│── create_seed_data.py # Script to create initial seed data
│── email_service.py # Email handling service
│── er_diagram.gv # Graphviz ER diagram file
│── forms.py # Flask forms
│── graphviz.svg # Generated schema/diagram
│── middleware.py # Middleware logic
│── models.py # Database models (SQLAlchemy)
│── monitoring.py # Monitoring features
│── notifications.py # Notifications logic
│── requirements.txt # Python dependencies
│── run.py # Run server entry point
│── seed_data.py # Seed data
│── setup.py # Setup script
│── test_app.py # Unit tests for the app
│── test_restaurant_features.py # Tests for restaurant module
│── test_runner.py # Test runner script
│── utils.py # Utility functions
│── validators.py # Validation logic
│── verify_features.py # Feature verification
│
├── instance/ # Flask instance folder
├── migrations/ # Database migration files
│ ├── alembic.ini
│ ├── env.py
│ ├── script.py.mako
│ ├── versions/ # Migration versions
│
├── myvenv/ # Virtual environment (should be ignored in git)
│
└── ...
```

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone <repo-url>
cd ExitTestAssignment
```

### 2. Create and Activate Virtual Environment

```
python -m venv venv
source venv/bin/activate   # On macOS/Linux
venv\Scripts\activate      # On Windows
```

### 3. Install Dependencies

```
pip install -r requirements.txt

```

### 4. Set Environment Variables

- Create a .env file (if not already present) and configure required variables like:

```bash
- DATABASE_URL=mysql+pymysql://user_name:user_password@localhost/fooddelivery
- SECRET_KEY=dev-secret-key-change-in-production
```

- **note**:
  1. DATABASE_URL=mysql+pymysql://user_name:user_password@localhost/fooddelivery
  2. you can replace the user_name and user_password with you databse user name and password

### 5. Run Database Migrations

```
flask db upgrade
```

### 6. Seed Initial Data

```
python create_seed_data.py
```

### 7. Start the Application

```
python run.py
```

## 🧪 Running Tests

Run all tests:

```
python test_app.py
python comprehensive_test.py
python test_restaurant_features.py
python verify_features.py
```

## 📜 Notes

- The myvenv/ folder is a virtual environment and should be added to .gitignore.

- Database migrations are managed with Alembic inside the migrations/ directory.

- graphviz.svg and er_diagram.gv provide database schema visualization.
