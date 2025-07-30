from database import db
import datetime

class User(db.Model):
    __tablename__ = 'user'
    id= db.Column(db.Integer(), primary_key=True)
    fullname = db.Column(db.String(30), nullable = False)
    email = db.Column(db.String(25), unique = True,nullable = False)
    password = db.Column(db.String(), nullable= False)
    role = db.Column(db.String(10), nullable=False, default='user')
    status=db.Column(db.Integer(), nullable=False)
    
    reservations_by_email = db.relationship('ReserveParkingSpot', backref='user_email_rel', foreign_keys='ReserveParkingSpot.email', primaryjoin="User.email == ReserveParkingSpot.email", lazy=True)
    
    def __repr__(self):
        return f'User {self.fullname}'

class ParkingLot(db.Model):
    __tablename__ = 'parking_lot'
    id=db.Column(db.Integer(), primary_key=True)
    location = db.Column(db.String(50), nullable=False)
    pincode=db.Column(db.Integer(), nullable=False)
    price=db.Column(db.Integer(), nullable=False)   
    maxSpots=db.Column(db.Integer(), nullable=False) 
    address=db.Column(db.String(200), nullable=False)
    occupied=db.Column(db.Integer(), default=0)
    
    parking_spots = db.relationship('ParkingSpot', backref='parking_lot', lazy=True)
    
    def __repr__(self):
        return f'ParkingLot {self.id}'

class ParkingSpot(db.Model):
    __tablename__ = 'parking_spot'
    id=db.Column(db.Integer(), primary_key=True)
    lotid=db.Column(db.Integer(), db.ForeignKey('parking_lot.id'), nullable=False)
    status = db.Column(db.String(5), default="A")
    veichleNumber=db.Column(db.String(20), nullable=True)
    
    def __repr__(self):
        return f'ParkingSpot {self.id}_{self.lotid}'

class ReserveParkingSpot(db.Model):
    __tablename__ = 'reserve_parking_spot'
    id=db.Column(db.Integer(), primary_key=True)
    spotid=db.Column(db.Integer(), db.ForeignKey('parking_spot.id'), nullable=False)
    lotid=db.Column(db.Integer(), db.ForeignKey('parking_lot.id'), nullable=False)
    email=db.Column(db.String(25), db.ForeignKey('user.email'), nullable=False)
    veichleNumber=db.Column(db.String(50), nullable=True)
    parking_time=db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    release_time=db.Column(db.DateTime, nullable=True)
    parkingcost=db.Column(db.Integer(), nullable=True, default=0)
    ispaid=db.Column(db.Integer(), default=0)
    
    parking_spot_rel = db.relationship('ParkingSpot', backref='reservations', foreign_keys=[spotid], lazy=True)
    parking_lot_rel = db.relationship('ParkingLot', backref='reservations', foreign_keys=[lotid], lazy=True)
    
    def __repr__(self):
        return f'Reservation {self.email}'

