from flask import Flask, render_template
from database import db
from controllers.controllers import controllers

def setup_app():
    app = Flask(__name__)
    app.debug=True
    app.config["SQLALCHEMY_DATABASE_URI"]= 'sqlite:///parking.db'
    db.init_app(app)
    app.app_context().push()
    app.register_blueprint(controllers)
    app.secret_key = "alpha6987"
    return app

app = setup_app()

if __name__ == "__main__":
    app.run()
