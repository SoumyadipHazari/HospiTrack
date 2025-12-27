from flask import Blueprint, request, redirect, url_for, render_template
from flask_login import login_required, current_user
from models import db, User, Patient, Doctor, Department, Appointment, Treatment
from datetime import datetime, date, timedelta, time
import json

patient_bp = Blueprint("patient", __name__)


def patient_only():
    return current_user.is_authenticated and current_user.role == "patient"


@patient_bp.route("/dashboard")
@login_required
def dashboard():
    if not patient_only():
        return "Access denied", 403

    patient = current_user.patient_profile
    if not patient:
        return "Patient profile not found", 500

    q = request.args.get("q", "").strip()


    doctors_query = Doctor.query.join(User).outerjoin(Department)


    if q:
        doctors_query = doctors_query.filter(
            (User.name.ilike(f"%{q}%")) |
            (Doctor.specialization.ilike(f"%{q}%")) |
            (Department.name.ilike(f"%{q}%"))
        )

    doctors = doctors_query.all()

    upcoming = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.date >= date.today(),
        Appointment.status == "Booked"
    ).order_by(Appointment.date, Appointment.time_start).all()


    return render_template(
        "patient/dashboard.html",
        patient=patient,
        doctors=doctors,
        upcoming=upcoming,
        q=q   
    )


@patient_bp.route("/doctor/<int:doctor_id>")
@login_required
def doctor_details(doctor_id):
    if not patient_only():
        return "Access denied", 403

    doctor = Doctor.query.get_or_404(doctor_id)
    return render_template("patient/doctor_details.html", doctor=doctor)


@patient_bp.route("/doctor/<int:doctor_id>/availability")
@login_required
def doctor_availability(doctor_id):
    if not patient_only():
        return "Access denied", 403

    doctor = Doctor.query.get_or_404(doctor_id)


    availability = json.loads(doctor.availability) if doctor.availability else {}


    today = date.today()
    dates = [(today + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]


    booked = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.status == "Booked"
    ).all()

    booked_slots = {(str(a.date), a.time_start.strftime("%H:%M")) for a in booked}

    patient = current_user.patient_profile
    my_booked = Appointment.query.filter_by(
        doctor_id=doctor.id,
        patient_id=patient.id,
        status="Booked"
    ).all()
    patient_booked_slots = {(str(a.date), a.time_start.strftime("%H:%M")) for a in my_booked}

    return render_template(
        "patient/doctor_availability.html",
        doctor=doctor,
        dates=dates,
        availability=availability,
        booked_slots=booked_slots,
        patient_booked_slots=patient_booked_slots
    )

@patient_bp.route("/book", methods=["POST"])
@login_required
def book_appointment():
    if not patient_only():
        return "Access denied", 403

    patient = current_user.patient_profile

    doctor_id = request.form.get("doctor_id")
    date_str = request.form.get("date")
    time_start_str = request.form.get("time_start")
    time_end_str = request.form.get("time_end")

    if not doctor_id or not date_str or not time_start_str or not time_end_str:
        return redirect(url_for("patient.doctor_availability", doctor_id=doctor_id))

    appt_date = datetime.strptime(date_str, "%Y-%m-%d").date()

    try:
        h1, m1 = map(int, time_start_str.split(":"))
        h2, m2 = map(int, time_end_str.split(":"))
        time_start = time(h1, m1)
        time_end = time(h2, m2)
    except:
        return redirect(url_for("patient.doctor_availability", doctor_id=doctor_id))
    


    conflict = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.date == appt_date,
        Appointment.time_start == time_start,
        Appointment.status == "Booked"
    ).first()

    if conflict:
        return redirect(url_for("patient.doctor_availability", doctor_id=doctor_id) + "?error=booked")

    already = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.patient_id == patient.id,
        Appointment.date == appt_date,
        Appointment.status == "Booked"
    ).first()

    if already:
        return redirect(url_for("patient.doctor_availability", doctor_id=doctor_id) + "?error=own")

    appointment = Appointment(
        patient_id=patient.id,
        doctor_id=doctor_id,
        date=appt_date,
        time_start=time_start,
        time_end=time_end,
        status="Booked"
    )

    db.session.add(appointment)
    db.session.commit()
    db.session.expire_all() 

    return redirect(url_for("patient.dashboard"))

@patient_bp.route("/history")
@login_required
def appointment_history():
    if not patient_only():
        return "Access denied", 403

    patient = current_user.patient_profile

    past_appointments = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.status == "Completed"
    ).order_by(Appointment.date.desc()).all()

    return render_template(
        "patient/history.html",
        appointments=past_appointments
    )

@patient_bp.route("/cancel/<int:app_id>")
@login_required
def cancel_appointment(app_id):
    if not patient_only():
        return "Access denied", 403

    appointment = Appointment.query.get_or_404(app_id)

    if appointment.patient_id != current_user.patient_profile.id:
        return "Cannot cancel this appointment", 403

    appointment.status = "Cancelled"
    db.session.commit()
    db.session.expire_all()

    return redirect(url_for("patient.dashboard"))


@patient_bp.route("/edit", methods=["GET"], endpoint="edit_profile_page")
@login_required
def edit_profile_page():
    if not patient_only():
        return "Access denied", 403

    patient = current_user.patient_profile
    return render_template("patient/edit_profile.html", patient=patient)


@patient_bp.route("/edit", methods=["POST"], endpoint="edit_profile")
@login_required
def edit_profile():
    if not patient_only():
        return "Access denied", 403

    patient = current_user.patient_profile

    patient.contact = request.form.get("contact")
    patient.address = request.form.get("address")

    db.session.commit()
    return redirect(url_for("patient.dashboard"))


@patient_bp.route("/search")
@login_required
def search_doctor():
    if not patient_only():
        return "Access denied", 403

    query = request.args.get("q", "")

    doctors = Doctor.query.join(User).filter(
        (User.name.contains(query)) |
        (Doctor.specialization.contains(query))
    ).all()

    return {
        "results": [
            {
                "id": d.id,
                "name": d.user.name,
                "specialization": d.specialization,
                "availability": json.loads(d.availability) if d.availability else {}
            }
            for d in doctors
        ]
    }
