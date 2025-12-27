from flask import Blueprint, request, redirect, render_template, url_for
from flask_login import login_required, current_user
from models import db, User, Doctor, Patient, Appointment, Treatment
from datetime import datetime, date, timedelta
import json

doctor_bp = Blueprint("doctor", __name__)


def doctor_only():
    return current_user.is_authenticated and current_user.role == "doctor"



@doctor_bp.route("/dashboard")
@login_required
def doctor_dashboard():
    if not doctor_only():
        return "Access denied", 403

    doctor = current_user.doctor_profile
    today = date.today()

    upcoming = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.date >= today,
        Appointment.status == "Booked"   
    ).order_by(Appointment.date, Appointment.time_start).all()


    assigned_patients = upcoming

    next_7_days = [(today + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

    saved = {}
    if doctor.availability:
        try:
            saved = json.loads(doctor.availability)
        except:
            saved = {}

    return render_template(
        "doctor/dashboard.html",
        doctor=doctor,
        upcoming=upcoming,
        assigned_patients=assigned_patients,
        next_7_days=next_7_days,
        saved=saved
    )




@doctor_bp.route("/update/<int:app_id>", methods=["GET"])
@login_required
def update_history_page(app_id):
    if not doctor_only():
        return "Access denied", 403

    appointment = Appointment.query.get_or_404(app_id)

    if appointment.doctor_id != current_user.doctor_profile.id:
        return "Unauthorized", 403

    return render_template(
        "doctor/update_history.html",
        appointment=appointment
    )




@doctor_bp.route("/update/<int:app_id>", methods=["POST"])
@login_required
def update_history(app_id):
    if not doctor_only():
        return "Access denied", 403

    appointment = Appointment.query.get_or_404(app_id)

    if appointment.doctor_id != current_user.doctor_profile.id:
        return "Unauthorized", 403

    visit_type = request.form.get("visit_type")
    test_done = request.form.get("test_done")
    diagnosis = request.form.get("diagnosis")
    prescription = request.form.get("prescription")
    medicines = request.form.get("medicines")

    if appointment.treatment:
        t = appointment.treatment
    else:
        t = Treatment(appointment_id=appointment.id)
        db.session.add(t)

    t.diagnosis = diagnosis
    t.prescription = prescription
    t.notes = f"Visit Type: {visit_type}, Tests: {test_done}, Medicines: {medicines}"

    db.session.commit()

    return redirect(url_for("doctor.doctor_dashboard"))


@doctor_bp.route("/history/<int:patient_id>")
@login_required
def patient_history(patient_id):
    if not doctor_only():
        return "Access denied", 403

    doctor = current_user.doctor_profile

    appointments = Appointment.query.filter_by(
        patient_id=patient_id,
        doctor_id=doctor.id
    ).order_by(Appointment.date).all()

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
                "date": a.date
            })

    patient = Patient.query.get_or_404(patient_id)

    return render_template(
        "doctor/patient_history.html",
        patient=patient,
        doctor=doctor,
        history=history
    )




@doctor_bp.route("/complete/<int:app_id>")
@login_required
def mark_complete(app_id):
    if not doctor_only():
        return "Access denied", 403

    app = Appointment.query.get_or_404(app_id)

    if app.doctor_id != current_user.doctor_profile.id:
        return "Unauthorized", 403

    app.status = "Completed"
    db.session.commit()

    return redirect(url_for("doctor.doctor_dashboard"))




@doctor_bp.route("/cancel/<int:app_id>")
@login_required
def cancel_appointment(app_id):
    if not doctor_only():
        return "Access denied", 403

    app = Appointment.query.get_or_404(app_id)

    if app.doctor_id != current_user.doctor_profile.id:
        return "Unauthorized", 403

    app.status = "Cancelled"
    db.session.commit()

    return redirect(url_for("doctor.doctor_dashboard"))


@doctor_bp.route("/availability")
@login_required
def availability_page():
    if not doctor_only():
        return "Access denied", 403

    doctor = current_user.doctor_profile

    saved = {}
    if doctor.availability:
        try:
            saved = json.loads(doctor.availability)
        except:
            saved = {}

    today = date.today()
    next_7_days = [(today + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

    return render_template(
        "doctor/availability.html",
        next_7_days=next_7_days,
        saved=saved
    )


@doctor_bp.route("/availability", methods=["POST"])
@login_required
def save_availability():
    if not doctor_only():
        return "Access denied", 403

    doctor = current_user.doctor_profile

    availability = {}

    for i in range(1, 8):
        availability[f"day_{i}"] = {
            "morning": request.form.get(f"morning_{i}", ""),
            "evening": request.form.get(f"evening_{i}", "")
        }

    doctor.availability = json.dumps(availability)
    db.session.commit()

    return redirect(url_for("doctor.doctor_dashboard"))
