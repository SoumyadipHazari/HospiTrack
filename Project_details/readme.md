# Hospital management app 

You are required to build a Hospital Management System (HMS) web application that allows Admins, Doctors, and Patients to interact with the system based on their roles.

### These are the mandatory frameworks on which the project has to be built.
- Flask for application back-end
- Jinja2 templating, HTML, CSS and Bootstraps for application front-end
- SQLite for database (No other database is permitted)

# Roles and Functionalities 
1. Admin
   - Admin is the pre-existing superuser of the application
   - Can add, update, and delete doctor profiles (name, specialization, availability).
   - Can view and manage all appointments.
   - Can search for patients or doctors by name/specialization.
  
2. Doctor
   - Can log in to view assigned appointments.
   - Can mark a patient’s visit as completed and enter diagnosis & treatment notes.
   - Can view patient history (previous diagnoses & prescriptions).

3. Patient
   - Can register, log in, and update their profile.
   - Can search for doctors by specialization and availability.
   - Can book, reschedule, or cancel an appointment.
   - Can view their own appointment history and treatment details.

# Key terminologies
1. Admin -- A superuser with the highest level of access who manages doctors,appoinments and overall hospital data (He can set appoinments, can add doctors, can add patients, can check the profiles of the doctors and patients) (What he can't do is to change the treatment details made by the doctor), he can appoint a patient to a doctor or can ask for another date to the user 

2. Doctor -- A medical professional registered in the system who interacts with patients via the app

3. Patient  -- A user who seeks for the medical care and can interact with the doctors and check their profile and according with that can make appointments and can check their treatments 

4. Appointment (A scheduled meeting between a patient and doctor for treatment)

- Attributes
  - Patient ID
  - Doctor ID
  - Date 
  - Time
  - Status (Booked/Completed/Cancelled)
  - etc

5. Treatment (A record of medical care provided to a patient during an appointment)
   - Attributes
     - Appointment ID
     - Diagnosis
     - Prescription
     - Notes
     - etc
  
  6. Department/Specialization: A field of medical science in which a particular doctor is specialized
    - Attributes
      - Department ID
      - Department Name
      - Description
      - Doctors_registered 
      - etc

# Core Features

1. Admin Functionalities 
    - Admin dashboard must display total number of doctors, patients, and appointments and also there profiles etc.
    - Admin should pre-exist in the app i.e. it must be created programmatically after the creation of the database. [No admin registration allowed]
    - Admin can add/update doctor profiles
    - Admin can view all upcoming and past appointments.
    - Admin can search for patients or doctors and view their details.
    - Admin can edit doctor details such as name, specialization etc., and also patient info if needed.
    - Admin can remove doctors and patients from the system

2. Doctors functionality
    - Doctor’s dashboard must display upcoming appointments for the day/week.
    - Doctor’s dashboard must show list of patients assigned to the doctor.
    - Doctor's dashboard must have the option to mark appointments as Completed or Cancelled.
    - Doctors can provide their availability for the next 7 days.
    - Doctors can update patient treatment history like provide diagnosis, treatment and prescriptions. (I am thinking of taking this as a normal text fromat like it will be form right beside of the patient profile where Medicine names, Notes and diagnosis will be there)

3. Patient Functionalities
    - Patients can register and login themselves on the app.
    - Patients’ Dashboard must display all available specialization/departments
    - Patients’ Dashboard must display availability of doctors for the coming 7 days (1 week) and patients can read doctors profiles.
    - It must display upcoming appointments and their status.
    - It must show past appointment history with diagnosis and prescriptions. (if it is there)
    - Patients can edit their profile.
    - Patients can book as well as cancel appointments with doctors.

## Other core functionalities 
- Prevent multiple appointments at the same date and time for the same doctor.
- Update appointment status dynamically (Booked → Completed → Cancelled).
- Admin and Patient should be able to search for a specialization or by a doctor’s name
- Admin should be able to search patients by name, ID, or contact information.
- Store all completed appointment records for each patient.
- Include diagnosis, prescriptions, and doctor notes for each visit.
- Allow patients to view their own treatment history.
- Allow doctors to view the full history of their patients for informed consultation.


HospitalManagementSystem

│

├── app.py

├── models.py

├── requirements.txt

├── config.py

│

├── instance/

│ └── hms.db # SQLite is generated here automatically

│

├── static/

│ ├── css/

│ │ └── style.css # (optional) minimal custom css

│ └── images/ # (optional)

│

├── templates/

│ ├── layout.html # base layout with navbar

│ │

│ ├── auth/

│ │ ├── login.html

│ │ └── register.html

│ │

│ ├── admin/

│ │ ├── dashboard.html

│ │ ├── add\_doctor.html

│ │ ├── edit\_doctor.html

│ │ ├── view\_doctors.html

│ │ ├── view\_patients.html

│ │ └── appointments.html

│ │

│ ├── doctor/

│ │ ├── dashboard.html

│ │ ├── appointments.html

│ │ └── patient\_history.html

│ │

│ └── patient/

│ ├── dashboard.html

│ ├── book\_appointment.html

│ ├── appointment\_history.html

│ └── edit\_profile.html

│

└── blueprints/

├── auth.py

├── admin.py

├── doctor.py

└── patient.py
