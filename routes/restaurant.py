from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import User, Restaurant, MenuItem, Order, OrderItem, Review, Feedback
from forms import MenuItemForm, OrderStatusForm
from forms import RestaurantRegistrationForm as RestaurantForm
from models import db
from datetime import datetime, date, timedelta
from forms import RestaurantProfileForm
from sqlalchemy import or_
import logging
import os

restaurant_bp = Blueprint("restaurant", __name__)
logger = logging.getLogger(__name__)


def restaurant_owner_required(f):
    """Decorator to ensure only restaurant owners can access"""
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "restaurant_owner":
            flash("Access denied. Restaurant owner login required.", "error")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return decorated_function


# Dashboard 
@restaurant_bp.route("/dashboard", methods=["GET"])
@login_required
@restaurant_owner_required
def dashboard():
    """Restaurant owner dashboard showing all restaurants, with search support"""
    try:
        q = request.args.get("q", "").strip()

        # Base query: restaurants owned by current user
        restaurants_query = current_user.restaurants

        # Apply search filter if query exists
        if q:
            restaurants_query = restaurants_query.filter(
                or_(
                    Restaurant.name.ilike(f"%{q}%"),
                    Restaurant.description.ilike(f"%{q}%")
                )
            )

        restaurants = restaurants_query.all()

        # If no restaurants at all and no search → redirect to register
        if not restaurants and not q:
            flash("Please register your restaurant first.", "info")
            return redirect(url_for("restaurant.register"))

        today = date.today()
        start_of_day = datetime.combine(today, datetime.min.time())
        end_of_day = datetime.combine(today, datetime.max.time())

        dashboard_data = []

        for restaurant in restaurants:
            try:
                today_orders = (
                    Order.query.filter(
                        Order.restaurant_id == restaurant.id,
                        Order.created_at >= start_of_day,
                        Order.created_at <= end_of_day,
                    )
                    .order_by(Order.created_at.desc())
                    .all()
                )

                total_orders = Order.query.filter_by(
                    restaurant_id=restaurant.id
                ).count()

                total_revenue = (
                    db.session.query(db.func.sum(Order.total_amount))
                    .filter_by(restaurant_id=restaurant.id)
                    .scalar()
                    or 0
                )

                dashboard_data.append(
                    {
                        "restaurant": restaurant,
                        "today_orders": today_orders,
                        "total_orders": total_orders,
                        "total_revenue": total_revenue,
                    }
                )
            except Exception as qe:
                logger.error(
                    f"Dashboard query error for restaurant {
                        restaurant.id}: {
                        str(qe)}")
                dashboard_data.append(
                    {
                        "restaurant": restaurant,
                        "today_orders": [],
                        "total_orders": 0,
                        "total_revenue": 0,
                    }
                )

        return render_template(
            "restaurant/dashboard.html",
            dashboard_data=dashboard_data
        )

    except Exception as e:
        logger.error(f"Restaurant dashboard error: {str(e)}")
        flash("Error loading dashboard.", "error")
        return redirect(url_for("index"))


# Register Restaurant
@restaurant_bp.route("/register", methods=["GET", "POST"])
@login_required
@restaurant_owner_required
def register():
    """Register a new restaurant for the logged-in owner"""
    form = RestaurantForm()
    if form.validate_on_submit():
        try:
            image_url = None
            if form.image.data:
                filename = f"restaurant_{
                    current_user.id}_{
                    datetime.utcnow().strftime('%Y%m%d%H%M%S')}.jpg"
                upload_folder = os.path.join(
                    "static", "uploads", "restaurants")
                os.makedirs(upload_folder, exist_ok=True)
                file_path = os.path.join(upload_folder, filename)
                form.image.data.save(file_path)
                # relative path only
                image_url = f"uploads/restaurants/{filename}"

            restaurant = Restaurant(
                name=form.name.data,
                description=form.description.data,
                cuisine_type=form.cuisine_type.data,
                address=form.address.data,
                phone=form.phone.data,
                email=form.email.data,
                opening_time=form.opening_time.data,
                closing_time=form.closing_time.data,
                owner_id=current_user.id,
                image_url=image_url,
            )
            db.session.add(restaurant)
            db.session.commit()

            logger.info(
                f"Restaurant {
                    restaurant.name} registered by user {
                    current_user.username}")
            flash("Restaurant registered successfully!", "success")
            return redirect(url_for("restaurant.dashboard"))

        except Exception as e:
            logger.error(f"Restaurant registration error: {str(e)}")
            flash("Error registering restaurant.", "error")

    return render_template("restaurant/register.html", form=form)


# Add Menu Item 
@restaurant_bp.route("/<int:restaurant_id>/menu/add", methods=["GET", "POST"])
@login_required
@restaurant_owner_required
def add_menu_item(restaurant_id):
    """Add menu item for a specific restaurant owned by current user"""
    restaurant = Restaurant.query.filter_by(
        id=restaurant_id, owner_id=current_user.id
    ).first_or_404()

    form = MenuItemForm()
    if form.validate_on_submit():
        try:
            image_url = None
            if form.image.data:
                filename = f"menu_{
                    restaurant.id}_{
                    datetime.utcnow().strftime('%Y%m%d%H%M%S')}.jpg"
                upload_folder = os.path.join("static", "uploads", "menu_items")
                os.makedirs(upload_folder, exist_ok=True)
                file_path = os.path.join(upload_folder, filename)
                form.image.data.save(file_path)
                # relative path only
                image_url = f"uploads/menu_items/{filename}"

            menu_item = MenuItem(
                name=form.name.data,
                description=form.description.data,
                price=form.price.data,
                category=form.category.data,
                preparation_time=form.preparation_time.data,
                is_available=form.is_available.data,
                is_special=form.is_special.data,
                is_deal_of_day=form.is_deal_of_day.data,
                diet_type=form.diet_type.data,
                restaurant_id=restaurant.id,
                image_url=image_url,
            )
            db.session.add(menu_item)
            db.session.commit()

            logger.info(
                f"Menu item '{
                    menu_item.name}' added to restaurant '{
                    restaurant.name}'")
            flash("Menu item added successfully!", "success")
            return redirect(
                url_for("restaurant.manage_menu_all",
                        restaurant_id=restaurant.id)
            )

        except Exception as e:
            logger.error(f"Add menu item error: {str(e)}")
            db.session.rollback()
            flash("Error adding menu item.", "danger")

    return render_template(
        "restaurant/add_menu_item.html", form=form, restaurant=restaurant
    )


# Edit Menu Item
@restaurant_bp.route(
    "/<int:restaurant_id>/menu/edit/<int:item_id>", methods=["GET", "POST"]
)
@login_required
@restaurant_owner_required
def edit_menu_item(restaurant_id, item_id):
    """Edit a menu item for a specific restaurant owned by current user"""
    restaurant = Restaurant.query.filter_by(
        id=restaurant_id, owner_id=current_user.id
    ).first_or_404()
    menu_item = MenuItem.query.filter_by(
        id=item_id, restaurant_id=restaurant.id
    ).first_or_404()

    form = MenuItemForm(obj=menu_item)
    if form.validate_on_submit():
        try:
            menu_item.name = form.name.data
            menu_item.description = form.description.data
            menu_item.price = form.price.data
            menu_item.category = form.category.data
            menu_item.preparation_time = form.preparation_time.data
            menu_item.is_available = form.is_available.data
            menu_item.is_special = form.is_special.data
            menu_item.is_deal_of_day = form.is_deal_of_day.data
            menu_item.diet_type = form.diet_type.data

            if form.image.data:
                filename = f"menu_{
                    restaurant.id}_{
                    datetime.utcnow().strftime('%Y%m%d%H%M%S')}.jpg"
                upload_folder = os.path.join("static", "uploads", "menu_items")
                os.makedirs(upload_folder, exist_ok=True)
                file_path = os.path.join(upload_folder, filename)
                form.image.data.save(file_path)
                menu_item.image_url = (
                    f"uploads/menu_items/{filename}"  # ✅ relative path only
                )

            db.session.commit()

            logger.info(
                f"Menu item '{
                    menu_item.name}' updated in restaurant '{
                    restaurant.name}'")
            flash("Menu item updated successfully!", "success")
            return redirect(
                url_for("restaurant.manage_menu_all",
                        restaurant_id=restaurant.id)
            )

        except Exception as e:
            logger.error(f"Edit menu item error: {str(e)}")
            db.session.rollback()
            flash("Error updating menu item.", "danger")

    return render_template(
        "restaurant/edit_menu_item.html",
        form=form,
        menu_item=menu_item,
        restaurant=restaurant,
    )


# Delete Menu Item
@restaurant_bp.route("/<int:restaurant_id>/menu/delete/<int:item_id>",
                     methods=["POST"])
@login_required
@restaurant_owner_required
def delete_menu_item(restaurant_id, item_id):
    """Delete menu item safely"""
    try:
        restaurant = Restaurant.query.get_or_404(restaurant_id)
        menu_item = MenuItem.query.get_or_404(item_id)

        # Ensure the current user is the owner
        if restaurant.owner_id != current_user.id or menu_item.restaurant_id != restaurant.id:
            flash("Unauthorized access.", "danger")
            return redirect(url_for("main.index"))

        # Check if the menu item is part of any existing order
        existing_orders = OrderItem.query.filter_by(
            menu_item_id=menu_item.id).count()
        if existing_orders > 0:
            flash(
                "Cannot delete this menu item because it is part of existing orders.",
                "warning")
            return redirect(
                url_for(
                    "restaurant.manage_menu_all",
                    restaurant_id=restaurant.id))

        # Safe to delete
        db.session.delete(menu_item)
        db.session.commit()

        logger.info(f"Menu item '{menu_item.name}' deleted successfully.")
        flash("Menu item deleted successfully!", "success")
        return redirect(
            url_for(
                "restaurant.manage_menu_all",
                restaurant_id=restaurant.id))

    except Exception as e:
        logger.exception("Error deleting menu item")  # full traceback
        flash("Error deleting menu item.", "danger")
        return redirect(
            url_for(
                "restaurant.manage_menu_all",
                restaurant_id=restaurant_id))


# Manage Orders
@restaurant_bp.route("/orders")
@login_required
@restaurant_owner_required
def manage_orders():
    """Manage orders for selected restaurant"""
    try:
        restaurant_id = request.args.get("restaurant_id", type=int)
        if restaurant_id:
            restaurant = Restaurant.query.get_or_404(restaurant_id)
        else:
            restaurants = current_user.restaurants.order_by(
                Restaurant.created_at.desc()
            ).all()
            if not restaurants:
                flash("Please register your restaurant first.", "info")
                return redirect(url_for("restaurant.register"))
            restaurant = restaurants[0]

        if restaurant.owner_id != current_user.id:
            flash("Unauthorized access.", "danger")
            return redirect(url_for("restaurant.dashboard"))

        page = request.args.get("page", 1, type=int)
        status_filter = request.args.get("status", "")

        query = Order.query.filter_by(restaurant_id=restaurant.id)
        if status_filter:
            query = query.filter_by(status=status_filter)

        orders = query.order_by(Order.created_at.desc()).paginate(
            page=page, per_page=10, error_out=False
        )

        return render_template(
            "restaurant/orders.html",
            orders=orders,
            status_filter=status_filter,
            restaurant=restaurant,
        )
    except Exception as e:
        logger.error(f"Order management error: {str(e)}")
        flash("Error loading orders.", "error")
        return redirect(url_for("restaurant.dashboard"))


# View Single Order
@restaurant_bp.route("/order/<int:order_id>")
@login_required
@restaurant_owner_required
def view_order(order_id):
    """View order details"""
    try:
        order = Order.query.get_or_404(order_id)
        restaurant = order.restaurant

        if restaurant.owner_id != current_user.id:
            flash("Unauthorized access.", "error")
            return redirect(
                url_for("restaurant.manage_orders",
                        restaurant_id=order.restaurant_id)
            )

        return render_template(
            "restaurant/order_detail.html", order=order, restaurant=restaurant
        )
    except Exception as e:
        logger.error(f"Order view error: {str(e)}")
        flash("Error loading order details.", "error")
        return redirect(
            url_for("restaurant.manage_orders",
                    restaurant_id=order.restaurant_id)
        )


@restaurant_bp.route("/order/<int:order_id>/update-status", methods=["POST"])
@login_required
@restaurant_owner_required
def update_order_status(order_id):
    """Update order status"""
    try:
        order = Order.query.get_or_404(order_id)

        if order.restaurant.owner_id != current_user.id:
            return jsonify({"success": False, "message": "Unauthorized"})

        new_status = request.json.get("status")
        if new_status not in [
            "pending",
            "confirmed",
            "preparing",
            "ready",
            "delivered",
            "cancelled",
        ]:
            return jsonify({"success": False, "message": "Invalid status"})

        order.status = new_status
        order.updated_at = datetime.utcnow()
        db.session.commit()

        logger.info(
            f"Order {order.order_number} status updated to {new_status}")
        return jsonify({"success": True, "message": "Order status updated!"})
    except Exception as e:
        logger.error(f"Update order status error: {str(e)}")
        return jsonify({"success": False,
                        "message": "Error updating order status"})


# View Reviews
@restaurant_bp.route("/reviews")
@login_required
@restaurant_owner_required
def view_reviews():
    """View restaurant reviews"""
    try:
        restaurant_id = request.args.get("restaurant_id", type=int)
        if restaurant_id:
            restaurant = Restaurant.query.get_or_404(restaurant_id)
        else:
            restaurants = current_user.restaurants.all()
            if not restaurants:
                flash("Please register your restaurant first.", "info")
                return redirect(url_for("restaurant.register"))
            restaurant = restaurants[0]

        if restaurant.owner_id != current_user.id:
            flash("Unauthorized access.", "danger")
            return redirect(url_for("restaurant.dashboard"))

        page = request.args.get("page", 1, type=int)
        reviews = (
            Review.query.filter_by(restaurant_id=restaurant.id)
            .order_by(Review.created_at.desc())
            .paginate(page=page, per_page=10, error_out=False)
        )

        avg_rating = (
            db.session.query(db.func.avg(Review.rating))
            .filter_by(restaurant_id=restaurant.id)
            .scalar()
            or 0
        )

        return render_template(
            "restaurant/reviews.html",
            reviews=reviews,
            avg_rating=round(avg_rating, 1),
            restaurant=restaurant,
        )
    except Exception as e:
        logger.error(f"Reviews view error: {str(e)}")
        flash("Error loading reviews.", "error")
        return redirect(url_for("restaurant.dashboard"))


# View Feedback
@restaurant_bp.route("/feedback")
@login_required
@restaurant_owner_required
def view_feedback():
    """View customer feedback"""
    try:
        restaurant_id = request.args.get("restaurant_id", type=int)
        if restaurant_id:
            restaurant = Restaurant.query.get_or_404(restaurant_id)
        else:
            restaurants = current_user.restaurants.all()
            if not restaurants:
                flash("Please register your restaurant first.", "info")
                return redirect(url_for("restaurant.register"))
            restaurant = restaurants[0]

        if restaurant.owner_id != current_user.id:
            flash("Unauthorized access.", "danger")
            return redirect(url_for("restaurant.dashboard"))

        page = request.args.get("page", 1, type=int)
        feedbacks = (
            Feedback.query.filter_by(restaurant_id=restaurant.id)
            .order_by(Feedback.created_at.desc())
            .paginate(page=page, per_page=10, error_out=False)
        )

        return render_template(
            "restaurant/feedback.html",
            feedbacks=feedbacks,
            restaurant=restaurant)
    except Exception as e:
        logger.error(f"Feedback view error: {str(e)}")
        flash("Error loading feedback.", "error")
        return redirect(url_for("restaurant.dashboard"))


@restaurant_bp.route("/feedback/<int:feedback_id>/respond", methods=["POST"])
@login_required
@restaurant_owner_required
def respond_to_feedback(feedback_id):
    """Respond to customer feedback"""
    try:
        feedback = Feedback.query.get_or_404(feedback_id)

        if feedback.restaurant.owner_id != current_user.id:
            return jsonify({"success": False, "message": "Unauthorized"})

        response = request.json.get("response", "")
        status = request.json.get("status", "in_progress")

        feedback.response = response
        feedback.status = status
        feedback.updated_at = datetime.utcnow()

        db.session.commit()

        logger.info(f"Response added to feedback {feedback_id}")
        return jsonify({"success": True,
                        "message": "Response added successfully!"})
    except Exception as e:
        logger.error(f"Feedback response error: {str(e)}")
        return jsonify({"success": False, "message": "Error adding response"})


# Analytics
@restaurant_bp.route("/analytics")
@login_required
@restaurant_owner_required
def analytics():
    """Restaurant analytics"""
    try:
        restaurant_id = request.args.get("restaurant_id", type=int)
        if restaurant_id:
            restaurant = Restaurant.query.get_or_404(restaurant_id)
        else:
            restaurants = current_user.restaurants.all()
            if not restaurants:
                flash("Please register your restaurant first.", "info")
                return redirect(url_for("restaurant.register"))
            restaurant = restaurants[0]

        if restaurant.owner_id != current_user.id:
            flash("Unauthorized access.", "danger")
            return redirect(url_for("restaurant.dashboard"))

        # Popular items today
        today = date.today()
        start_of_today = datetime.combine(today, datetime.min.time())
        end_of_today = datetime.combine(today, datetime.max.time())

        popular_items = (
            db.session.query(MenuItem, db.func.count(
                OrderItem.id).label("order_count"))
            .join(OrderItem)
            .join(Order)
            .filter(
                MenuItem.restaurant_id == restaurant.id,
                Order.created_at >= start_of_today,
                Order.created_at <= end_of_today,
            )
            .group_by(MenuItem.id)
            .order_by(db.func.count(OrderItem.id).desc())
            .limit(5)
            .all()
        )

        # Daily revenue last 7 days
        daily_revenue = []
        for i in range(7):
            day = date.today() - timedelta(days=i)
            start_of_day = datetime.combine(day, datetime.min.time())
            end_of_day = datetime.combine(day, datetime.max.time())

            revenue = (
                db.session.query(db.func.sum(Order.total_amount))
                .filter(
                    Order.restaurant_id == restaurant.id,
                    Order.created_at >= start_of_day,
                    Order.created_at <= end_of_day,
                )
                .scalar()
                or 0
            )
            daily_revenue.append({"date": day, "revenue": float(revenue)})

        return render_template(
            "restaurant/analytics.html",
            popular_items=popular_items,
            daily_revenue=daily_revenue,
            restaurant=restaurant,
        )

    except Exception as e:
        logger.error(f"Analytics error: {str(e)}")
        flash("Error loading analytics.", "error")
        return redirect(url_for("restaurant.dashboard"))


@restaurant_bp.route("/<int:restaurant_id>/profile", methods=["GET", "POST"])
@login_required
@restaurant_owner_required
def profile(restaurant_id):
    """Edit a specific restaurant profile owned by current user"""
    restaurant = Restaurant.query.get_or_404(restaurant_id)

    if restaurant.owner_id != current_user.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("restaurant.dashboard"))

    form = RestaurantProfileForm(obj=restaurant)

    if request.method == "POST":
        # Handle image upload
        if form.image.data:
            upload_folder = os.path.join("static", "uploads", "restaurants")
            os.makedirs(upload_folder, exist_ok=True)

            timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
            orig_filename = secure_filename(form.image.data.filename)
            ext = os.path.splitext(orig_filename)[1].lower() or ".jpg"
            filename = f"restaurant_{restaurant.id}_{timestamp}{ext}"
            file_path = os.path.join(upload_folder, filename)

            try:
                form.image.data.save(file_path)
                restaurant.image_url = f"uploads/restaurants/{filename}"
            except Exception as img_err:
                logger.error(f"Error saving restaurant image: {img_err}")
                flash(
                    "Failed to save image. Check folder permissions.",
                    "warning")
                # Stop further processing if image fails
                return redirect(request.url)

        # Update profile fields
        if form.validate():
            try:
                restaurant.name = form.name.data
                restaurant.description = form.description.data
                restaurant.cuisine_type = form.cuisine_type.data
                restaurant.address = form.address.data
                restaurant.phone = form.phone.data
                restaurant.email = form.email.data
                restaurant.city = form.city.data
                restaurant.state = form.state.data
                restaurant.zip_code = form.zip_code.data
                restaurant.opening_time = form.opening_time.data
                restaurant.closing_time = form.closing_time.data

                db.session.commit()
                # Only one success flash
                flash("Restaurant profile updated successfully!", "success")
                return redirect(url_for("restaurant.dashboard"))

            except Exception as e:
                db.session.rollback()
                logger.error(
                    f"Profile update error for restaurant {
                        restaurant.id}: {
                        str(e)}")
                flash("Error updating profile. Please try again.", "danger")
        else:
            logger.warning(
                f"Form validation failed for restaurant {restaurant.name}")
            logger.warning(f"Form errors: {form.errors}")
            flash("Some fields are invalid. Profile not fully updated.", "warning")

    return render_template(
        "restaurant/profile.html",
        form=form,
        restaurant=restaurant)


# Delete Restaurant
@restaurant_bp.route("/<int:restaurant_id>/delete", methods=["POST"])
@login_required
@restaurant_owner_required
def delete_restaurant(restaurant_id):
    """Delete a restaurant owned by the current user safely"""
    try:
        restaurant = Restaurant.query.get_or_404(restaurant_id)

        # Ensure the current user is the owner
        if restaurant.owner_id != current_user.id:
            flash("Unauthorized access.", "danger")
            return redirect(url_for("restaurant.dashboard"))

        # Check if any orders exist for this restaurant
        existing_orders = Order.query.filter_by(
            restaurant_id=restaurant.id).count()
        if existing_orders > 0:
            flash(
                "Cannot delete this restaurant because it has existing orders.",
                "warning")
            return redirect(url_for("restaurant.dashboard"))

        # Optional: delete related menu items safely
        menu_items = MenuItem.query.filter_by(
            restaurant_id=restaurant.id).all()
        for item in menu_items:
            db.session.delete(item)

        # Now delete the restaurant
        db.session.delete(restaurant)
        db.session.commit()

        flash("Restaurant deleted successfully.", "success")
        logger.info(f"Restaurant '{restaurant.name}' deleted successfully.")
        return redirect(url_for("restaurant.dashboard"))

    except Exception as e:
        logger.exception("Delete restaurant error")  # logs full traceback
        flash("Error deleting restaurant.", "danger")
        return redirect(url_for("restaurant.dashboard"))


# Customer side: View restaurant & menu
@restaurant_bp.route("/restaurant/<int:restaurant_id>")
def restaurant_detail(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    menu_items = restaurant.menu_items.all()

    today = date.today()
    start_of_day = datetime.combine(today, datetime.min.time())
    end_of_day = datetime.combine(today, datetime.max.time())

    for item in menu_items:
        # Total quantity ordered today
        total_quantity = (
            db.session.query(db.func.coalesce(
                db.func.sum(OrderItem.quantity), 0))
            .join(Order)
            .filter(
                OrderItem.menu_item_id == item.id,
                Order.restaurant_id == restaurant.id,
                Order.created_at >= start_of_day,
                Order.created_at <= end_of_day,
            )
            .scalar()
        )

        # Max quantity in a single order today
        max_single_order = (
            db.session.query(db.func.coalesce(
                db.func.max(OrderItem.quantity), 0))
            .join(Order)
            .filter(
                OrderItem.menu_item_id == item.id,
                Order.restaurant_id == restaurant.id,
                Order.created_at >= start_of_day,
                Order.created_at <= end_of_day,
            )
            .scalar()
        )

        # Mostly ordered condition
        item.mostly_ordered = (total_quantity > 10) or (max_single_order > 10)

    return render_template(
        "restaurant_detail.html",
        restaurant=restaurant,
        menu_items=menu_items)


@restaurant_bp.route("/manage_menu_all", methods=["GET"])
@login_required
def manage_menu_all():
    # Ensure only restaurant owners can access
    if current_user.role != "restaurant_owner":
        flash("Access denied.", "danger")
        return redirect(url_for("main.index"))

    today = date.today()
    start_of_day = datetime.combine(today, datetime.min.time())
    end_of_day = datetime.combine(today, datetime.max.time())

    search_query = request.args.get("q", "").strip()  # <-- get search input

    restaurants = Restaurant.query.filter_by(owner_id=current_user.id).all()
    all_restaurants_menus = []

    for restaurant in restaurants:
        menu_query = MenuItem.query.filter_by(restaurant_id=restaurant.id)

        if search_query:
            menu_query = menu_query.filter(
                MenuItem.name.ilike(f"%{search_query}%"))

        menu_items = menu_query.all()

        # Group menu items by category
        menu_by_category = {}
        for item in menu_items:
            if item.category not in menu_by_category:
                menu_by_category[item.category] = []
            menu_by_category[item.category].append(item)

            # Mostly Ordered logic 
            total_quantity = (
                db.session.query(
                    db.func.coalesce(
                        db.func.sum(
                            OrderItem.quantity),
                        0)) .join(Order) .filter(
                    OrderItem.menu_item_id == item.id,
                    Order.restaurant_id == restaurant.id,
                    Order.created_at >= start_of_day,
                    Order.created_at <= end_of_day,
                ) .scalar())

            max_single_order = (
                db.session.query(
                    db.func.coalesce(
                        db.func.max(
                            OrderItem.quantity),
                        0)) .join(Order) .filter(
                    OrderItem.menu_item_id == item.id,
                    Order.restaurant_id == restaurant.id,
                    Order.created_at >= start_of_day,
                    Order.created_at <= end_of_day,
                ) .scalar())

            item.mostly_ordered = (
                total_quantity > 10) or (
                max_single_order > 10)

        all_restaurants_menus.append({
            "restaurant": restaurant,
            "menu_by_category": menu_by_category,
        })

    return render_template(
        "restaurant/manage_menu_all.html",
        all_restaurants_menus=all_restaurants_menus,
        search_query=search_query  # optional: to show in input field
    )
