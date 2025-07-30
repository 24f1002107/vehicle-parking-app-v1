from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, NumberRange
from models.models import User

class RegisterForm(FlaskForm):
    fullname = StringField(label='Full Name:', validators=[DataRequired()])
    email = StringField(label='Email Address:', validators=[DataRequired(), Email()])
    password1 = PasswordField(label='Password:', validators=[DataRequired()])
    password2 = PasswordField(label='Confirm Password:', validators=[DataRequired(), EqualTo('password1', message='Passwords must match!')])
    submit = SubmitField(label='Create Account')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email is already registered. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField(label='Email Address:', validators=[DataRequired(), Email()])
    password = PasswordField(label='Password:', validators=[DataRequired()])
    submit = SubmitField(label='Sign In')

class AdminLoginForm(FlaskForm):
    email = StringField(label='Admin Email:', validators=[DataRequired(), Email()])
    password = PasswordField(label='Admin Password:', validators=[DataRequired()])
    submit = SubmitField(label='Admin Sign In')

class ParkingLotForm(FlaskForm):
    prime_location_name = StringField(label='Prime Location Name:', validators=[DataRequired()])
    address = TextAreaField(label='Address:', validators=[DataRequired()])
    pincode = IntegerField(label='Pin Code:', validators=[DataRequired(), NumberRange(min=100000, max=999999, message='Pin code must be 6 digits')])
    price = IntegerField(label='Price (per hour):', validators=[DataRequired(), NumberRange(min=1, message='Price must be greater than 0')])
    maxSpots = IntegerField(label='Maximum Number of Spots:', validators=[DataRequired(), NumberRange(min=1, max=100, message='Number of spots must be between 1 and 100')])
    submit = SubmitField(label='Add Parking Lot')