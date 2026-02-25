// Navigation handling
function showSection(sectionId) {
  document.querySelectorAll(".page").forEach(page => {
    page.classList.add("hidden");
  });
  document.getElementById(sectionId).classList.remove("hidden");
}

// ---------------- Patients ----------------
function addPatient(event) {
  event.preventDefault();
  let name = document.getElementById("pname").value;
  let age = document.getElementById("page").value;
  let gender = document.getElementById("pgender").value;

  let table = document.getElementById("patientTable");
  let row = table.insertRow();
  row.innerHTML = `<td>${name}</td><td>${age}</td><td>${gender}</td>`;

  event.target.reset();
}

// ---------------- Doctors ----------------
function addDoctor(event) {
  event.preventDefault();
  let name = document.getElementById("dname").value;
  let special = document.getElementById("dspecial").value;

  let table = document.getElementById("doctorTable");
  let row = table.insertRow();
  row.innerHTML = `<td>${name}</td><td>${special}</td>`;

  event.target.reset();
}

// ---------------- Appointments ----------------
function addAppointment(event) {
  event.preventDefault();
  let patient = document.getElementById("aname").value;
  let doctor = document.getElementById("adoctor").value;
  let date = document.getElementById("adate").value;

  let table = document.getElementById("appointmentTable");
  let row = table.insertRow();
  row.innerHTML = `<td>${patient}</td><td>${doctor}</td><td>${date}</td>`;

  event.target.reset();
}

// ---------------- Lab Tests ----------------
function addLabTest(event) {
  event.preventDefault();
  let patient = document.getElementById("ltpatient").value;
  let test = document.getElementById("lttest").value;

  let table = document.getElementById("labTable");
  let row = table.insertRow();
  row.innerHTML = `<td>${patient}</td><td>${test}</td>`;

  event.target.reset();
}

// ---------------- Billing ----------------
function addBill(event) {
  event.preventDefault();
  let patient = document.getElementById("bpatient").value;
  let amount = document.getElementById("bamount").value;

  let table = document.getElementById("billTable");
  let row = table.insertRow();
  row.innerHTML = `<td>${patient}</td><td>₹${amount}</td>`;

  event.target.reset();
}

// ---------------- Reports ----------------
function generateReport() {
  let report = `
    <h3>Report Generated:</h3>
    <p>Total Patients: ${document.getElementById("patientTable").rows.length}</p>
    <p>Total Doctors: ${document.getElementById("doctorTable").rows.length}</p>
    <p>Total Appointments: ${document.getElementById("appointmentTable").rows.length}</p>
    <p>Total Lab Tests: ${document.getElementById("labTable").rows.length}</p>
    <p>Total Bills: ${document.getElementById("billTable").rows.length}</p>
  `;
  document.getElementById("reportOutput").innerHTML = report;
}
