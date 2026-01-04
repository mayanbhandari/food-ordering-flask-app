from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, IntegerField, DecimalField, BooleanField, TimeField, SubmitField, DateTimeField
from wtforms.validators import DataRequired, Email, Length, NumberRange, ValidationError, Optional
from models import User, Restaurant
from flask_wtf.file import FileField, FileAllowed


class LoginForm(FlaskForm):
    """Login form for both customers and restaurant owners"""
    username = StringField('Username', validators=[
                           DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class PasswordResetForm(FlaskForm):
    """Password reset form"""
    username = StringField('Username', validators=[DataRequired()])
    security_answer = StringField('Security Answer', validators=[
                                  DataRequired(), Length(min=2, max=120)])
    new_password = PasswordField('New Password', validators=[
                                 DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        'Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Reset Password')

    def validate_confirm_password(self, field):
        if field.data != self.new_password.data:
            raise ValidationError('Passwords must match')


class RestaurantRegistrationForm(FlaskForm):
    name = StringField('Restaurant Name', validators=[
                       DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    cuisine_type = SelectField(
        "Cuisine Type",
        choices=[
            ("North Indian", "North Indian"),
            ("South Indian", "South Indian"),
            ("Rajasthani/Gujarati", "Rajasthani/Gujarati"),
            ("Mughlai", "Mughlai"),
            ("Street Food", "Street Food"),
        ],
        validators=[DataRequired()],
    )
    address = TextAreaField('Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired(), Length(max=100)])
    state = StringField('State', validators=[DataRequired(), Length(max=50)])
    zip_code = StringField('ZIP Code', validators=[
                           DataRequired(), Length(max=10)])
    phone = StringField('Restaurant Phone', validators=[DataRequired()])
    email = StringField('Restaurant Email', validators=[Email()])
    opening_time = TimeField('Opening Time', validators=[DataRequired()])
    closing_time = TimeField('Closing Time', validators=[DataRequired()])

    # Image upload (correct field name to match model)
    image = FileField('Restaurant Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])

    submit = SubmitField('Register Restaurant')


class MenuItemForm(FlaskForm):
    """Menu item form"""
    name = StringField('Item Name', validators=[
                       DataRequired(), Length(max=100)])
    description = TextAreaField('Description')
    price = DecimalField('Price', validators=[
                         DataRequired(), NumberRange(min=0.01)])
    category = SelectField(
        "Category",
        choices=[
            ("Appetizers", "Appetizers"),
            ("Main Course", "Main Course"),
            ("Breakfast", "Breakfast"),
            ("Snacks", "Snacks"),
            ("Sides", "Sides"),
            ("Desserts", "Desserts"),
            ("Beverages", "Beverages"),
        ],
        validators=[DataRequired()],
    )
    preparation_time = IntegerField(
        'Preparation Time (minutes)', validators=[NumberRange(min=1)])
    is_available = BooleanField('Available')
    is_special = BooleanField('Today\'s Special')
    is_deal_of_day = BooleanField('Deal of the Day')
    diet_type = SelectField('Diet Type',
                            choices=[('veg', 'Veg'), ('non-veg', 'Non-Veg')],
                            validators=[DataRequired()])

    # Added image upload field
    image = FileField('Menu Item Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])

    submit = SubmitField('Add Menu Item')


class OrderStatusForm(FlaskForm):
    """Order status update form"""
    status = SelectField('Status', choices=[
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled')
    ], validators=[DataRequired()])
    submit = SubmitField('Update Status')


class ReviewForm(FlaskForm):
    """Review form"""
    rating = SelectField('Rating', choices=[
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars')
    ], validators=[DataRequired()], coerce=int)
    comment = TextAreaField('Comment')
    submit = SubmitField('Submit Review')


class FeedbackForm(FlaskForm):
    """Feedback form"""
    subject = StringField('Subject', validators=[
                          DataRequired(), Length(max=200)])
    message = TextAreaField('Message', validators=[DataRequired()])
    restaurant = SelectField('Restaurant (Optional)', coerce=int)
    submit = SubmitField('Submit Feedback')


class ProfileForm(FlaskForm):
    """User profile form"""
    first_name = StringField('First Name', validators=[
                             DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[
                            DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[Email()])
    phone = StringField('Phone')
    address = TextAreaField('Address')

    # Add profile image upload field
    profile_image = FileField('Profile Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])

    submit = SubmitField('Update Profile')


class SearchForm(FlaskForm):
    """Search form"""
    search = StringField('Search', validators=[Length(max=100)])
    cuisine_filter = SelectField(
        "Cuisine Type",
        choices=[
            ("", "All Cuisines"),
            ("North Indian", "North Indian"),
            ("South Indian", "South Indian"),
            ("Rajasthani/Gujarati", "Rajasthani/Gujarati"),
            ("Mughlai", "Mughlai"),
            ("Street Food", "Street Food"),
        ],
    )
    location_filter = SelectField(
        "Location",
        choices=[
            ("", "All Locations"),
            ("New Delhi", "New Delhi"),
            ("Bengaluru", "Bengaluru"),
            ("Ahmedabad", "Ahmedabad"),
            ("Kolkata", "Kolkata"),
            ("Hyderabad", "Hyderabad"),
        ],
    )
    price_filter = SelectField(
        "Price Range",
        choices=[
            ("", "All Prices"),
            ("0-100", "₹0 - ₹100"),
            ("100-300", "₹100 - ₹300"),
            ("300-500", "₹300 - ₹500"),
            ("500+", "₹500+"),
        ],
    )
    submit = SubmitField("Search")


class PromotionForm(FlaskForm):
    """Promotion form"""
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[DataRequired()])
    discount_percentage = DecimalField(
        'Discount Percentage', validators=[
            DataRequired(), NumberRange(
                min=0, max=100)])
    discount_amount = DecimalField('Fixed Discount Amount', validators=[
                                   Optional(), NumberRange(min=0)])
    min_order_amount = DecimalField('Minimum Order Amount', validators=[
                                    Optional(), NumberRange(min=0)])
    max_discount_amount = DecimalField('Maximum Discount Amount', validators=[
                                       Optional(), NumberRange(min=0)])
    code = StringField('Promo Code', validators=[Optional(), Length(max=50)])
    valid_from = DateTimeField('Valid From', validators=[DataRequired()])
    valid_until = DateTimeField('Valid Until', validators=[DataRequired()])
    usage_limit = IntegerField('Usage Limit', validators=[
                               Optional(), NumberRange(min=1)])
    submit = SubmitField('Create Promotion')


class RestaurantProfileForm(FlaskForm):
    name = StringField('Restaurant Name', validators=[
                       DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    cuisine_type = SelectField(
        "Cuisine Type",
        choices=[
            ("North Indian", "North Indian"),
            ("South Indian", "South Indian"),
            ("Rajasthani/Gujarati", "Rajasthani/Gujarati"),
            ("Mughlai", "Mughlai"),
            ("Street Food", "Street Food"),
        ],
        validators=[DataRequired()],
    )
    address = TextAreaField('Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired(), Length(max=100)])
    state = StringField('State', validators=[DataRequired(), Length(max=50)])
    zip_code = StringField('ZIP Code', validators=[
                           DataRequired(), Length(max=10)])
    phone = StringField('Restaurant Phone', validators=[DataRequired()])
    email = StringField('Restaurant Email', validators=[Email()])
    opening_time = TimeField('Opening Time', validators=[DataRequired()])
    closing_time = TimeField('Closing Time', validators=[DataRequired()])
    image = FileField('Restaurant Image', validators=[
                      FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')])

    submit = SubmitField('Update Restaurant')
