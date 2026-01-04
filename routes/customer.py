from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import (
    User,
    Restaurant,
    MenuItem,
    Order,
    OrderItem,
    Cart,
    Review,
    Feedback,
    UserPreference,
)
from forms import ReviewForm, FeedbackForm, ProfileForm, SearchForm
from models import db
from datetime import datetime, date
from sqlalchemy import func
from flask import current_app
from werkzeug.utils import secure_filename
from sqlalchemy import or_
import logging
import random
import os

customer_bp = Blueprint("customer", __name__)
logger = logging.getLogger(__name__)


def customer_required(f):
    """Decorator to ensure only customers can access"""
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "customer":
            flash("Access denied. Customer login required.", "error")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return decorated_function


@customer_bp.route("/dashboard")
@login_required
def dashboard():
    # Recent Orders
    recent_orders = (
        Order.query.filter_by(customer_id=current_user.id)
        .order_by(Order.created_at.desc())
        .limit(5)
        .all()
    )

    # Favorite Restaurants from Preferences (using UserPreference)
    favorite_restaurant_ids = [
        int(pref.preference_value)
        for pref in UserPreference.query.filter_by(
            user_id=current_user.id, preference_type="restaurant"
        ).all()
    ]
    pref_restaurants = (
        Restaurant.query.filter(Restaurant.id.in_(
            favorite_restaurant_ids)).all()
        if favorite_restaurant_ids
        else []
    )

    # Favorite Restaurants from Order History (fallback)
    order_restaurants = (
        db.session.query(Restaurant)
        .join(Order)
        .filter(Order.customer_id == current_user.id)
        .group_by(Restaurant.id)
        .order_by(db.func.count(Order.id).desc())
        .limit(3)
        .all()
    )

    # Merge (preferences + order history), deduplicate by ID
    restaurant_map = {r.id: r for r in (pref_restaurants + order_restaurants)}
    favorite_restaurants = list(restaurant_map.values())

    return render_template(
        "customer/dashboard.html",
        recent_orders=recent_orders,
        favorite_restaurants=favorite_restaurants,
    )


@customer_bp.route("/restaurants")
@login_required
@customer_required
def browse_restaurants():
    """Browse restaurants with search, filters, price, and images"""
    page = request.args.get("page", 1, type=int)
    per_page = 9
    search = request.args.get("search", "")
    cuisine_filter = request.args.get("cuisine_filter", "")
    location_filter = request.args.get("location_filter", "")
    location_search = request.args.get("location_search", "")
    price_filter = request.args.get("price_filter", "")

    query = Restaurant.query.filter_by(is_active=True)

    if search:
        query = query.filter(or_(
            Restaurant.name.ilike(f"%{search}%"),
            Restaurant.description.ilike(f"%{search}%")
        ))

    if cuisine_filter:
        query = query.filter(Restaurant.cuisine_type == cuisine_filter)

    if location_filter:
        query = query.filter(Restaurant.city == location_filter)

    if location_search:
        query = query.filter(Restaurant.city.ilike(f"%{location_search}%"))

    pagination = query.order_by(Restaurant.name.asc()).paginate(
        page=page, per_page=per_page, error_out=False)
    restaurants = pagination.items

    # Price filter
    if price_filter:
        filtered_restaurants = []
        for restaurant in restaurants:
            if any(
                (price_filter == "0-200" and 0 <= float(item.price) <= 200) or
                (price_filter == "201-500" and 201 <= float(item.price) <= 500) or
                (price_filter == "501-1000" and 501 <= float(item.price) <= 1000) or
                (price_filter == "1001-1500" and 1001 <= float(item.price) <= 1500) or
                (price_filter == "1501+" and float(item.price) >= 1501)
                for item in restaurant.menu_items
            ):
                filtered_restaurants.append(restaurant)
        restaurants = filtered_restaurants
        pagination.items = restaurants
        pagination.total = len(restaurants)

    # Debug: print restaurant names and image URLs
    for r in restaurants:
        print(f"Restaurant: {r.name}, Image URL: {r.image_url}")
        for item in r.menu_items:
            print(f"  Menu Item: {item.name}, Image URL: {item.image_url}")

    return render_template(
        "customer/restaurants.html",
        restaurants=pagination,
        search=search,
        cuisine_filter=cuisine_filter,
        location_filter=location_filter,
        location_search=location_search,
        price_filter=price_filter,
    )


@customer_bp.route("/restaurant/<int:restaurant_id>")
@login_required
@customer_required
def view_restaurant(restaurant_id):
    """View restaurant details and menu with filters and 'Mostly Ordered' tagging"""
    try:
        restaurant = Restaurant.query.get_or_404(restaurant_id)

        # Get filters from query params
        diet_filter = request.args.get("diet_filter", "all")
        price_filter = request.args.get("price_filter", "")

        # Base query for menu items
        query = MenuItem.query.filter_by(
            restaurant_id=restaurant_id, is_available=True)

        # Apply diet filter
        if diet_filter in ["veg", "non-veg"]:
            query = query.filter_by(diet_type=diet_filter)

        # Apply price filter
        if price_filter:
            if "-" in price_filter:
                try:
                    min_price, max_price = map(int, price_filter.split("-"))
                    query = query.filter(
                        MenuItem.price >= min_price,
                        MenuItem.price <= max_price)
                except ValueError:
                    logger.warning(
                        f"Invalid price filter format: {price_filter}")
            elif "+" in price_filter:
                try:
                    min_price = int(price_filter.replace("+", ""))
                    query = query.filter(MenuItem.price >= min_price)
                except ValueError:
                    logger.warning(
                        f"Invalid price filter format: {price_filter}")

        # Get menu items
        menu_items = query.all()

        # Mark "Mostly Ordered" dynamically
        today = date.today()
        for item in menu_items:
            # total quantity ordered today across all orders
            total_quantity = (
                db.session.query(func.coalesce(
                    func.sum(OrderItem.quantity), 0))
                .join(Order, Order.id == OrderItem.order_id)
                .filter(OrderItem.menu_item_id == item.id)
                .filter(func.date(Order.created_at) == today)
                .scalar()
            )

            # check if any single order had quantity > 10
            single_large_order = (
                db.session.query(OrderItem.id)
                .join(Order, Order.id == OrderItem.order_id)
                .filter(OrderItem.menu_item_id == item.id)
                .filter(func.date(Order.created_at) == today)
                .filter(OrderItem.quantity > 10)
                .first()
            )

            item.mostly_ordered = (total_quantity > 10) or (
                single_large_order is not None
            )

        # Group menu items by category
        menu_by_category = {}
        for item in menu_items:
            menu_by_category.setdefault(item.category, []).append(item)

        no_items = len(menu_items) == 0

        # Recent reviews
        reviews = (
            Review.query.filter_by(restaurant_id=restaurant_id)
            .order_by(Review.created_at.desc())
            .limit(5)
            .all()
        )

        # Recent feedbacks
        feedbacks = (
            Feedback.query.filter_by(restaurant_id=restaurant_id)
            .order_by(Feedback.created_at.desc())
            .limit(5)
            .all()
        )

        # Average rating
        avg_rating = (
            db.session.query(func.avg(Review.rating))
            .filter_by(restaurant_id=restaurant_id)
            .scalar()
            or 0
        )

        return render_template(
            "customer/restaurant_detail.html",
            restaurant=restaurant,
            menu_by_category=menu_by_category,
            reviews=reviews,
            feedbacks=feedbacks,
            avg_rating=round(avg_rating, 1),
            diet_filter=diet_filter,
            price_filter=price_filter,
            no_items=no_items,
        )
    except Exception as e:
        logger.error(f"Restaurant view error: {str(e)}")
        flash("Error loading restaurant details.", "error")
        return redirect(url_for("customer.browse_restaurants"))


@customer_bp.route("/restaurant/<int:restaurant_id>/feedbacks")
@login_required
@customer_required
def view_feedbacks(restaurant_id):
    """Display feedbacks and owner responses for a restaurant"""
    restaurant = Restaurant.query.get_or_404(restaurant_id)

    feedbacks = (
        Feedback.query.filter_by(restaurant_id=restaurant_id)
        .order_by(Feedback.created_at.desc())
        .all()
    )

    return render_template(
        "customer/restaurant_feedback.html",
        restaurant=restaurant,
        feedbacks=feedbacks)


@customer_bp.route("/add-to-cart", methods=["POST"])
@login_required
@customer_required
def add_to_cart():
    """Add item to cart"""
    try:
        menu_item_id = request.json.get("menu_item_id")
        quantity = request.json.get("quantity", 1)
        logger.info(
            f"Add to cart called: user_id={
                current_user.id}, menu_item_id={menu_item_id}, quantity={quantity}")
        menu_item = MenuItem.query.get_or_404(menu_item_id)

        # Check if item already in cart
        existing_cart_item = Cart.query.filter_by(
            user_id=current_user.id, menu_item_id=menu_item_id
        ).first()

        if existing_cart_item:
            existing_cart_item.quantity += quantity
        else:
            cart_item = Cart(
                user_id=current_user.id,
                menu_item_id=menu_item_id,
                quantity=quantity)
            db.session.add(cart_item)

        db.session.commit()
        # Log all cart items for debugging
        all_cart_items = Cart.query.all()
        logger.info(f"All cart items in DB: {[{'user': item.user_id,
                                               'menu_item': item.menu_item_id,
                                               'qty': item.quantity} for item in all_cart_items]}")

        logger.info(
            f"Item {
                menu_item.name} added to cart for user {
                current_user.username}")

        return jsonify({"success": True, "message": "Item added to cart!"})
    except Exception as e:
        logger.error(f"Add to cart error: {str(e)}")
        return jsonify({"success": False,
                        "message": "Error adding item to cart"})


@customer_bp.route("/cart")
@login_required
@customer_required
def view_cart():
    """View shopping cart"""
    try:
        db.session.expire_all()
        # Force reload from DB

        cart_items = Cart.query.filter_by(user_id=current_user.id).all()
        total = sum(item.menu_item.price *
                    item.quantity for item in cart_items)

        return render_template(
            "customer/cart.html",
            cart_items=cart_items,
            total=total)
    except Exception as e:
        logger.error(f"Cart view error: {str(e)}")
        flash("Error loading cart.", "error")
        return redirect(url_for("customer.dashboard"))


@customer_bp.route("/update-cart", methods=["POST"])
@login_required
@customer_required
def update_cart():
    """Update cart item quantity"""
    try:
        cart_item_id = request.json.get("cart_item_id")
        quantity = request.json.get("quantity", 1)

        cart_item = Cart.query.get_or_404(cart_item_id)

        if cart_item.user_id != current_user.id:
            return jsonify({"success": False, "message": "Unauthorized"})

        if quantity <= 0:
            db.session.delete(cart_item)
        else:
            cart_item.quantity = quantity

        db.session.commit()

        return jsonify({"success": True, "message": "Cart updated!"})
    except Exception as e:
        logger.error(f"Update cart error: {str(e)}")
        return jsonify({"success": False, "message": "Error updating cart"})


@customer_bp.route("/remove-from-cart/<int:cart_item_id>")
@login_required
@customer_required
def remove_from_cart(cart_item_id):
    """Remove item from cart"""
    try:
        cart_item = Cart.query.get_or_404(cart_item_id)

        if cart_item.user_id != current_user.id:
            flash("Unauthorized access.", "error")
            return redirect(url_for("customer.view_cart"))

        db.session.delete(cart_item)
        db.session.commit()

        flash("Item removed from cart.", "success")
        return redirect(url_for("customer.view_cart"))
    except Exception as e:
        logger.error(f"Remove from cart error: {str(e)}")
        flash("Error removing item from cart.", "error")
        return redirect(url_for("customer.view_cart"))


@customer_bp.route("/place-order", methods=["POST"])
@login_required
@customer_required
def place_order():
    """Place order from cart (AJAX compatible)"""
    try:
        # Reload fresh cart items
        db.session.expire_all()
        cart_items = Cart.query.filter_by(user_id=current_user.id).all()
        logger.info(
            f"Cart items for current user (ID {
                current_user.id}): {
                [
                    str(item) for item in cart_items]}")

        if not cart_items:
            return jsonify(
                {"success": False, "message": "Your cart is empty."})

        # Group items by restaurant
        restaurants = {}
        for item in cart_items:
            rid = item.menu_item.restaurant_id
            restaurants.setdefault(rid, []).append(item)

        # Create orders for each restaurant
        for restaurant_id, items in restaurants.items():
            order_number = f"ORD{
                datetime.now().strftime('%Y%m%d%H%M%S%f')}{
                current_user.id}{
                random.randint(
                    100,
                    999)}"
            total = sum(item.menu_item.price * item.quantity for item in items)

            order = Order(
                order_number=order_number,
                total_amount=total,
                customer_id=current_user.id,
                restaurant_id=restaurant_id,
            )
            db.session.add(order)
            db.session.flush()  # get order.id immediately

            # Add items to order
            for item in items:
                order_item = OrderItem(
                    order_id=order.id,
                    menu_item_id=item.menu_item_id,
                    quantity=item.quantity,
                    price=item.menu_item.price,
                )
                db.session.add(order_item)

        # Clear all items from cart in one query
        Cart.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()

        logger.info(f" Order placed by user {current_user.username}")
        return jsonify({"success": True,
                        "message": "Order placed successfully!"})

    except Exception as e:
        db.session.rollback()
        logger.error(f"Place order error: {str(e)}")
        return jsonify({"success": False,
                        "message": "Error placing order. Please try again."})


@customer_bp.route("/orders")
@login_required
@customer_required
def order_history():
    """View order history"""
    try:
        page = request.args.get("page", 1, type=int)
        search = request.args.get("search", "")

        query = Order.query.filter_by(customer_id=current_user.id)

        if search:
            query = query.filter(Order.order_number.contains(search))

        orders = query.order_by(Order.created_at.desc()).paginate(
            page=page, per_page=10, error_out=False
        )

        return render_template(
            "customer/orders.html",
            orders=orders,
            search=search)
    except Exception as e:
        logger.error(f"Order history error: {str(e)}")
        flash("Error loading order history.", "error")
        return redirect(url_for("customer.dashboard"))


@customer_bp.route("/order/<int:order_id>")
@login_required
@customer_required
def view_order(order_id):
    """View order details"""
    try:
        order = Order.query.get_or_404(order_id)

        if order.customer_id != current_user.id:
            flash("Unauthorized access.", "error")
            return redirect(url_for("customer.order_history"))

        return render_template("customer/order_detail.html", order=order)
    except Exception as e:
        logger.error(f"Order view error: {str(e)}")
        flash("Error loading order details.", "error")
        return redirect(url_for("customer.order_history"))


@customer_bp.route("/profile", methods=["GET", "POST"])
@login_required
@customer_required
def profile():
    """View and update customer profile with profile photo support"""
    form = ProfileForm(obj=current_user)

    if form.validate_on_submit():
        try:
            # Update text fields
            current_user.first_name = form.first_name.data
            current_user.last_name = form.last_name.data
            current_user.email = form.email.data
            current_user.phone = form.phone.data
            current_user.address = form.address.data

            # Handle profile photo upload
            if form.profile_image.data:
                file = form.profile_image.data
                filename = secure_filename(file.filename)

                # Save file in static/uploads/profile_images
                upload_folder = os.path.join(
                    current_app.root_path, "static", "uploads", "profile_images")
                os.makedirs(upload_folder, exist_ok=True)

                # Add timestamp + user id for uniqueness
                timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
                filename = f"{current_user.id}_{timestamp}_{filename}"

                filepath = os.path.join(upload_folder, filename)
                file.save(filepath)

                # Store relative path from static/
                current_user.profile_image = f"uploads/profile_images/{filename}"

            db.session.commit()
            logger.info(f"Profile updated for user {current_user.username}")
            flash("Profile updated successfully!", "success")
            return redirect(url_for("customer.profile"))

        except Exception as e:
            db.session.rollback()
            logger.error(f"Profile update error: {str(e)}")
            flash("Error updating profile.", "error")

    # Build correct profile image URL
    profile_image_url = (
        url_for("static", filename=current_user.profile_image)
        if current_user.profile_image
        else url_for("static", filename="images/default_profile.png")
    )

    return render_template(
        "customer/profile.html", form=form, profile_image_url=profile_image_url
    )


@customer_bp.route("/review/<int:restaurant_id>", methods=["GET", "POST"])
@login_required
@customer_required
def add_review(restaurant_id):
    """Add review for restaurant"""
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    form = ReviewForm()

    if form.validate_on_submit():
        try:
            review = Review(
                rating=form.rating.data,
                comment=form.comment.data,
                user_id=current_user.id,
                restaurant_id=restaurant_id,
            )
            db.session.add(review)
            db.session.commit()

            logger.info(
                f"Review added for restaurant {
                    restaurant.name} by user {
                    current_user.username}")
            flash("Review submitted successfully!", "success")
            return redirect(
                url_for("customer.view_restaurant",
                        restaurant_id=restaurant_id)
            )
        except Exception as e:
            logger.error(f"Review submission error: {str(e)}")
            flash("Error submitting review.", "error")

    return render_template(
        "customer/add_review.html",
        form=form,
        restaurant=restaurant)


@customer_bp.route("/menu-item/<int:menu_item_id>/review",
                   methods=["GET", "POST"])
@login_required
@customer_required
def add_menu_item_review(menu_item_id):
    """Add review for a menu item"""
    menu_item = MenuItem.query.get_or_404(menu_item_id)
    form = ReviewForm()

    if form.validate_on_submit():
        try:
            review = Review(
                rating=form.rating.data,
                comment=form.comment.data,
                user_id=current_user.id,
                menu_item_id=menu_item_id,
                restaurant_id=menu_item.restaurant_id,  # keep for aggregation if needed
            )
            db.session.add(review)
            db.session.commit()

            flash("Review submitted successfully!", "success")
            return redirect(
                url_for(
                    "customer.view_restaurant",
                    restaurant_id=menu_item.restaurant_id))
        except Exception as e:
            logger.error(f"Menu item review error: {str(e)}")
            flash("Error submitting review.", "error")

    return render_template(
        "customer/add_menu_item_review.html", form=form, menu_item=menu_item
    )


@customer_bp.route("/feedback", methods=["GET", "POST"])
@login_required
@customer_required
def feedback():
    """Submit feedback"""
    form = FeedbackForm()

    # Populate restaurant choices
    restaurants = Restaurant.query.filter_by(is_active=True).all()
    form.restaurant.choices = [(0, "General Feedback")] + [
        (r.id, r.name) for r in restaurants
    ]

    if form.validate_on_submit():
        try:
            feedback = Feedback(
                subject=form.subject.data,
                message=form.message.data,
                user_id=current_user.id,
                restaurant_id=form.restaurant.data if form.restaurant.data else None,
            )
            db.session.add(feedback)
            db.session.commit()

            logger.info(f"Feedback submitted by user {current_user.username}")
            flash("Feedback submitted successfully!", "success")
            return redirect(url_for("customer.feedback"))  # refresh page
        except Exception as e:
            logger.error(f"Feedback submission error: {str(e)}")
            flash("Error submitting feedback.", "error")

    # Fetch previous feedbacks from this user
    feedbacks = (
        Feedback.query.filter_by(user_id=current_user.id)
        .order_by(Feedback.created_at.desc())
        .all()
    )

    return render_template(
        "customer/feedback.html",
        form=form,
        feedbacks=feedbacks)


@customer_bp.route("/recommendations")
@login_required
@customer_required
def recommendations():
    """Smart recommendations based on user preferences and history"""
    try:
        # Get saved user preferences
        preferences = UserPreference.query.filter_by(
            user_id=current_user.id).all()
        saved_cuisines = [
            p.preference_value for p in preferences if p.preference_type == "cuisine"]
        dietary_restrictions = [
            p.preference_value for p in preferences if p.preference_type == "dietary"]

        # Get user's order history cuisines
        user_orders = Order.query.filter_by(customer_id=current_user.id).all()
        history_cuisines = set()
        for order in user_orders:
            for order_item in order.order_items:
                history_cuisines.add(
                    order_item.menu_item.restaurant.cuisine_type)

        # Merge saved cuisines + history cuisines
        favorite_cuisines = list(set(saved_cuisines) | history_cuisines)

        # Get recommended restaurants
        recommended_restaurants = []
        if favorite_cuisines:
            for cuisine in favorite_cuisines:
                restaurants = (
                    Restaurant.query.filter_by(
                        cuisine_type=cuisine, is_active=True)
                    .limit(3)
                    .all()
                )
                recommended_restaurants.extend(restaurants)

        # Fallback if no prefs/history
        if not recommended_restaurants:
            recommended_restaurants = (
                Restaurant.query.filter_by(is_active=True).limit(6).all()
            )

        # Popular + offers
        popular_restaurants = Restaurant.query.filter_by(
            is_active=True).limit(6).all()
        special_items = (
            MenuItem.query.filter_by(
                is_special=True, is_available=True).limit(6).all()
        )
        deal_items = (
            MenuItem.query.filter_by(is_deal_of_day=True, is_available=True)
            .limit(6)
            .all()
        )

        return render_template(
            "customer/recommendations.html",
            recommended_restaurants=recommended_restaurants,
            popular_restaurants=popular_restaurants,
            special_items=special_items,
            deal_items=deal_items,
            favorite_cuisines=favorite_cuisines,
            dietary_restrictions=dietary_restrictions,  
        )
    except Exception as e:
        logger.error(f"Recommendations error: {str(e)}")
        flash("Error loading recommendations.", "error")
        return redirect(url_for("customer.dashboard"))


@customer_bp.route("/preferences", methods=["GET", "POST"])
@login_required
@customer_required
def preferences():
    """Manage user preferences"""
    try:
        if request.method == "POST":
            # Clear existing preferences
            UserPreference.query.filter_by(user_id=current_user.id).delete()

            # Add new preferences
            cuisine_preferences = request.form.getlist("cuisine_preferences")
            dietary_restrictions = request.form.getlist("dietary_restrictions")
            favorite_restaurants = request.form.getlist("favorite_restaurants")

            # Save cuisines
            for cuisine in cuisine_preferences:
                preference = UserPreference(
                    user_id=current_user.id,
                    preference_type="cuisine",
                    preference_value=cuisine,
                )
                db.session.add(preference)

            # Save dietary restrictions
            for dietary in dietary_restrictions:
                preference = UserPreference(
                    user_id=current_user.id,
                    preference_type="dietary",
                    preference_value=dietary,
                )
                db.session.add(preference)

            # Save favorite restaurants
            for restaurant_id in favorite_restaurants:
                preference = UserPreference(
                    user_id=current_user.id,
                    preference_type="restaurant",
                    preference_value=str(
                        restaurant_id
                    ),  # store restaurant.id as string
                )
                db.session.add(preference)

            db.session.commit()
            flash("Preferences updated successfully!", "success")
            return redirect(url_for("customer.preferences"))

        # Get current preferences
        current_preferences = UserPreference.query.filter_by(
            user_id=current_user.id
        ).all()

        cuisine_prefs = [
            p.preference_value
            for p in current_preferences
            if p.preference_type == "cuisine"
        ]
        dietary_prefs = [
            p.preference_value
            for p in current_preferences
            if p.preference_type == "dietary"
        ]
        restaurant_prefs = [
            p.preference_value
            for p in current_preferences
            if p.preference_type == "restaurant"
        ]

        # Get available options
        cuisine_types = [
            "North Indian",
            "South Indian",
            "Rajasthani/Gujarati",
            "Mughlai",
            "Street Food"
        ]

        dietary_options = [
            "veg",
            "non-veg"
        ]

        restaurants = Restaurant.query.filter_by(is_active=True).all()

        return render_template(
            "customer/preferences.html",
            cuisine_prefs=cuisine_prefs,
            dietary_prefs=dietary_prefs,
            restaurant_prefs=restaurant_prefs,
            cuisine_types=cuisine_types,
            dietary_options=dietary_options,
            restaurants=restaurants,  # send restaurants to template
        )
    except Exception as e:
        logger.error(f"Preferences error: {str(e)}")
        flash("Error managing preferences.", "error")
        return redirect(url_for("customer.dashboard"))


@customer_bp.route("/debug-cart")
@login_required
@customer_required
def debug_cart():
    try:
        db.session.expire_all()  # Reload all objects
        items = Cart.query.filter_by(user_id=current_user.id).all()

        return jsonify(
            [
                {
                    "menu_item_id": item.menu_item_id,
                    "menu_item_name": item.menu_item.name,
                    "quantity": item.quantity,
                    "price": float(item.menu_item.price),
                }
                for item in items
            ]
        )
    except Exception as e:
        return jsonify({"error": str(e)})
