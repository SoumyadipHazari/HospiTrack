from flask import Blueprint, request, redirect, url_for, flash, render_template
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Patient

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        if User.query.filter_by(email=email).first():
            return "Email already exists", 400

        user = User(
            name=name,
            email=email,
            role="patient"
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        patient = Patient(
            user_id=user.id,
            dob=None,
            contact="",
            address=""
        )
        db.session.add(patient)
        db.session.commit()

        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            return "Invalid email or password", 401
        
        login_user(user)

        if user.role == "admin":
            return redirect("/admin/dashboard")
        elif user.role == "doctor":
            return redirect("/doctor/dashboard")
        elif user.role == "patient":
            return redirect("/patient/dashboard")

        return "Unknown role", 400

    return render_template("auth/login.html")



@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@auth_bp.route("/check")
@login_required
def check():
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role
    }
