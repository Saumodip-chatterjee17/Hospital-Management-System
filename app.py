from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

# ---------- Database Setup ----------
def init_db():
    conn = sqlite3.connect("hospital.db")
    c = conn.cursor()
    # Patients
    c.execute("""CREATE TABLE IF NOT EXISTS patients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT, age INTEGER, gender TEXT)""")
    # Doctors
    c.execute("""CREATE TABLE IF NOT EXISTS doctors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT, specialization TEXT)""")
    # Appointments
    c.execute("""CREATE TABLE IF NOT EXISTS appointments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient TEXT, doctor TEXT, date TEXT)""")
    # Lab Tests
    c.execute("""CREATE TABLE IF NOT EXISTS lab_tests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient TEXT, test_name TEXT)""")
    # Billing
    c.execute("""CREATE TABLE IF NOT EXISTS billing (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient TEXT, amount REAL)""")
    conn.commit()
    conn.close()

init_db()

# ---------- Routes ----------
@app.route("/")
def home():
    return render_template("index.html")

# Add Patient
@app.route("/add_patient", methods=["POST"])
def add_patient():
    data = request.json
    conn = sqlite3.connect("hospital.db")
    c = conn.cursor()
    c.execute("INSERT INTO patients (name, age, gender) VALUES (?, ?, ?)",
              (data["name"], data["age"], data["gender"]))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

# Get Patients
@app.route("/get_patients", methods=["GET"])
def get_patients():
    conn = sqlite3.connect("hospital.db")
    c = conn.cursor()
    c.execute("SELECT name, age, gender FROM patients")
    rows = c.fetchall()
    conn.close()
    return jsonify(rows)

# Similar APIs for Doctors
@app.route("/add_doctor", methods=["POST"])
def add_doctor():
    data = request.json
    conn = sqlite3.connect("hospital.db")
    c = conn.cursor()
    c.execute("INSERT INTO doctors (name, specialization) VALUES (?, ?)",
              (data["name"], data["specialization"]))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

@app.route("/get_doctors", methods=["GET"])
def get_doctors():
    conn = sqlite3.connect("hospital.db")
    c = conn.cursor()
    c.execute("SELECT name, specialization FROM doctors")
    rows = c.fetchall()
    conn.close()
    return jsonify(rows)

# Appointments
@app.route("/add_appointment", methods=["POST"])
def add_appointment():
    data = request.json
    conn = sqlite3.connect("hospital.db")
    c = conn.cursor()
    c.execute("INSERT INTO appointments (patient, doctor, date) VALUES (?, ?, ?)",
              (data["patient"], data["doctor"], data["date"]))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

@app.route("/get_appointments", methods=["GET"])
def get_appointments():
    conn = sqlite3.connect("hospital.db")
    c = conn.cursor()
    c.execute("SELECT patient, doctor, date FROM appointments")
    rows = c.fetchall()
    conn.close()
    return jsonify(rows)

# Lab Tests
@app.route("/add_lab", methods=["POST"])
def add_lab():
    data = request.json
    conn = sqlite3.connect("hospital.db")
    c = conn.cursor()
    c.execute("INSERT INTO lab_tests (patient, test_name) VALUES (?, ?)",
              (data["patient"], data["test"]))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

@app.route("/get_lab", methods=["GET"])
def get_lab():
    conn = sqlite3.connect("hospital.db")
    c = conn.cursor()
    c.execute("SELECT patient, test_name FROM lab_tests")
    rows = c.fetchall()
    conn.close()
    return jsonify(rows)

# Billing
@app.route("/add_bill", methods=["POST"])
def add_bill():
    data = request.json
    conn = sqlite3.connect("hospital.db")
    c = conn.cursor()
    c.execute("INSERT INTO billing (patient, amount) VALUES (?, ?)",
              (data["patient"], data["amount"]))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

@app.route("/get_bills", methods=["GET"])
def get_bills():
    conn = sqlite3.connect("hospital.db")
    c = conn.cursor()
    c.execute("SELECT patient, amount FROM billing")
    rows = c.fetchall()
    conn.close()
    return jsonify(rows)

# Run
if __name__ == "__main__":
    app.run(debug=True)
