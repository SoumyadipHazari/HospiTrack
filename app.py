from flask import Flask, render_template
from flask_login import LoginManager
from models import db, User
from dotenv import load_dotenv
import os

def create_app():
    load_dotenv()
    app = Flask(__name__, instance_relative_config=True)
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hms.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.query.get(int(user_id))
        except Exception:
            return None
    
    from blueprints.auth import auth_bp
    from blueprints.admin import admin_bp
    from blueprints.doctor import doctor_bp
    from blueprints.patient import patient_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(doctor_bp, url_prefix="/doctor")
    app.register_blueprint(patient_bp, url_prefix="/patient")

    with app.app_context():
        db.create_all()

        admin = User.query.filter_by(role="admin").first()
        if not admin:
            admin = User(
                name="Admin User",
                email="admin@example.com",
                role="admin"
            )
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()
            print(">> Default Admin Created: admin@example.com / admin123")
        else:
            print(">> Admin already exists")

    @app.route("/")
    def home():
        return render_template("index.html")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
