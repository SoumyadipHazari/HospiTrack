from flask import Blueprint, request, render_template, redirect, url_for
from flask_login import login_required, current_user
from models import db, User, Doctor, Patient, Department, Appointment, Treatment
from datetime import datetime

admin_bp = Blueprint("admin", __name__)


def admin_only():
    return current_user.is_authenticated and current_user.role == "admin"


@admin_bp.route("/dashboard")
@login_required
def dashboard():
    if not admin_only():
        return "Access denied", 403

    doctors = Doctor.query.all()
    patients = Patient.query.all()

    upcoming = Appointment.query.filter(
        Appointment.date >= datetime.today().date(),
        Appointment.status == "Booked"
    ).order_by(Appointment.date).all()

    return render_template(
        "admin/dashboard.html",
        doctors=doctors,
        patients=patients,
        upcoming=upcoming,
        total_doctors=len(doctors),
        total_patients=len(patients),
    )

@admin_bp.route("/appointment/cancel/<int:app_id>")
@login_required
def admin_cancel_appointment(app_id):
    if not admin_only():
        return "Access denied", 403

    app = Appointment.query.get_or_404(app_id)
    app.status = "Cancelled"
    db.session.commit()

    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/search")
@login_required
def search():
    if not admin_only():
        return "Access denied", 403

    query = request.args.get("query", "")

    doctors = Doctor.query.join(User).filter(User.name.contains(query)).all()
    patients = Patient.query.join(User).filter(User.name.contains(query)).all()

    return render_template(
        "admin/dashboard.html",
        doctors=doctors,
        patients=patients,
        upcoming=[],
        total_doctors=len(doctors),
        total_patients=len(patients),
        search_query=query,
        searching=True
    )


@admin_bp.route("/add-doctor")
@login_required
def add_doctor_html():
    if not admin_only():
        return "Access denied", 403

    departments = Department.query.all()
    return render_template("admin/add_doctor.html", departments=departments)


@admin_bp.route("/doctors/add", methods=["POST"])
@login_required
def add_doctor():
    if not admin_only():
        return "Access denied", 403

    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")
    specialization = request.form.get("specialization")
    department_id = request.form.get("department_id")

    if User.query.filter_by(email=email).first():
        return "Email already exists", 400

    user = User(name=name, email=email, role="doctor")
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    doctor = Doctor(
        user_id=user.id,
        specialization=specialization,
        department_id=department_id or None,
    )
    db.session.add(doctor)
    db.session.commit()

    return redirect(url_for("admin.dashboard"))

@admin_bp.route("/department/add", methods=["GET"])
@login_required
def add_department_page():
    if not admin_only():
        return "Access denied", 403

    return render_template("admin/add_department.html")


@admin_bp.route("/department/add", methods=["POST"])
@login_required
def add_department():
    if not admin_only():
        return "Access denied", 403

    name = request.form.get("name")
    desc = request.form.get("description")

    # prevent duplicate names
    if Department.query.filter_by(name=name).first():
        return "Department already exists", 400

    dept = Department(name=name, description=desc)
    db.session.add(dept)
    db.session.commit()

    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/doctors/edit/<int:doctor_id>", methods=["GET"])
@login_required
def edit_doctor_page(doctor_id):
    if not admin_only():
        return "Access denied", 403

    doctor = Doctor.query.get_or_404(doctor_id)
    departments = Department.query.all()

    return render_template("admin/edit_doctor.html",
                           doctor=doctor,
                           departments=departments)


@admin_bp.route("/doctors/edit/<int:doctor_id>", methods=["POST"])
@login_required
def edit_doctor(doctor_id):
    if not admin_only():
        return "Access denied", 403

    doctor = Doctor.query.get_or_404(doctor_id)
    
    doctor.specialization = request.form.get("specialization")
    doctor.department_id = request.form.get("department_id")

    db.session.commit()
    return redirect(url_for("admin.dashboard"))





@admin_bp.route("/doctors/delete/<int:doctor_id>")
@login_required
def delete_doctor(doctor_id):
    if not admin_only():
        return "Access denied", 403

    doctor = Doctor.query.get_or_404(doctor_id)
    user = doctor.user

    Appointment.query.filter_by(doctor_id=doctor_id).delete()

    db.session.delete(doctor)
    db.session.delete(user)
    db.session.commit()

    return redirect(url_for("admin.dashboard"))



@admin_bp.route("/patients/delete/<int:patient_id>")
@login_required
def delete_patient(patient_id):
    if not admin_only():
        return "Access denied", 403

    patient = Patient.query.get_or_404(patient_id)
    user = patient.user

    Appointment.query.filter_by(patient_id=patient_id).delete()

    db.session.delete(patient)
    db.session.delete(user)
    db.session.commit()

    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/patient/<int:patient_id>/history")
@login_required
def patient_history(patient_id):
    if not admin_only():
        return "Access denied", 403

    patient = Patient.query.get_or_404(patient_id)

    appointments = Appointment.query.filter_by(patient_id=patient_id).order_by(
        Appointment.date
    ).all()

    history = []

    for a in appointments:
        if a.treatment:

            raw = a.treatment.notes or ""
            cleaned = raw.replace("\n", " ").replace("  ", " ")

            vt = ""
            td = ""
            md = ""

            if "Visit Type:" in cleaned:
                try:
                    vt = cleaned.split("Visit Type:")[1].split("Tests:")[0].strip()
                except:
                    pass

            if "Tests:" in cleaned:
                try:
                    td = cleaned.split("Tests:")[1].split("Medicines:")[0].strip()
                except:
                    pass

            if "Medicines:" in cleaned:
                try:
                    md = cleaned.split("Medicines:")[1].strip()
                except:
                    pass

            vt = vt.rstrip(",").strip()
            td = td.rstrip(",").strip()
            md = md.rstrip(",").strip()

            history.append({
                "visit_type": vt,
                "test_done": td,
                "diagnosis": a.treatment.diagnosis,
                "prescription": a.treatment.prescription,
                "medicines": md,
                "doctor": a.doctor.user.name,
                "department": a.doctor.department.name if a.doctor.department else None,
                "date": a.date,
                "time_start": a.time_start,
                "time_end": a.time_end,
                "status": a.status,
                "appointment_id": a.id
            })

    return render_template(
        "admin/patient_history.html",
        patient=patient,
        history=history
    )