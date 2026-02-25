#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hospital & Lab Management System (Console, SQLite)
-------------------------------------------------
Single-file Python project suitable for college submissions.

How to run:
    python hospital_lab_system.py

Python version: 3.8+
Dependencies: Only Python standard library (sqlite3, datetime, textwrap, os, sys)

Author: Your Team
"""

import os
import sys
import sqlite3
from datetime import datetime
from textwrap import dedent

DB_PATH = os.path.join(os.path.dirname(__file__), "hospital_lab.db")


# ---------------------------
# Database Utilities
# ---------------------------
def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with connect() as conn:
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS doctors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                specialization TEXT,
                contact TEXT
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER,
                gender TEXT,
                contact TEXT,
                disease TEXT,
                doctor_id INTEGER,
                FOREIGN KEY (doctor_id) REFERENCES doctors(id)
                    ON UPDATE CASCADE ON DELETE SET NULL
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                doctor_id INTEGER NOT NULL,
                date TEXT NOT NULL,     -- YYYY-MM-DD
                time TEXT NOT NULL,     -- HH:MM (24h)
                notes TEXT,
                FOREIGN KEY (patient_id) REFERENCES patients(id)
                    ON UPDATE CASCADE ON DELETE CASCADE,
                FOREIGN KEY (doctor_id) REFERENCES doctors(id)
                    ON UPDATE CASCADE ON DELETE CASCADE
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS lab_tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                test_name TEXT NOT NULL,
                cost REAL NOT NULL DEFAULT 0,
                result TEXT,
                ordered_on TEXT NOT NULL,   -- ISO timestamp
                reported_on TEXT,           -- ISO timestamp
                FOREIGN KEY (patient_id) REFERENCES patients(id)
                    ON UPDATE CASCADE ON DELETE CASCADE
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS billing (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                amount REAL NOT NULL CHECK (amount >= 0),
                description TEXT,
                billed_on TEXT NOT NULL,   -- ISO date
                paid INTEGER NOT NULL DEFAULT 0, -- 0/1
                FOREIGN KEY (patient_id) REFERENCES patients(id)
                    ON UPDATE CASCADE ON DELETE CASCADE
            );
        """)

        conn.commit()


# ---------------------------
# Helpers & Validators
# ---------------------------
def input_nonempty(prompt):
    while True:
        s = input(prompt).strip()
        if s:
            return s
        print("Value cannot be empty. Try again.")


def input_int(prompt, allow_blank=False, min_value=None, max_value=None):
    while True:
        s = input(prompt).strip()
        if allow_blank and s == "":
            return None
        try:
            val = int(s)
            if min_value is not None and val < min_value:
                print(f"Enter >= {min_value}")
                continue
            if max_value is not None and val > max_value:
                print(f"Enter <= {max_value}")
                continue
            return val
        except ValueError:
            print("Please enter a valid integer.")


def input_float(prompt, allow_blank=False, min_value=None, max_value=None):
    while True:
        s = input(prompt).strip()
        if allow_blank and s == "":
            return None
        try:
            val = float(s)
            if min_value is not None and val < min_value:
                print(f"Enter >= {min_value}")
                continue
            if max_value is not None and val > max_value:
                print(f"Enter <= {max_value}")
                continue
            return val
        except ValueError:
            print("Please enter a valid number.")


def input_date(prompt="Date (YYYY-MM-DD): ", allow_blank=False):
    while True:
        s = input(prompt).strip()
        if allow_blank and s == "":
            return None
        try:
            datetime.strptime(s, "%Y-%m-%d")
            return s
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD.")


def input_time(prompt="Time (HH:MM, 24h): ", allow_blank=False):
    while True:
        s = input(prompt).strip()
        if allow_blank and s == "":
            return None
        try:
            datetime.strptime(s, "%H:%M")
            return s
        except ValueError:
            print("Invalid time format. Use HH:MM (24h).")


def press_enter():
    input("\nPress Enter to continue...")


def print_table(rows, headers=None):
    if not rows:
        print("No records found.")
        return
    if headers is None:
        headers = rows[0].keys()
    widths = [max(len(str(h)), max(len(str(r[h])) for r in rows)) for h in headers]
    sep = "+".join("-" * (w + 2) for w in widths)
    print("+" + sep + "+")
    print("| " + " | ".join(str(h).ljust(w) for h, w in zip(headers, widths)) + " |")
    print("+" + sep + "+")
    for r in rows:
        print("| " + " | ".join(str(r[h]).ljust(w) for h, w in zip(headers, widths)) + " |")
    print("+" + sep + "+")


# ---------------------------
# Doctor Module
# ---------------------------
def add_doctor():
    print("\n== Add Doctor ==")
    name = input_nonempty("Name: ")
    specialization = input("Specialization: ").strip()
    contact = input("Contact: ").strip()
    with connect() as conn:
        conn.execute("INSERT INTO doctors(name, specialization, contact) VALUES(?,?,?)",
                     (name, specialization, contact))
        conn.commit()
    print("Doctor added successfully!")


def view_doctors():
    print("\n== Doctors ==")
    with connect() as conn:
        cur = conn.execute("SELECT * FROM doctors ORDER BY id;")
        rows = cur.fetchall()
        print_table(rows)


def update_doctor():
    print("\n== Update Doctor ==")
    view_doctors()
    doc_id = input_int("Enter Doctor ID to update: ")
    with connect() as conn:
        cur = conn.execute("SELECT * FROM doctors WHERE id = ?", (doc_id,))
        row = cur.fetchone()
        if not row:
            print("Doctor not found.")
            return
        name = input(f"Name [{row['name']}]: ").strip() or row['name']
        spec = input(f"Specialization [{row['specialization'] or ''}]: ").strip() or row['specialization']
        contact = input(f"Contact [{row['contact'] or ''}]: ").strip() or row['contact']
        conn.execute("UPDATE doctors SET name=?, specialization=?, contact=? WHERE id=?",
                     (name, spec, contact, doc_id))
        conn.commit()
    print("Doctor updated successfully!")


def delete_doctor():
    print("\n== Delete Doctor ==")
    view_doctors()
    doc_id = input_int("Enter Doctor ID to delete: ")
    with connect() as conn:
        conn.execute("DELETE FROM doctors WHERE id=?", (doc_id,))
        conn.commit()
    print("Doctor deleted (if existed).")


# ---------------------------
# Patient Module
# ---------------------------
def add_patient():
    print("\n== Add Patient ==")
    name = input_nonempty("Name: ")
    age = input_int("Age: ", min_value=0)
    gender = input("Gender (M/F/Other): ").strip()
    contact = input("Contact: ").strip()
    disease = input("Disease/Complaint: ").strip()
    view_doctors()
    doctor_id = input_int("Assign Doctor ID (or blank to skip): ", allow_blank=True)
    with connect() as conn:
        conn.execute("""
            INSERT INTO patients(name, age, gender, contact, disease, doctor_id)
            VALUES(?,?,?,?,?,?)
        """, (name, age, gender, contact, disease, doctor_id))
        conn.commit()
    print("Patient added successfully!")


def view_patients():
    print("\n== Patients ==")
    with connect() as conn:
        cur = conn.execute("""
            SELECT p.id, p.name, p.age, p.gender, p.contact, p.disease,
                   d.name AS doctor
            FROM patients p
            LEFT JOIN doctors d ON d.id = p.doctor_id
            ORDER BY p.id;
        """)
        rows = cur.fetchall()
        print_table(rows, headers=["id", "name", "age", "gender", "contact", "disease", "doctor"])


def update_patient():
    print("\n== Update Patient ==")
    view_patients()
    pid = input_int("Enter Patient ID to update: ")
    with connect() as conn:
        cur = conn.execute("SELECT * FROM patients WHERE id = ?", (pid,))
        row = cur.fetchone()
        if not row:
            print("Patient not found.")
            return
        name = input(f"Name [{row['name']}]: ").strip() or row['name']
        age = input_int(f"Age [{row['age']}]: ", allow_blank=True, min_value=0)
        age = row['age'] if age is None else age
        gender = input(f"Gender [{row['gender'] or ''}]: ").strip() or row['gender']
        contact = input(f"Contact [{row['contact'] or ''}]: ").strip() or row['contact']
        disease = input(f"Disease [{row['disease'] or ''}]: ").strip() or row['disease']

        print("\nAssign/Change Doctor:")
        view_doctors()
        doctor_id = input_int(f"Doctor ID [{row['doctor_id'] or ''}] (blank to keep): ", allow_blank=True)
        doctor_id = row['doctor_id'] if doctor_id is None else doctor_id

        conn.execute("""
            UPDATE patients
               SET name=?, age=?, gender=?, contact=?, disease=?, doctor_id=?
             WHERE id=?
        """, (name, age, gender, contact, disease, doctor_id, pid))
        conn.commit()
    print("Patient updated successfully!")


def delete_patient():
    print("\n== Delete Patient ==")
    view_patients()
    pid = input_int("Enter Patient ID to delete: ")
    with connect() as conn:
        conn.execute("DELETE FROM patients WHERE id=?", (pid,))
        conn.commit()
    print("Patient deleted (if existed).")


# ---------------------------
# Appointments
# ---------------------------
def schedule_appointment():
    print("\n== Schedule Appointment ==")
    view_patients()
    pid = input_int("Patient ID: ")
    view_doctors()
    did = input_int("Doctor ID: ")
    date = input_date("Date (YYYY-MM-DD): ")
    time = input_time("Time (HH:MM, 24h): ")
    notes = input("Notes (optional): ").strip()
    with connect() as conn:
        conn.execute("""
            INSERT INTO appointments(patient_id, doctor_id, date, time, notes)
            VALUES(?,?,?,?,?)
        """, (pid, did, date, time, notes))
        conn.commit()
    print("Appointment scheduled!")


def view_appointments():
    print("\n== Appointments ==")
    with connect() as conn:
        cur = conn.execute("""
            SELECT a.id, a.date, a.time, p.name AS patient, d.name AS doctor, a.notes
              FROM appointments a
              JOIN patients p ON p.id = a.patient_id
              JOIN doctors d ON d.id = a.doctor_id
             ORDER BY a.date, a.time;
        """)
        rows = cur.fetchall()
        print_table(rows, headers=["id", "date", "time", "patient", "doctor", "notes"])


def delete_appointment():
    print("\n== Delete Appointment ==")
    view_appointments()
    aid = input_int("Appointment ID to delete: ")
    with connect() as conn:
        conn.execute("DELETE FROM appointments WHERE id=?", (aid,))
        conn.commit()
    print("Appointment deleted (if existed).")


# ---------------------------
# Lab Tests
# ---------------------------
def order_lab_test():
    print("\n== Order Lab Test ==")
    view_patients()
    pid = input_int("Patient ID: ")
    test_name = input_nonempty("Test Name: ")
    cost = input_float("Cost: ", min_value=0)
    ordered_on = datetime.now().isoformat(timespec="seconds")
    with connect() as conn:
        conn.execute("""
            INSERT INTO lab_tests(patient_id, test_name, cost, ordered_on)
            VALUES(?,?,?,?)
        """, (pid, test_name, cost, ordered_on))
        conn.commit()
    print("Lab test ordered!")


def enter_lab_result():
    print("\n== Enter/Update Lab Result ==")
    view_lab_tests(show_results=False)
    tid = input_int("Lab Test ID to update: ")
    result = input_nonempty("Result (text): ")
    reported_on = datetime.now().isoformat(timespec="seconds")
    with connect() as conn:
        conn.execute("""
            UPDATE lab_tests SET result=?, reported_on=? WHERE id=?
        """, (result, reported_on, tid))
        conn.commit()
    print("Lab result saved!")


def view_lab_tests(show_results=True):
    print("\n== Lab Tests ==")
    with connect() as conn:
        if show_results:
            cur = conn.execute("""
                SELECT lt.id, p.name AS patient, lt.test_name, lt.cost,
                       lt.ordered_on, lt.reported_on, COALESCE(lt.result, '') AS result
                  FROM lab_tests lt
                  JOIN patients p ON p.id = lt.patient_id
                 ORDER BY lt.ordered_on DESC;
            """)
            rows = cur.fetchall()
            print_table(rows, headers=["id", "patient", "test_name", "cost", "ordered_on", "reported_on", "result"])
        else:
            cur = conn.execute("""
                SELECT lt.id, p.name AS patient, lt.test_name, lt.cost, lt.ordered_on
                  FROM lab_tests lt
                  JOIN patients p ON p.id = lt.patient_id
                 WHERE lt.result IS NULL
                 ORDER BY lt.ordered_on DESC;
            """)
            rows = cur.fetchall()
            print_table(rows, headers=["id", "patient", "test_name", "cost", "ordered_on"])


# ---------------------------
# Billing
# ---------------------------
def create_bill():
    print("\n== Create Bill ==")
    view_patients()
    pid = input_int("Patient ID: ")
    description = input("Description (e.g., Consultation/Lab Test): ").strip()
    amount = input_float("Amount: ", min_value=0)
    billed_on = datetime.now().date().isoformat()
    with connect() as conn:
        conn.execute("""
            INSERT INTO billing(patient_id, amount, description, billed_on, paid)
            VALUES(?,?,?,?,0)
        """, (pid, amount, description, billed_on))
        conn.commit()
    print("Bill created!")


def view_bills(include_paid=True):
    print("\n== Bills ==")
    with connect() as conn:
        if include_paid:
            cur = conn.execute("""
                SELECT b.id, p.name AS patient, b.amount, b.description, b.billed_on,
                       CASE b.paid WHEN 1 THEN 'YES' ELSE 'NO' END AS paid
                  FROM billing b
                  JOIN patients p ON p.id = b.patient_id
                 ORDER BY b.billed_on DESC, b.id DESC;
            """)
        else:
            cur = conn.execute("""
                SELECT b.id, p.name AS patient, b.amount, b.description, b.billed_on
                  FROM billing b
                  JOIN patients p ON p.id = b.patient_id
                 WHERE b.paid = 0
                 ORDER BY b.billed_on DESC, b.id DESC;
            """)
        rows = cur.fetchall()
        if include_paid:
            print_table(rows, headers=["id", "patient", "amount", "description", "billed_on", "paid"])
        else:
            print_table(rows, headers=["id", "patient", "amount", "description", "billed_on"])


def mark_bill_paid():
    print("\n== Mark Bill as Paid ==")
    view_bills(include_paid=False)
    bid = input_int("Bill ID to mark as paid: ")
    with connect() as conn:
        conn.execute("UPDATE billing SET paid=1 WHERE id=?", (bid,))
        conn.commit()
    print("Bill updated!")


# ---------------------------
# Simple Reports
# ---------------------------
def report_patient_summary():
    print("\n== Report: Patient Summary ==")
    with connect() as conn:
        cur = conn.execute("""
            SELECT p.id, p.name,
                   COUNT(DISTINCT a.id) AS appointments,
                   COUNT(DISTINCT lt.id) AS lab_tests,
                   COALESCE(SUM(CASE WHEN b.paid=0 THEN b.amount ELSE 0 END), 0) AS unpaid_amount
              FROM patients p
         LEFT JOIN appointments a ON a.patient_id = p.id
         LEFT JOIN lab_tests lt ON lt.patient_id = p.id
         LEFT JOIN billing b ON b.patient_id = p.id
          GROUP BY p.id, p.name
          ORDER BY p.id;
        """)
        rows = cur.fetchall()
        print_table(rows, headers=["id", "name", "appointments", "lab_tests", "unpaid_amount"])


def report_doctor_load():
    print("\n== Report: Doctor Workload ==")
    with connect() as conn:
        cur = conn.execute("""
            SELECT d.id, d.name, d.specialization,
                   COUNT(DISTINCT a.id) AS appointments_count,
                   COUNT(DISTINCT p.id) AS patients_assigned
              FROM doctors d
         LEFT JOIN appointments a ON a.doctor_id = d.id
         LEFT JOIN patients p ON p.doctor_id = d.id
          GROUP BY d.id, d.name, d.specialization
          ORDER BY appointments_count DESC, d.name;
        """)
        rows = cur.fetchall()
        print_table(rows, headers=["id", "name", "specialization", "appointments_count", "patients_assigned"])


# ---------------------------
# Sample Data (Optional)
# ---------------------------
def seed_sample_data():
    with connect() as conn:
        cur = conn.cursor()
        # Doctors
        cur.executemany("""
            INSERT INTO doctors(name, specialization, contact) VALUES(?,?,?)
        """, [
            ("Dr. A. Sen", "Cardiology", "9876543210"),
            ("Dr. R. Gupta", "Orthopedics", "9876543211"),
            ("Dr. P. Bose", "General Medicine", "9876543212"),
        ])
        # Patients
        cur.executemany("""
            INSERT INTO patients(name, age, gender, contact, disease, doctor_id)
            VALUES(?,?,?,?,?,?)
        """, [
            ("S. Chatterjee", 35, "M", "9000000001", "Fever", 3),
            ("M. Das", 56, "F", "9000000002", "Chest Pain", 1),
            ("A. Khan", 42, "M", "9000000003", "Back Pain", 2),
        ])
        # Appointments
        cur.executemany("""
            INSERT INTO appointments(patient_id, doctor_id, date, time, notes)
            VALUES(?,?,?,?,?)
        """, [
            (1, 3, "2025-09-10", "10:00", "Follow-up"),
            (2, 1, "2025-09-11", "11:30", "New issue"),
            (3, 2, "2025-09-12", "09:15", "Routine check"),
        ])
        # Lab tests
        now = datetime.now().isoformat(timespec="seconds")
        cur.executemany("""
            INSERT INTO lab_tests(patient_id, test_name, cost, ordered_on, result, reported_on)
            VALUES(?,?,?,?,?,?)
        """, [
            (1, "CBC", 400, now, "Normal", now),
            (2, "ECG", 800, now, None, None),
        ])
        # Billing
        today = datetime.now().date().isoformat()
        cur.executemany("""
            INSERT INTO billing(patient_id, amount, description, billed_on, paid)
            VALUES(?,?,?,?,?)
        """, [
            (1, 500, "Consultation", today, 1),
            (1, 400, "CBC Test", today, 0),
            (2, 600, "Consultation", today, 0),
        ])
        conn.commit()
    print("Sample data inserted!")


# ---------------------------
# Menus
# ---------------------------
MAIN_MENU = dedent("""\
    \n===============================
      Hospital & Lab Management
    ===============================
    1) Patients
    2) Doctors
    3) Appointments
    4) Lab Tests
    5) Billing
    6) Reports
    7) Seed Sample Data
    0) Exit
""")

PATIENT_MENU = dedent("""\
    \n-- Patients --
    1) Add Patient
    2) View Patients
    3) Update Patient
    4) Delete Patient
    0) Back
""")

DOCTOR_MENU = dedent("""\
    \n-- Doctors --
    1) Add Doctor
    2) View Doctors
    3) Update Doctor
    4) Delete Doctor
    0) Back
""")

APPT_MENU = dedent("""\
    \n-- Appointments --
    1) Schedule Appointment
    2) View Appointments
    3) Delete Appointment
    0) Back
""")

LAB_MENU = dedent("""\
    \n-- Lab Tests --
    1) Order Lab Test
    2) Enter/Update Lab Result
    3) View Lab Tests
    4) View Pending Lab Tests
    0) Back
""")

BILL_MENU = dedent("""\
    \n-- Billing --
    1) Create Bill
    2) View All Bills
    3) View Unpaid Bills
    4) Mark Bill as Paid
    0) Back
""")

REPORT_MENU = dedent("""\
    \n-- Reports --
    1) Patient Summary
    2) Doctor Workload
    0) Back
""")


def patients_menu():
    while True:
        print(PATIENT_MENU)
        choice = input("Choose: ").strip()
        if choice == "1":
            add_patient(); press_enter()
        elif choice == "2":
            view_patients(); press_enter()
        elif choice == "3":
            update_patient(); press_enter()
        elif choice == "4":
            delete_patient(); press_enter()
        elif choice == "0":
            return
        else:
            print("Invalid choice!")


def doctors_menu():
    while True:
        print(DOCTOR_MENU)
        choice = input("Choose: ").strip()
        if choice == "1":
            add_doctor(); press_enter()
        elif choice == "2":
            view_doctors(); press_enter()
        elif choice == "3":
            update_doctor(); press_enter()
        elif choice == "4":
            delete_doctor(); press_enter()
        elif choice == "0":
            return
        else:
            print("Invalid choice!")


def appointments_menu():
    while True:
        print(APPT_MENU)
        choice = input("Choose: ").strip()
        if choice == "1":
            schedule_appointment(); press_enter()
        elif choice == "2":
            view_appointments(); press_enter()
        elif choice == "3":
            delete_appointment(); press_enter()
        elif choice == "0":
            return
        else:
            print("Invalid choice!")


def lab_menu():
    while True:
        print(LAB_MENU)
        choice = input("Choose: ").strip()
        if choice == "1":
            order_lab_test(); press_enter()
        elif choice == "2":
            enter_lab_result(); press_enter()
        elif choice == "3":
            view_lab_tests(show_results=True); press_enter()
        elif choice == "4":
            view_lab_tests(show_results=False); press_enter()
        elif choice == "0":
            return
        else:
            print("Invalid choice!")


def billing_menu():
    while True:
        print(BILL_MENU)
        choice = input("Choose: ").strip()
        if choice == "1":
            create_bill(); press_enter()
        elif choice == "2":
            view_bills(include_paid=True); press_enter()
        elif choice == "3":
            view_bills(include_paid=False); press_enter()
        elif choice == "4":
            mark_bill_paid(); press_enter()
        elif choice == "0":
            return
        else:
            print("Invalid choice!")


def reports_menu():
    while True:
        print(REPORT_MENU)
        choice = input("Choose: ").strip()
        if choice == "1":
            report_patient_summary(); press_enter()
        elif choice == "2":
            report_doctor_load(); press_enter()
        elif choice == "0":
            return
        else:
            print("Invalid choice!")


def main():
    init_db()
    while True:
        print(MAIN_MENU)
        choice = input("Choose: ").strip()
        if choice == "1":
            patients_menu()
        elif choice == "2":
            doctors_menu()
        elif choice == "3":
            appointments_menu()
        elif choice == "4":
            lab_menu()
        elif choice == "5":
            billing_menu()
        elif choice == "6":
            reports_menu()
        elif choice == "7":
            seed_sample_data(); press_enter()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid choice! Try again.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
