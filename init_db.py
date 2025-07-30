from app import setup_app
from database import db
from models.models import User
from werkzeug.security import generate_password_hash

app = setup_app()

with app.app_context():
    db.create_all()
    print("Database created successfully :)")
    print("Tables created successfully :)")
    
    # Check if admin already exists
    existing_admin = User.query.filter_by(email="aman991173@gmail.com").first()
    
    if existing_admin:
        print("Admin already exists in the database.")
    else:
        print("Adding admin...")
        
        hashed_password = generate_password_hash("Admin@1234/", method='pbkdf2:sha256')
        
        admin = User(
            fullname ="Aman Kumar",
            email = "aman991173@gmail.com",
            password=hashed_password,
            role="admin",
            status=0
        )
        db.session.add(admin)
        db.session.commit()
        
        print("Admin added successfully :)")