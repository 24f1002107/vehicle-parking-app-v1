from app import setup_app
from database import db
from models.models import User

app = setup_app()

with app.app_context():
    db.create_all()
    print("Database created successfully :)")
    print("Tables created successfully :)")
    print("Adding admin...")
    admin = User(
        fullname ="Aman Kumar",
        email = "aman991173@gmail.com",
        password="Admin@1234/",
        role="admin",
        status=0
    )
    db.session.add(admin)
    db.session.commit()
    
    print("Admin added successfully :)")