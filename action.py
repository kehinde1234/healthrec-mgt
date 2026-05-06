import datetime
from typing import Dict, List, Optional, Union
import uuid

class HealthcareRecordManagementSystem:
    def __init__(self):
        # Patients: {patient_id: {"name": str, "student_id": str, "dob": str, "contact": str, "medical_history": List[Dict]}}
        self.patients: Dict[str, Dict] = {}

        # Medical Records: {record_id: {"patient_id": str, "date": str, "diagnosis": str, "treatment": str, "doctor": str, "prescriptions": List[Dict]}}
        self.medical_records: Dict[str, Dict] = {}

        # Appointments: {appointment_id: {"patient_id": str, "date": str, "time": str, "doctor": str, "status": str, "reason": str}}
        self.appointments: Dict[str, Dict] = {}

        # Doctors: {doctor_id: {"name": str, "specialization": str, "contact": str, "schedule": Dict[str, List[str]]}}
        self.doctors: Dict[str, Dict] = {}

        # Prescriptions: {prescription_id: {"patient_id": str, "date": str, "medication": str, "dosage": str, "duration": str, "doctor": str}}
        self.prescriptions: Dict[str, Dict] = {}

        # Emergency Contacts: {patient_id: {"name": str, "relationship": str, "contact": str}}
        self.emergency_contacts: Dict[str, Dict] = {}

        # Audit Logs: List[Dict]
        self.audit_logs: List[Dict] = []

    # --- Patient Management ---
    def add_patient(self, name: str, student_id: str, dob: str, contact: str) -> str:
        """Add a new patient (student) to the system."""
        patient_id = str(uuid.uuid4())[:8]  # Generate a unique ID
        self.patients[patient_id] = {
            "name": name,
            "student_id": student_id,
            "dob": dob,
            "contact": contact,
            "medical_history": []
        }
        self._log_activity("patient_added", {"patient_id": patient_id, "name": name, "student_id": student_id})
        return f"Patient {name} added with ID: {patient_id}"

    def update_patient_contact(self, patient_id: str, new_contact: str) -> str:
        """Update a patient's contact information."""
        if patient_id in self.patients:
            self.patients[patient_id]["contact"] = new_contact
            self._log_activity("patient_updated", {"patient_id": patient_id, "new_contact": new_contact})
            return f"Contact updated for patient {patient_id}"
        return f"Patient ID {patient_id} not found."

    def add_emergency_contact(self, patient_id: str, name: str, relationship: str, contact: str) -> str:
        """Add an emergency contact for a patient."""
        if patient_id in self.patients:
            self.emergency_contacts[patient_id] = {
                "name": name,
                "relationship": relationship,
                "contact": contact
            }
            self._log_activity("emergency_contact_added", {"patient_id": patient_id, "name": name})
            return f"Emergency contact added for patient {patient_id}"
        return f"Patient ID {patient_id} not found."

    # --- Medical Records ---
    def create_medical_record(self, patient_id: str, diagnosis: str, treatment: str, doctor: str) -> str:
        """Create a new medical record for a patient."""
        if patient_id in self.patients and doctor in self.doctors:
            record_id = str(uuid.uuid4())[:8]
            self.medical_records[record_id] = {
                "patient_id": patient_id,
                "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "diagnosis": diagnosis,
                "treatment": treatment,
                "doctor": doctor,
                "prescriptions": []
            }
            self.patients[patient_id]["medical_history"].append(record_id)
            self._log_activity("record_created", {"record_id": record_id, "patient_id": patient_id, "diagnosis": diagnosis})
            return f"Medical record created with ID: {record_id}"
        return "Invalid patient ID or doctor ID."

    def add_prescription(self, record_id: str, medication: str, dosage: str, duration: str, doctor: str) -> str:
        """Add a prescription to a medical record."""
        if record_id in self.medical_records and doctor in self.doctors:
            prescription_id = str(uuid.uuid4())[:8]
            self.prescriptions[prescription_id] = {
                "patient_id": self.medical_records[record_id]["patient_id"],
                "date": datetime.datetime.now().strftime("%Y-%m-%d"),
                "medication": medication,
                "dosage": dosage,
                "duration": duration,
                "doctor": doctor
            }
            self.medical_records[record_id]["prescriptions"].append(prescription_id)
            self._log_activity("prescription_added", {"prescription_id": prescription_id, "record_id": record_id, "medication": medication})
            return f"Prescription added with ID: {prescription_id}"
        return "Invalid record ID or doctor ID."

    def get_patient_history(self, patient_id: str) -> List[Dict]:
        """Retrieve the medical history of a patient."""
        if patient_id in self.patients:
            history = []
            for record_id in self.patients[patient_id]["medical_history"]:
                record = self.medical_records[record_id]
                history.append({
                    "date": record["date"],
                    "diagnosis": record["diagnosis"],
                    "treatment": record["treatment"],
                    "doctor": record["doctor"],
                    "prescriptions": [self.prescriptions[pid] for pid in record["prescriptions"]]
                })
            return history
        return []

    # --- Appointment Management ---
    def add_doctor(self, name: str, specialization: str, contact: str) -> str:
        """Add a new doctor to the system."""
        doctor_id = str(uuid.uuid4())[:8]
        self.doctors[doctor_id] = {
            "name": name,
            "specialization": specialization,
            "contact": contact,
            "schedule": {}  # {day: [available_times]}
        }
        self._log_activity("doctor_added", {"doctor_id": doctor_id, "name": name, "specialization": specialization})
        return f"Doctor {name} added with ID: {doctor_id}"

    def set_doctor_schedule(self, doctor_id: str, day: str, times: List[str]) -> str:
        """Set the schedule for a doctor."""
        if doctor_id in self.doctors:
            self.doctors[doctor_id]["schedule"][day] = times
            self._log_activity("schedule_updated", {"doctor_id": doctor_id, "day": day, "times": times})
            return f"Schedule updated for doctor {doctor_id} on {day}"
        return f"Doctor ID {doctor_id} not found."

    def book_appointment(self, patient_id: str, doctor_id: str, date: str, time: str, reason: str) -> str:
        """Book an appointment for a patient with a doctor."""
        if patient_id in self.patients and doctor_id in self.doctors:
            # Check if the doctor is available at the requested time
            day = datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%A")
            if day in self.doctors[doctor_id]["schedule"] and time in self.doctors[doctor_id]["schedule"][day]:
                appointment_id = str(uuid.uuid4())[:8]
                self.appointments[appointment_id] = {
                    "patient_id": patient_id,
                    "doctor_id": doctor_id,
                    "date": date,
                    "time": time,
                    "status": "Booked",
                    "reason": reason
                }
                # Remove the time slot from the doctor's schedule
                self.doctors[doctor_id]["schedule"][day].remove(time)
                self._log_activity("appointment_booked", {"appointment_id": appointment_id, "patient_id": patient_id, "doctor_id": doctor_id})
                return f"Appointment booked with ID: {appointment_id}"
            return f"Doctor {doctor_id} is not available on {date} at {time}."
        return "Invalid patient ID or doctor ID."

    def cancel_appointment(self, appointment_id: str) -> str:
        """Cancel an appointment."""
        if appointment_id in self.appointments:
            appointment = self.appointments[appointment_id]
            doctor_id = appointment["doctor_id"]
            date = appointment["date"]
            time = appointment["time"]
            day = datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%A")

            # Return the time slot to the doctor's schedule
            self.doctors[doctor_id]["schedule"][day].append(time)
            self.appointments[appointment_id]["status"] = "Cancelled"
            self._log_activity("appointment_cancelled", {"appointment_id": appointment_id})
            return f"Appointment {appointment_id} cancelled."
        return f"Appointment ID {appointment_id} not found."

    # --- Audit Logging ---
    def _log_activity(self, action: str, details: Dict) -> None:
        """Log an activity to the audit trail."""
        log_entry = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "action": action,
            "details": details
        }
        self.audit_logs.append(log_entry)

    def get_audit_logs(self) -> List[Dict]:
        """Retrieve all audit logs."""
        return self.audit_logs

    # --- Reporting ---
    def generate_patient_report(self, patient_id: str) -> Dict:
        """Generate a comprehensive report for a patient."""
        if patient_id in self.patients:
            patient = self.patients[patient_id]
            report = {
                "patient_id": patient_id,
                "name": patient["name"],
                "student_id": patient["student_id"],
                "dob": patient["dob"],
                "contact": patient["contact"],
                "medical_history": self.get_patient_history(patient_id),
                "emergency_contact": self.emergency_contacts.get(patient_id, {}),
                "appointments": [
                    self.appointments[aid] for aid in self.appointments
                    if self.appointments[aid]["patient_id"] == patient_id
                ]
            }
            return report
        return {"error": "Patient ID not found"}

    def generate_clinic_stats(self) -> Dict:
        """Generate statistics for the clinic."""
        total_patients = len(self.patients)
        total_records = len(self.medical_records)
        total_appointments = len(self.appointments)
        total_doctors = len(self.doctors)

        return {
            "total_patients": total_patients,
            "total_records": total_records,
            "total_appointments": total_appointments,
            "total_doctors": total_doctors,
            "active_appointments": sum(1 for appt in self.appointments.values() if appt["status"] == "Booked")
        }

# --- Example Usage ---
if __name__ == "__main__":
    clinic = HealthcareRecordManagementSystem()

    # Add doctors
    print("=== Doctor Management ===")
    print(clinic.add_doctor("Dr. Smith", "General Practitioner", "smith@clinic.edu"))
    print(clinic.add_doctor("Dr. Johnson", "Pediatrics", "johnson@clinic.edu"))
    print(clinic.set_doctor_schedule("D1", "Monday", ["09:00", "10:00", "11:00", "14:00", "15:00"]))

    # Add patients
    print("\n=== Patient Management ===")
    print(clinic.add_patient("Alice Brown", "STU2023001", "2000-05-15", "alice@university.edu"))
    print(clinic.add_patient("Bob Green", "STU2023002", "1999-11-22", "bob@university.edu"))
    print(clinic.add_emergency_contact("P1", "John Brown", "Father", "john@email.com"))

    # Book appointments
    print("\n=== Appointment Management ===")
    print(clinic.book_appointment("P1", "D1", "2026-05-10", "10:00", "Annual Checkup"))
    print(clinic.book_appointment("P2", "D1", "2026-05-10", "11:00", "Flu Symptoms"))

    # Create medical records and prescriptions
    print("\n=== Medical Records ===")
    print(clinic.create_medical_record("P1", "Common Cold", "Rest and Fluids", "D1"))
    print(clinic.add_prescription("R1", "Ibuprofen", "400mg", "5 days", "D1"))

    # Generate reports
    print("\n=== Reports ===")
    print("Patient Report:", clinic.generate_patient_report("P1"))
    print("\nClinic Stats:", clinic.generate_clinic_stats())

    # Display audit logs
    print("\n=== Audit Logs ===")
    for log in clinic.get_audit_logs():
        print(f"{log['timestamp']}: {log['action']} - {log['details']}")
