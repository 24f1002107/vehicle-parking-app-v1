# VeePark [Vehicle Parking App - V1]
**(MAD 1 - IITM)**

A comprehensive web-based parking management system built with Flask, SQLAlchemy, and Bootstrap. This application allows users to book parking spots and administrators to manage parking lots efficiently.

## 🚗 Features

### For Users
- **User Registration & Authentication**: Secure user registration and login system
- **Parking Lot Browsing**: View all available parking lots with real-time availability
- **Spot Booking**: Book available parking spots with vehicle number
- **Parking History**: View complete parking history with duration and costs
- **Spot Release**: Release parking spots and get cost calculation
- **User Dashboard**: Personalized dashboard showing current and historical reservations

### For Administrators
- **Admin Authentication**: Secure admin login system
- **Parking Lot Management**: 
  - Add new parking lots with custom details
  - Edit existing parking lots (location, address, price, spot count)
  - Delete parking lots (when no spots are occupied)
  - View detailed parking lot information
- **User Management**: Monitor all users and their parking activities
- **Parking Records**: Complete history of all parking transactions
- **Advanced Search**: Search across users, spots, lots, and reservations
- **Real-time Statistics**: Occupancy rates and parking lot performance

## 🛠️ Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, Bootstrap 5
- **Authentication**: Werkzeug password hashing
- **Session Management**: Flask sessions

## 📋 Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/24f1002107/vehicle-parking-app-v1.git
   cd vehicle_parking_24f1002107
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv mvenv
   ```

3. **Activate the virtual environment**
   - **Windows:**
     ```bash
     mvenv\Scripts\activate
     ```
   - **Linux/Mac:**
     ```bash
     source mvenv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Initialize the database**
   ```bash
   python init_db.py
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Access the application**
   - Open your browser and go to `http://localhost:5000`
   - For admin access, use the admin login page

## 📁 Project Structure

```
vehicle_parking_24f1002107/
├── app.py                          # Main Flask application
├── database.py                     # Database configuration
├── init_db.py                      # Database initialization script
├── requirements.txt                # Python dependencies
├── README.md                      # Project documentation
├── controllers/
│   ├── controllers.py             # Route handlers and business logic
│   └── forms.py                   # Flask-WTF form definitions
├── models/
│   └── models.py                  # SQLAlchemy database models
├── templates/                      # HTML templates
│   ├── index.html                 # Base template
│   ├── home.html                  # Home page
│   ├── login.html                 # User login
│   ├── register.html              # User registration
│   ├── admin_login.html           # Admin login
│   ├── user_dashboard.html        # User dashboard
│   ├── admin_dashboard.html       # Admin dashboard
│   ├── parking_lots.html          # Parking lots listing
│   ├── add_parking_lot.html       # Add parking lot form
│   ├── edit_parking_lot.html      # Edit parking lot form
│   └── ...                        # Other template files
└── instance/
    └── parking.db                 # SQLite database file
```

## 🗄️ Database Schema

### Users Table
- `id`: Primary key
- `fullname`: User's full name
- `email`: Unique email address
- `password`: Hashed password
- `role`: User role (user/admin)
- `status`: Account status

### Parking Lots Table
- `id`: Primary key
- `location`: Parking lot name/location
- `address`: Complete address
- `pincode`: Postal code
- `price`: Price per hour
- `maxSpots`: Maximum number of spots
- `occupied`: Currently occupied spots count

### Parking Spots Table
- `id`: Primary key
- `lotid`: Foreign key to parking lot
- `status`: Spot status (A=Available, O=Occupied)
- `veichleNumber`: Vehicle number (if occupied)

### Reserve Parking Spots Table
- `id`: Primary key
- `spotid`: Foreign key to parking spot
- `lotid`: Foreign key to parking lot
- `email`: User's email
- `veichleNumber`: Vehicle number
- `parking_time`: Booking time
- `release_time`: Release time (if released)
- `parkingcost`: Calculated cost
- `ispaid`: Payment status

## 🔐 Security Features

- **Password Hashing**: All passwords are hashed using Werkzeug
- **Session Management**: Secure session handling
- **Role-based Access**: Separate user and admin interfaces
- **Input Validation**: Form validation and sanitization
- **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection

## 🎯 Key Features Explained

### Smart Parking Lot Management
- **Dynamic Spot Management**: Add/remove parking spots with validation
- **Occupancy Protection**: Cannot reduce spots below occupied count
- **Reservation Safety**: Spots with reservations cannot be deleted
- **Real-time Updates**: Occupancy counts update automatically

### User Experience
- **Intuitive Interface**: Clean, responsive design with Bootstrap
- **Real-time Feedback**: Flash messages for all actions
- **Mobile Responsive**: Works on all device sizes
- **Quick Actions**: One-click booking and releasing

### Admin Controls
- **Comprehensive Dashboard**: Overview of all parking lots
- **Detailed Analytics**: User activity and parking statistics
- **Advanced Search**: Find specific users, spots, or reservations
- **Bulk Operations**: Manage multiple parking lots efficiently

## 🚦 Usage Guide

### For Users
1. **Register/Login**: Create an account or login
2. **Browse Lots**: View available parking lots
3. **Book Spot**: Select a lot and book an available spot
4. **Release Spot**: Release your spot when done
5. **View History**: Check your parking history and costs

### For Administrators
1. **Admin Login**: Use admin credentials
2. **Manage Lots**: Add, edit, or delete parking lots
3. **Monitor Users**: View user activities and reservations
4. **View Records**: Access complete parking transaction history
5. **Search Data**: Use advanced search for specific information

## 🔧 Configuration

### Environment Variables
The application uses default SQLite database. For production:
- Set `SQLALCHEMY_DATABASE_URI` for different database
- Configure `SECRET_KEY` for enhanced security
- Set `FLASK_ENV` for production/development modes

### Database Configuration
- **Development**: SQLite database (`instance/parking.db`)
- **Production**: Configure PostgreSQL or MySQL

## 🐛 Troubleshooting

### Common Issues
1. **Database Errors**: Run `python init_db.py` to recreate database
2. **Import Errors**: Ensure virtual environment is activated
3. **Port Issues**: Change port in `app.py` if 5000 is occupied
4. **Template Errors**: Check if all template files are present

### Debug Mode
Enable debug mode for development:
```python
app.debug = True
```

## 📈 Future Enhancements

- **Payment Integration**: Online payment processing
- **Mobile App**: Native mobile application
- **Real-time Notifications**: Push notifications for users
- **Advanced Analytics**: Detailed reporting and analytics
- **Multi-location Support**: Chain parking management
- **API Development**: RESTful API for third-party integrations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- **Developer**: Aman Kumar
- **Secondary Github ID**: [AmanChauhan16](https://github.com/AmanChauhan16)
- **Project**: VeePark [Vehicle Parking App - V1]
- **Version**: 1.0.0

## 📞 Support

For support and questions:
- Create an issue in the repository
- Contact: [Email:Aman Kumar](24f1002107@ds.study.iitm.ac.in)

---
