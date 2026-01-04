from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
import logging
import os
import pytz   # added for timezone conversion

# Configure logging
log_file = os.path.join(os.path.dirname(__file__), "app.log")

# Create handlers
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Get root logger and attach handlers
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

if not root_logger.handlers:
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

# Use module-level logger for this file
logger = logging.getLogger(__name__)
logger.info(" Logging initialized. Writing to app.log")


# Flask Application Factory

def create_app(config_name='default'):
    app = Flask(__name__)

    if config_name == 'testing':
        app.config.from_object('config.TestingConfig')
    else:
        app.config.from_object('config.Config')

    # Import db from models to avoid circular imports
    from models import db

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'

    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))

    # Custom Jinja2 filter for IST datetime
    def format_datetime_ist(value):
        if value is None:
            return ""
        ist = pytz.timezone("Asia/Kolkata")
        if value.tzinfo is None:  # assume UTC if naive
            value = pytz.utc.localize(value)
        return value.astimezone(ist).strftime("%d/%m/%Y %I:%M %p")

    app.jinja_env.filters["datetime_ist"] = format_datetime_ist

    # Import models and blueprints after db initialization
    from models import User, Restaurant, MenuItem, Order, OrderItem, Cart, Review, Feedback
    from routes.auth import auth_bp
    from routes.customer import customer_bp
    from routes.restaurant import restaurant_bp
    from routes.api import api_bp
    from routes.admin import admin_bp

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(customer_bp, url_prefix='/customer')
    app.register_blueprint(restaurant_bp, url_prefix='/restaurant')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    #  Render-safe DB init + seed
    with app.app_context():
        try:
            db.create_all()
            from seed_data import seed_data
            seeded = seed_data()
            if seeded:
                logger.info("Database seeded successfully.")
            else:
                logger.info("Database already seeded. Skipping.")
        except Exception:
            logger.error("Database initialization failed", exc_info=True)



    # Initialize advanced features
    try:
        from monitoring import init_performance_monitoring
        from cache import configure_cache
        from notifications import notification_service
        init_performance_monitoring(app)
        configure_cache(use_redis=app.config.get('USE_REDIS', False))
    except ImportError:
        logger.warning("Optional advanced features not loaded.")

    # Auto log requests/responses
    @app.before_request
    def log_request_info():
        logger.info(
            f"Request: {
                request.method} {
                request.path} " f"from {
                request.remote_addr}, user={
                    getattr(
                        current_user,
                        'id',
                        'anonymous')}")

    @app.after_request
    def log_response_info(response):
        logger.info(
            f"Response: {response.status} for {request.method} {request.path}"
        )
        return response

    # Routes
    @app.route('/')
    def index():
        """Home page with featured restaurants"""
        logger.info("Accessed Home Page")
        restaurants = Restaurant.query.limit(6).all()
        return render_template('index.html', restaurants=restaurants)

    @app.route('/restaurants')
    def restaurants():
        """Browse all restaurants (public view)"""
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '')
        cuisine_filter = request.args.get('cuisine_filter', '')
        location_filter = request.args.get('location_filter', '')
        location_search = request.args.get('location_search', '')
        price_filter = request.args.get('price_filter', '')

        logger.info(
            f"Restaurant search requested: search='{search}', "
            f"cuisine='{cuisine_filter}', location='{location_filter}', "
            f"location_search='{location_search}', price='{price_filter}'"
        )

        query = Restaurant.query.filter_by(is_active=True)

        if search:
            query = query.filter(Restaurant.name.contains(search))
        if cuisine_filter:
            query = query.filter(Restaurant.cuisine_type == cuisine_filter)
        if location_filter:
            query = query.filter(Restaurant.city == location_filter)
        if location_search:
            query = query.filter(Restaurant.city.contains(location_search))

        restaurants = query.paginate(page=page, per_page=9, error_out=False)

        # Price filter logic
        if price_filter:
            filtered_restaurants = []
            for restaurant in restaurants.items:
                has_items_in_range = any(
                    (price_filter == "0-200" and 0 <= float(item.price) <= 200) or
                    (price_filter == "201-500" and 201 <= float(item.price) <= 500) or
                    (price_filter == "501-1000" and 501 <= float(item.price) <= 1000) or
                    (price_filter == "1001-1500" and 1001 <= float(item.price) <= 1500) or
                    (price_filter == "1501+" and float(item.price) >= 1501)
                    for item in restaurant.menu_items
                )
                if has_items_in_range:
                    filtered_restaurants.append(restaurant)

            restaurants.items = filtered_restaurants
            restaurants.total = len(filtered_restaurants)

        return render_template(
            'restaurants.html',
            restaurants=restaurants,
            search=search,
            cuisine_filter=cuisine_filter,
            location_filter=location_filter,
            location_search=location_search,
            price_filter=price_filter
        )

    @app.errorhandler(404)
    def not_found_error(error):
        logger.warning(f"404 Not Found: {request.path}")
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error("500 Internal Server Error", exc_info=True)
        db.session.rollback()
        return render_template('errors/500.html'), 500

    return app

# App Entry Point
app = create_app()

if __name__ == "__main__":
    logger.info("Starting Flask Application...")
    app.run(debug=True)

