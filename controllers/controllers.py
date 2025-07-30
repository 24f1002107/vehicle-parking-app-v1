from flask import render_template, Blueprint, redirect, url_for, flash, request, session
from models.models import User, ParkingLot, ParkingSpot, ReserveParkingSpot
from controllers.forms import RegisterForm, LoginForm, AdminLoginForm
from database import db
from werkzeug.security import generate_password_hash, check_password_hash

controllers = Blueprint('controllers', __name__, template_folder='templates')

@controllers.route('/')
@controllers.route('/home')
def home():
    return render_template('home.html')

@controllers.route('/parkingLots')
def parking_lots():
    lots = ParkingLot.query.all()    
    return render_template('parkingLots.html', lots = lots)

@controllers.route('/parkingSpots')
def parking_spots():
    spots = ParkingSpot.query.all()
    return render_template('parkingSpots.html', spots=spots)

@controllers.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Hash the password before storing
        hashed_password = generate_password_hash(form.password1.data, method='pbkdf2:sha256')
        new_user = User(fullname=form.fullname.data,
                        email=form.email.data,
                        password=hashed_password,
                        role='user', 
                        status=0)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('controllers.login'))
    else:
        print(form.errors)

    return render_template('register.html', form=form)

@controllers.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            # Check if user is not admin (only allow regular users)
            if user.role != 'admin':
                # Store user info in session
                session['user_id'] = user.id
                session['user_email'] = user.email
                session['user_fullname'] = user.fullname
                session['user_role'] = user.role
                
                flash(f'Welcome back, {user.fullname}!', 'success')
                return redirect(url_for('controllers.home'))
            else:
                flash('Admin users should use the admin login page.', 'warning')
        else:
            flash('Invalid email or password. Please try again.', 'danger')
    
    return render_template('login.html', form=form)

@controllers.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    form = AdminLoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            # Check if user is admin
            if user.role == 'admin':
                # Store admin info in session
                session['user_id'] = user.id
                session['user_email'] = user.email
                session['user_fullname'] = user.fullname
                session['user_role'] = user.role
                
                flash(f'Welcome Admin {user.fullname}!', 'success')
                return redirect(url_for('controllers.admin_dashboard'))
            else:
                flash('This login is only for administrators.', 'warning')
        else:
            flash('Invalid admin credentials. Please try again.', 'danger')
    
    return render_template('admin_login.html', form=form)

@controllers.route('/admin/dashboard')
def admin_dashboard():
    # Check if user is logged in and is admin
    if not session.get('user_id') or session.get('user_role') != 'admin':
        flash('Access denied. Admin login required.', 'danger')
        return redirect(url_for('controllers.admin_login'))
    
    return render_template('admin_dashboard.html')

@controllers.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('controllers.home'))

