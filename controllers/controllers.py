from flask import render_template, Blueprint
from models.models import User, ParkingLot, ParkingSpot, ReserveParkingSpot

controllers = Blueprint('controllers', __name__, template_folder='templates')

@controllers.route('/')
@controllers.route('/home')
def home():
    return render_template('home.html')

@controllers.route('/parkingLots')
def parkingLots():
    lots = ParkingLot.query.all()    
    return render_template('parkingLots.html', lots = lots)

@controllers.route('/parkingSpots')
def parkingSpots():
    spots = ParkingSpot.query.all()
    return render_template('parkingSpots.html', spots=spots)

