from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from models import User, Restaurant, db
from forms import LoginForm, PasswordResetForm, RestaurantRegistrationForm
from werkzeug.security import generate_password_hash
import logging
import os

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

# Login
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page for customers, restaurant owners, and admins"""
    if current_user.is_authenticated:
        if current_user.role == 'customer':
            return redirect(url_for('customer.dashboard'))
        elif current_user.role == 'restaurant_owner':
            return redirect(url_for('restaurant.dashboard'))
        elif current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(username=form.username.data).first()
            if user and check_password_hash(
                    user.password_hash, form.password.data):
                if user.is_active:
                    login_user(user, remember=True)
                    logger.info(f"User {user.username} logged in successfully")
                    flash('Login successful!', 'success')

                    if user.role == 'customer':
                        return redirect(url_for('customer.dashboard'))
                    elif user.role == 'restaurant_owner':
                        return redirect(url_for('restaurant.dashboard'))
                    elif user.role == 'admin':
                        return redirect(url_for('admin.dashboard'))
                    else:
                        return redirect(url_for('index'))
                else:
                    flash(
                        'Your account is deactivated. Please contact support.',
                        'error')
            else:
                flash('Invalid username or password.', 'error')
                logger.warning(
                    f"Failed login attempt for username: {form.username.data}")
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            flash('An error occurred during login. Please try again.', 'error')

    return render_template('auth/login.html', form=form)


# Logout
@auth_bp.route('/logout')
@login_required
def logout():
    """Logout user"""
    username = current_user.username
    logout_user()
    logger.info(f"User {username} logged out")
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))


# Password Reset
@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """Password reset functionality"""
    form = PasswordResetForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(username=form.username.data).first()
            if user:
                # Check security answer
                if form.security_answer.data.strip().lower() == (
                        user.security_answer or "").strip().lower():
                    user.password_hash = generate_password_hash(
                        form.new_password.data)
                    db.session.commit()
                    logger.info(f"Password reset for user: {user.username}")
                    flash(
                        'Password reset successful! You can now login with your new password.',
                        'success')
                    return redirect(url_for('auth.login'))
                else:
                    flash('Incorrect security answer.', 'error')
            else:
                flash('Username not found.', 'error')

        except Exception as e:
            logger.error(f"Password reset error: {str(e)}")
            flash(
                'An error occurred during password reset. Please try again.',
                'error')

    return render_template('auth/reset_password.html', form=form)


# Register Restaurant (Only for logged-in owners)
@auth_bp.route('/register-restaurant', methods=['GET', 'POST'])
@login_required
def register_restaurant():
    """Restaurant registration for logged-in restaurant owners"""
    if current_user.role != 'restaurant_owner':
        flash('Only restaurant owners can register a restaurant.', 'error')
        return redirect(url_for('index'))

    form = RestaurantRegistrationForm()

    if form.validate_on_submit():
        try:
            # Handle image upload
            image_file = form.image.data
            image_filename = None
            if image_file:
                filename = secure_filename(image_file.filename)
                upload_folder = os.path.join(
                    current_app.root_path, 'static', 'uploads', 'restaurants')
                os.makedirs(upload_folder, exist_ok=True)
                image_path = os.path.join(upload_folder, filename)
                image_file.save(image_path)
                # relative path for static
                image_filename = f"uploads/restaurants/{filename}"

            # Create restaurant linked to current owner
            restaurant = Restaurant(
                name=form.name.data,
                description=form.description.data,
                cuisine_type=form.cuisine_type.data,
                address=form.address.data,
                city=form.city.data,
                state=form.state.data,
                zip_code=form.zip_code.data,
                phone=form.phone.data,
                email=form.email.data,
                opening_time=form.opening_time.data,
                closing_time=form.closing_time.data,
                owner_id=current_user.id,
                image_url=image_filename,
                is_active=True
            )
            db.session.add(restaurant)
            db.session.commit()

            logger.info(
                f"Restaurant {
                    restaurant.name} registered by {
                    current_user.username}")
            flash('Restaurant registered successfully!', 'success')
            return redirect(url_for('restaurant.dashboard'))

        except Exception as e:
            logger.error(f"Restaurant registration error: {str(e)}")
            flash(
                'An error occurred during registration. Please try again.',
                'error')

    return render_template('auth/register_restaurant.html', form=form)


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Profile page with editable personal info and profile image"""
    if request.method == 'POST':
        try:
            # Update basic fields
            current_user.first_name = request.form.get('first_name')
            current_user.last_name = request.form.get('last_name')
            current_user.email = request.form.get('email')
            current_user.phone = request.form.get('phone')
            current_user.address = request.form.get('address')

            # Handle profile image upload
            image_file = request.files.get('profile_image')
            if image_file and image_file.filename:
                filename = secure_filename(image_file.filename)
                upload_folder = os.path.join(
                    current_app.root_path, 'static', 'uploads', 'profile_images')
                os.makedirs(upload_folder, exist_ok=True)

                image_path = os.path.join(upload_folder, filename)
                image_file.save(image_path)

                # Save relative path to DB
                current_user.profile_image = f'uploads/profile_images/{filename}'

            db.session.commit()
            flash('Profile updated successfully!', 'success')

        except Exception as e:
            db.session.rollback()
            flash('Error updating profile. Please try again.', 'error')

    return render_template('auth/profile.html', user=current_user)
