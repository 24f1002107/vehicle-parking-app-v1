from flask import render_template, Blueprint, redirect, url_for, flash, request, session
from models.models import User, ParkingLot, ParkingSpot, ReserveParkingSpot
from controllers.forms import RegisterForm, LoginForm, AdminLoginForm, ParkingLotForm
from database import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

controllers = Blueprint('controllers', __name__, template_folder='templates')

@controllers.route('/')
@controllers.route('/home')
def home():
    return render_template('home.html')

@controllers.route('/parkinglots')
def parking_lots():
    # Check if user is logged in
    if not session.get('user_id'):
        flash('Please login to view parking lots.', 'warning')
        return redirect(url_for('controllers.login'))
    
    lots = ParkingLot.query.all()    
    return render_template('parking_lots.html', lots = lots)

@controllers.route('/parkingspots')
def parking_spots():
    # Check if user is logged in
    if not session.get('user_id'):
        flash('Please login to view parking spots.', 'warning')
        return redirect(url_for('controllers.login'))
    
    spots = ParkingSpot.query.all()
    return render_template('parking_spots.html', spots=spots)

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
                return redirect(url_for('controllers.user_dashboard'))
            else:
                flash('Admin users should use the admin login page.', 'warning')
        else:
            flash('Invalid email or password. Please try again.', 'danger')
    
    return render_template('login.html', form=form)

@controllers.route('/user/dashboard')
def user_dashboard():
    # Check if user is logged in
    if not session.get('user_id'):
        flash('Please login to access your dashboard.', 'warning')
        return redirect(url_for('controllers.login'))
    
    # Get user's current reservations (not released yet)
    user_email = session.get('user_email')
    current_reservations = ReserveParkingSpot.query.filter_by(email=user_email, release_time=None).all()
    
    # Get parking lot details for each current reservation
    current_reservations_with_details = []
    for reservation in current_reservations:
        spot = ParkingSpot.query.get(reservation.spotid)
        lot = ParkingLot.query.get(reservation.lotid)
        if spot and lot:
            current_reservations_with_details.append({
                'reservation': reservation,
                'spot': spot,
                'lot': lot
            })
    
    # Get user's parking history (released reservations)
    historical_reservations = ReserveParkingSpot.query.filter_by(email=user_email).filter(ReserveParkingSpot.release_time.isnot(None)).order_by(ReserveParkingSpot.release_time.desc()).limit(10).all()
    
    # Get parking lot details for historical reservations
    historical_reservations_with_details = []
    for reservation in historical_reservations:
        spot = ParkingSpot.query.get(reservation.spotid)
        lot = ParkingLot.query.get(reservation.lotid)
        if spot and lot:
            # Calculate duration
            duration = reservation.release_time - reservation.parking_time
            hours = duration.total_seconds() / 3600
            
            historical_reservations_with_details.append({
                'reservation': reservation,
                'spot': spot,
                'lot': lot,
                'duration_hours': round(hours, 2)
            })
    
    return render_template('user_dashboard.html', 
                         current_reservations_with_details=current_reservations_with_details,
                         historical_reservations_with_details=historical_reservations_with_details)

@controllers.route('/user/parking-history')
def user_parking_history():
    # Check if user is logged in
    if not session.get('user_id'):
        flash('Please login to view your parking history.', 'warning')
        return redirect(url_for('controllers.login'))
    
    user_email = session.get('user_email')
    
    # Get all user's parking history (both current and historical)
    all_reservations = ReserveParkingSpot.query.filter_by(email=user_email).order_by(ReserveParkingSpot.parking_time.desc()).all()
    
    # Get parking lot details for all reservations
    all_reservations_with_details = []
    for reservation in all_reservations:
        spot = ParkingSpot.query.get(reservation.spotid)
        lot = ParkingLot.query.get(reservation.lotid)
        if spot and lot:
            # Calculate duration if released
            duration_hours = None
            if reservation.release_time:
                duration = reservation.release_time - reservation.parking_time
                duration_hours = round(duration.total_seconds() / 3600, 2)
            
            all_reservations_with_details.append({
                'reservation': reservation,
                'spot': spot,
                'lot': lot,
                'duration_hours': duration_hours
            })
    
    return render_template('user_parking_history.html', reservations_with_details=all_reservations_with_details)

@controllers.route('/user/book-spot/<int:lot_id>', methods=['POST'])
def book_parking_spot(lot_id):
    # Check if user is logged in
    if not session.get('user_id'):
        flash('Please login to book a parking spot.', 'warning')
        return redirect(url_for('controllers.login'))
    
    user_email = session.get('user_email')
    
    # Find the first available spot in this lot
    available_spot = ParkingSpot.query.filter_by(lotid=lot_id, status="A").first()
    
    if not available_spot:
        flash('No available spots in this parking lot.', 'danger')
        return redirect(url_for('controllers.parking_lots'))
    
    # Create reservation
    reservation = ReserveParkingSpot(
        spotid=available_spot.id,
        lotid=lot_id,
        email=user_email,
        veichleNumber=request.form.get('vehicle_number', ''),
        parking_time=datetime.now(),
        parkingcost=0,
        ispaid=0
    )
    
    # Update spot status to occupied
    available_spot.status = "O"
    
    # Update parking lot occupied count
    parking_lot = ParkingLot.query.get(lot_id)
    parking_lot.occupied += 1
    
    db.session.add(reservation)
    db.session.commit()
    
    flash(f'Successfully booked spot {available_spot.id} in {parking_lot.location}!', 'success')
    return redirect(url_for('controllers.user_dashboard'))

@controllers.route('/user/release-spot/<int:reservation_id>', methods=['POST'])
def release_parking_spot(reservation_id):
    # Check if user is logged in
    if not session.get('user_id'):
        flash('Please login to release a parking spot.', 'warning')
        return redirect(url_for('controllers.login'))
    
    user_email = session.get('user_email')
    
    # Get the reservation
    reservation = ReserveParkingSpot.query.get_or_404(reservation_id)
    
    # Check if this reservation belongs to the current user
    if reservation.email != user_email:
        flash('You can only release your own parking spots.', 'danger')
        return redirect(url_for('controllers.user_dashboard'))
    
    # Calculate parking cost (basic calculation)
    parking_lot = ParkingLot.query.get(reservation.lotid)
    parking_duration = datetime.now() - reservation.parking_time
    hours_parked = parking_duration.total_seconds() / 3600
    cost = int(hours_parked * parking_lot.price)
    
    # Update reservation
    reservation.release_time = datetime.now()
    reservation.parkingcost = cost
    reservation.ispaid = 1
    
    # Update spot status to available
    spot = ParkingSpot.query.get(reservation.spotid)
    spot.status = "A"
    
    # Update parking lot occupied count
    parking_lot.occupied -= 1
    
    db.session.commit()
    
    flash(f'Successfully released spot {spot.id}. Total cost: ₹{cost}', 'success')
    return redirect(url_for('controllers.user_dashboard'))

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
    
    # Get all parking lots with their statistics
    parking_lots = ParkingLot.query.all()
    return render_template('admin_dashboard.html', parking_lots=parking_lots)

@controllers.route('/admin/parking-lots/add', methods=['GET', 'POST'])
def add_parking_lot():
    # Check if user is logged in and is admin
    if not session.get('user_id') or session.get('user_role') != 'admin':
        flash('Access denied. Admin login required.', 'danger')
        return redirect(url_for('controllers.admin_login'))
    
    form = ParkingLotForm()
    if form.validate_on_submit():
        # Create new parking lot
        new_lot = ParkingLot(
            location=form.prime_location_name.data,
            address=form.address.data,
            pincode=form.pincode.data,
            price=form.price.data,
            maxSpots=form.maxSpots.data,
            occupied=0
        )
        db.session.add(new_lot)
        db.session.commit()
        
        # Create parking spots for this lot
        for i in range(1, form.maxSpots.data + 1):
            new_spot = ParkingSpot(
                lotid=new_lot.id,
                status="A"  # Available
            )
            db.session.add(new_spot)
        
        db.session.commit()
        flash(f'Parking lot "{form.prime_location_name.data}" created successfully with {form.maxSpots.data} spots!', 'success')
        return redirect(url_for('controllers.admin_dashboard'))
    
    return render_template('add_parking_lot.html', form=form)

@controllers.route('/admin/parking-lots/edit/<int:lot_id>', methods=['GET', 'POST'])
def edit_parking_lot(lot_id):
    # Check if user is logged in and is admin
    if not session.get('user_id') or session.get('user_role') != 'admin':
        flash('Access denied. Admin login required.', 'danger')
        return redirect(url_for('controllers.admin_login'))
    
    parking_lot = ParkingLot.query.get_or_404(lot_id)
    form = ParkingLotForm()
    
    if form.validate_on_submit():
        # Check if trying to reduce slots to less than occupied spots
        current_spots = ParkingSpot.query.filter_by(lotid=lot_id).count()
        new_spots_count = form.maxSpots.data
        occupied_spots = ParkingSpot.query.filter_by(lotid=lot_id, status="O").count()
        
        if new_spots_count < occupied_spots:
            flash(f'Cannot reduce slots to {new_spots_count}. {occupied_spots} spots are currently occupied. The new number of spots must be at least {occupied_spots}.', 'danger')
            return render_template('edit_parking_lot.html', form=form, parking_lot=parking_lot)
        
        # Update parking lot details (these can always be updated)
        parking_lot.location = form.prime_location_name.data
        parking_lot.address = form.address.data
        parking_lot.pincode = form.pincode.data
        parking_lot.price = form.price.data
        parking_lot.maxSpots = new_spots_count
        
        # Handle spot count changes
        if new_spots_count >= current_spots:
            # Add more spots
            for i in range(current_spots + 1, new_spots_count + 1):
                new_spot = ParkingSpot(lotid=lot_id, status="A")
                db.session.add(new_spot)
        elif new_spots_count < current_spots:
            # Remove spots (only if they're available and have no reservations)
            spots_to_remove = current_spots - new_spots_count
            available_spots = ParkingSpot.query.filter_by(lotid=lot_id, status="A").all()
            
            # Check if we have enough available spots to remove
            if len(available_spots) < spots_to_remove:
                flash(f'Cannot reduce slots. Only {len(available_spots)} spots are available, but you want to remove {spots_to_remove} spots.', 'danger')
                return render_template('edit_parking_lot.html', form=form, parking_lot=parking_lot)
            
            # Get spots that can be safely deleted (no reservations)
            spots_to_delete = []
            for spot in available_spots:
                if len(spots_to_delete) >= spots_to_remove:
                    break
                    
                # Check if this spot has any reservations
                reservations = ReserveParkingSpot.query.filter_by(spotid=spot.id).count()
                if reservations == 0:
                    spots_to_delete.append(spot)
            
            # Check if we have enough spots to delete
            if len(spots_to_delete) < spots_to_remove:
                flash(f'Cannot reduce slots. Some available spots have existing reservations that cannot be deleted.', 'danger')
                return render_template('edit_parking_lot.html', form=form, parking_lot=parking_lot)
            
            # Delete the spots that can be safely removed
            for spot in spots_to_delete:
                db.session.delete(spot)
        
        db.session.commit()
        
        flash(f'Parking lot "{form.prime_location_name.data}" updated successfully!', 'success')
        return redirect(url_for('controllers.admin_dashboard'))
    
    # Pre-fill form with existing data
    if request.method == 'GET':
        form.prime_location_name.data = parking_lot.location
        form.address.data = parking_lot.address
        form.pincode.data = parking_lot.pincode
        form.price.data = parking_lot.price
        form.maxSpots.data = parking_lot.maxSpots
    
    return render_template('edit_parking_lot.html', form=form, parking_lot=parking_lot)

@controllers.route('/admin/parking-lots/delete/<int:lot_id>', methods=['POST'])
def delete_parking_lot(lot_id):
    # Check if user is logged in and is admin
    if not session.get('user_id') or session.get('user_role') != 'admin':
        flash('Access denied. Admin login required.', 'danger')
        return redirect(url_for('controllers.admin_login'))
    
    parking_lot = ParkingLot.query.get_or_404(lot_id)
    
    # Check if any spots are occupied
    occupied_spots = ParkingSpot.query.filter_by(lotid=lot_id, status="O").count()
    
    if occupied_spots > 0:
        flash(f'Cannot delete parking lot. {occupied_spots} spots are currently occupied.', 'danger')
    else:
        try:
            # First, delete all reservations for spots in this lot
            # Get all spot IDs for this lot
            spot_ids = [spot.id for spot in ParkingSpot.query.filter_by(lotid=lot_id).all()]
            
            # Delete reservations for these spots
            if spot_ids:
                ReserveParkingSpot.query.filter(ReserveParkingSpot.spotid.in_(spot_ids)).delete(synchronize_session=False)
            
            # Then delete all parking spots for this lot
            ParkingSpot.query.filter_by(lotid=lot_id).delete()
            
            # Finally, delete the parking lot
            db.session.delete(parking_lot)
            db.session.commit()
            
            flash(f'Parking lot "{parking_lot.location}" deleted successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error deleting parking lot: {str(e)}', 'danger')
    
    return redirect(url_for('controllers.admin_dashboard'))

@controllers.route('/admin/parking-lots/<int:lot_id>')
def view_parking_lot_details(lot_id):
    # Check if user is logged in and is admin
    if not session.get('user_id') or session.get('user_role') != 'admin':
        flash('Access denied. Admin login required.', 'danger')
        return redirect(url_for('controllers.admin_login'))
    
    parking_lot = ParkingLot.query.get_or_404(lot_id)
    parking_spots = ParkingSpot.query.filter_by(lotid=lot_id).all()
    
    # Get reservation details for occupied spots
    occupied_spots_with_details = []
    for spot in parking_spots:
        if spot.status == "O":
            reservation = ReserveParkingSpot.query.filter_by(spotid=spot.id).first()
            if reservation:
                occupied_spots_with_details.append({
                    'spot': spot,
                    'reservation': reservation,
                    'user': User.query.filter_by(email=reservation.email).first()
                })
    
    return render_template('parking_lot_details.html', 
                         parking_lot=parking_lot, 
                         parking_spots=parking_spots,
                         occupied_spots_with_details=occupied_spots_with_details)

@controllers.route('/admin/users')
def admin_users():
    # Check if user is logged in and is admin
    if not session.get('user_id') or session.get('user_role') != 'admin':
        flash('Access denied. Admin login required.', 'danger')
        return redirect(url_for('controllers.admin_login'))
    
    # Get all users with their parking information
    users = User.query.filter(User.role != 'admin').all()
    
    # Get parking information for each user
    users_with_parking = []
    for user in users:
        # Get current active reservations
        active_reservations = ReserveParkingSpot.query.filter_by(email=user.email).all()
        
        # Get parking spot details for active reservations
        parking_info = []
        for reservation in active_reservations:
            spot = ParkingSpot.query.get(reservation.spotid)
            lot = ParkingLot.query.get(reservation.lotid)
            if spot and lot:
                parking_info.append({
                    'spot_id': spot.id,
                    'lot_name': lot.location,
                    'vehicle_number': reservation.veichleNumber,
                    'parking_time': reservation.parking_time,
                    'cost': reservation.parkingcost
                })
        
        users_with_parking.append({
            'user': user,
            'parking_info': parking_info,
            'active_spots': len(parking_info)
        })
    
    return render_template('admin_users.html', users_with_parking=users_with_parking)

@controllers.route('/admin/parking-records')
def admin_parking_records():
    # Check if user is logged in and is admin
    if not session.get('user_id') or session.get('user_role') != 'admin':
        flash('Access denied. Admin login required.', 'danger')
        return redirect(url_for('controllers.admin_login'))
    
    # Get all parking records with user details
    all_reservations = ReserveParkingSpot.query.order_by(ReserveParkingSpot.parking_time.desc()).all()
    
    # Get complete details for each reservation
    reservations_with_details = []
    for reservation in all_reservations:
        spot = ParkingSpot.query.get(reservation.spotid)
        lot = ParkingLot.query.get(reservation.lotid)
        user = User.query.filter_by(email=reservation.email).first()
        
        if spot and lot:
            # Calculate duration if released
            duration_hours = None
            if reservation.release_time:
                duration = reservation.release_time - reservation.parking_time
                duration_hours = round(duration.total_seconds() / 3600, 2)
            
            reservations_with_details.append({
                'reservation': reservation,
                'spot': spot,
                'lot': lot,
                'user': user,
                'duration_hours': duration_hours
            })
    
    return render_template('admin_parking_records.html', reservations_with_details=reservations_with_details)

@controllers.route('/admin/search')
def admin_search():
    # Check if user is logged in and is admin
    if not session.get('user_id') or session.get('user_role') != 'admin':
        flash('Access denied. Admin login required.', 'danger')
        return redirect(url_for('controllers.admin_login'))
    
    query = request.args.get('q', '').strip()
    search_type = request.args.get('type', 'all')
    
    results = {
        'users': [],
        'spots': [],
        'parking_lots': [],
        'reservations': []
    }
    
    if query:
        # Search users
        if search_type in ['all', 'users']:
            users = User.query.filter(
                (User.fullname.ilike(f'%{query}%')) |
                (User.email.ilike(f'%{query}%'))
            ).all()
            results['users'] = users
        
        # Search parking spots
        if search_type in ['all', 'spots']:
            spots = ParkingSpot.query.join(ParkingLot).filter(
                (ParkingSpot.id == query) |
                (ParkingLot.location.ilike(f'%{query}%'))
            ).all()
            results['spots'] = spots
        
        # Search parking lots
        if search_type in ['all', 'lots']:
            lots = ParkingLot.query.filter(
                (ParkingLot.location.ilike(f'%{query}%')) |
                (ParkingLot.address.ilike(f'%{query}%')) |
                (ParkingLot.pincode == query if query.isdigit() else False)
            ).all()
            results['parking_lots'] = lots
        
        # Search reservations
        if search_type in ['all', 'reservations']:
            reservations = ReserveParkingSpot.query.join(User).join(ParkingLot).filter(
                (User.fullname.ilike(f'%{query}%')) |
                (User.email.ilike(f'%{query}%')) |
                (ParkingLot.location.ilike(f'%{query}%')) |
                (ReserveParkingSpot.veichleNumber.ilike(f'%{query}%'))
            ).all()
            results['reservations'] = reservations
    
    return render_template('admin_search.html', results=results, query=query, search_type=search_type)

@controllers.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('controllers.home'))

