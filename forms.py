from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, IntegerField, FloatField, BooleanField, PasswordField, EmailField, FileField
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange

class AppointmentForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=10, max=20)])
    email = EmailField('Email', validators=[Optional(), Email()])
    service_id = SelectField('Service', coerce=int, validators=[DataRequired()])
    stylist_id = SelectField('Stylist (Optional)', coerce=int, validators=[Optional()])
    date = DateField('Date', validators=[DataRequired()])
    time = SelectField('Time', choices=[
        ('9:00', '9:00 AM'),
        ('10:00', '10:00 AM'),
        ('11:00', '11:00 AM'),
        ('12:00', '12:00 PM'),
        ('13:00', '1:00 PM'),
        ('14:00', '2:00 PM'),
        ('15:00', '3:00 PM'),
        ('16:00', '4:00 PM'),
        ('17:00', '5:00 PM'),
        ('18:00', '6:00 PM'),
    ], validators=[DataRequired()])
    notes = TextAreaField('Additional Notes', validators=[Optional()])

class ServiceForm(FlaskForm):
    name = StringField('Service Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    duration = StringField('Duration', validators=[DataRequired(), Length(max=50)])
    image_url = StringField('Image URL', validators=[Optional(), Length(max=200)])
    image_file = FileField('Upload Image', validators=[Optional()])
    category = SelectField('Category', choices=[
        ('haircut', 'Haircut'),
        ('coloring', 'Hair Coloring'),
        ('treatment', 'Hair Treatment'),
        ('styling', 'Hair Styling'),
        ('spa', 'Hair Spa'),
    ], validators=[DataRequired()])
    featured = BooleanField('Featured Service')

class StylistForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    specialization = StringField('Specialization', validators=[DataRequired(), Length(max=100)])
    experience = StringField('Experience', validators=[DataRequired(), Length(max=50)])
    image_url = StringField('Image URL', validators=[Optional(), Length(max=200)])
    image_file = FileField('Upload Image', validators=[Optional()])
    bio = TextAreaField('Bio', validators=[Optional()])

class GalleryForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    image_url = StringField('Image URL', validators=[Optional(), Length(max=200)])
    image_file = FileField('Upload Image', validators=[Optional()])
    category = SelectField('Category', choices=[
        ('haircut', 'Haircut'),
        ('coloring', 'Hair Coloring'),
        ('treatment', 'Hair Treatment'),
        ('styling', 'Hair Styling'),
        ('bridal', 'Bridal'),
    ], validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=10, max=20)])
    subject = StringField('Subject', validators=[DataRequired(), Length(max=200)])
    message = TextAreaField('Message', validators=[DataRequired()])

class AboutForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    image_url = StringField('Image URL', validators=[Optional(), Length(max=200)])
    image_file = FileField('Upload Image', validators=[Optional()])
    video_url = StringField('Video URL', validators=[Optional(), Length(max=200)])
    video_file = FileField('Upload Video', validators=[Optional()])
    use_video = BooleanField('Use Video Instead of Image')
    years_experience = IntegerField('Years of Experience', validators=[DataRequired()])
    happy_clients = IntegerField('Happy Clients', validators=[DataRequired()])
    expert_stylists = IntegerField('Expert Stylists', validators=[DataRequired()])

class TestimonialForm(FlaskForm):
    customer_name = StringField('Customer Name', validators=[DataRequired(), Length(max=100)])
    customer_image_url = StringField('Customer Image URL', validators=[Optional(), Length(max=200)])
    customer_image_file = FileField('Upload Customer Image', validators=[Optional()])
    review = TextAreaField('Review', validators=[DataRequired()])
    rating = IntegerField('Rating (1-5)', validators=[DataRequired()])

class SiteSettingsForm(FlaskForm):
    site_name = StringField('Site Name', validators=[DataRequired(), Length(max=100)])
    logo_url = StringField('Logo URL', validators=[Optional(), Length(max=200)])
    logo_file = FileField('Upload Logo', validators=[Optional()])
    background_url = StringField('Background Image URL', validators=[Optional(), Length(max=200)])
    background_file = FileField('Upload Background Image', validators=[Optional()])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    email = EmailField('Email', validators=[Optional(), Email()])
    address = TextAreaField('Address', validators=[Optional()])
    whatsapp_number = StringField('WhatsApp Number', validators=[Optional(), Length(max=20)])
    business_hours = StringField('Business Hours', validators=[Optional(), Length(max=100)])
    facebook_url = StringField('Facebook URL', validators=[Optional(), Length(max=200)])
    instagram_url = StringField('Instagram URL', validators=[Optional(), Length(max=200)])
    twitter_url = StringField('Twitter URL', validators=[Optional(), Length(max=200)])
    pinterest_url = StringField('Pinterest URL', validators=[Optional(), Length(max=200)])

class BeforeAfterForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    before_image_url = StringField('Before Image URL', validators=[Optional(), Length(max=200)])
    before_image_file = FileField('Upload Before Image', validators=[Optional()])
    after_image_url = StringField('After Image URL', validators=[Optional(), Length(max=200)])
    after_image_file = FileField('Upload After Image', validators=[Optional()])
    service_type = SelectField('Service Type', choices=[
        ('haircut', 'Haircut'),
        ('coloring', 'Hair Coloring'),
        ('treatment', 'Hair Treatment'),
        ('styling', 'Hair Styling'),
        ('spa', 'Hair Spa'),
    ], validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    featured = BooleanField('Featured Transformation')

class PromotionForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    image_url = StringField('Image URL', validators=[Optional(), Length(max=200)])
    image_file = FileField('Upload Image', validators=[Optional()])
    discount_percentage = IntegerField('Discount Percentage', validators=[Optional(), NumberRange(min=0, max=100)])
    valid_from = DateField('Valid From', validators=[Optional()])
    valid_until = DateField('Valid Until', validators=[Optional()])
    is_active = BooleanField('Active Promotion')
