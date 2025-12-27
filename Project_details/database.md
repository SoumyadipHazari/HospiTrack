# database structure
1. User
2. Doctor
3. Patient
4. Department
5. Appointment
6. Treatment
   
- User stores login info + role (admin/doctor/patient).
- Doctor and Patient extend User by linking using user_id (One-to-One)
- Department stores specialization. Doctors belong to a department
- Appointment connects a patient with a doctor on a date+time
- Treatment links to Appointment (One-to-One), and stores diagnosis & prescriptions.

## Table 1 -- User
Purpose: authentication + role management
1. id (primary key) (so it is user_id)
2. name
3. email
4. password_hash
5. role (admin/doctor/patient)

## Table 2 -- Doctor
attach extra doctor information
1. id (primary key) (doctor_id)
2. user_id (foreign key -> user.id) (one to one)
3. department_id (foreign key -> department.id)
4. specialization
5. availability (text/json)
one user --> one doctor profile

## table 3 -- Patient
1. id (primary key)
2. user_id (foreign key -> user.id)
3. dob
4. contact
5. address
one user --> one patient 

## table 4 -- department
1. id (primary key)
2. name
3. description
one department can have many doctoes but one doctor can't have many departments

## table 5 -- Appointment
1. id (primary key)
2. patient_id (foreign key -> patient.id)
3. doctor_id (foreign key -> doctor.id)
4. date
5. time_start
6. time_end
7. status (booked/completed/cancelled)
8. notes (prescription)

## relationship 
user -- Doctor (one to one)

User -- Patient (one to one)

Department -- Doctors (one to many)

Patient -- Appointments (one to many)

Doctor -- Appointment (one to many)

Appointment -- Treatment (one to one)


