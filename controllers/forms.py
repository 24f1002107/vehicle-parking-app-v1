from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
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