
from flask import Flask, render_template, request, redirect, session
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = "healthcare123"

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["healthcare_system"]

# Collections
patients = db["patients"]
appointments = db["appointments"]
sos_requests = db["sos_requests"]

# ---------------- REGISTER ----------------

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        patients.insert_one({
            "name": request.form['name'],
            "email": request.form['email'],
            "password": request.form['password']
        })

        return redirect('/login')

    return render_template('register.html')


# ---------------- LOGIN ----------------

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        user = patients.find_one({
            "email": email,
            "password": password
        })

        if user:
            session['user'] = user['name']
            return redirect('/dashboard')

        return "Invalid Email or Password"

    return render_template('login.html')


# ---------------- DASHBOARD ----------------

@app.route('/dashboard')
def dashboard():

    if 'user' not in session:
        return redirect('/login')

    total_patients = patients.count_documents({})
    total_appointments = appointments.count_documents({})
    total_sos = sos_requests.count_documents({})

    return render_template(
        'dashboard.html',
        total_patients=total_patients,
        total_appointments=total_appointments,
        total_sos=total_sos
    )


# ---------------- BOOK APPOINTMENT PAGE ----------------

@app.route('/book')
def book():

    if 'user' not in session:
        return redirect('/login')

    return render_template('book_appointment.html')


# ---------------- SAVE APPOINTMENT ----------------

@app.route('/book_appointment', methods=['POST'])
def book_appointment():

    appointments.insert_one({
        "patient_name": request.form['patient_name'],
        "doctor": request.form['doctor'],
        "department": request.form['department'],
        "date": request.form['date'],
        "time": request.form['time']
    })

    return redirect('/appointments')


# ---------------- VIEW APPOINTMENTS ----------------

@app.route('/appointments')
def view_appointments():

    if 'user' not in session:
        return redirect('/login')

    all_appointments = appointments.find()

    return render_template(
        'appointments.html',
        appointments=all_appointments
    )


# ---------------- DELETE APPOINTMENT ----------------

@app.route('/delete/<id>')
def delete(id):

    appointments.delete_one({
        "_id": ObjectId(id)
    })

    return redirect('/appointments')


# ---------------- SOS PAGE ----------------

@app.route('/sos')
def sos():

    if 'user' not in session:
        return redirect('/login')

    return render_template('sos.html')


# ---------------- SEND SOS ----------------

@app.route('/send_sos', methods=['POST'])
def send_sos():

    sos_requests.insert_one({

        "patient_name": request.form['patient_name'],
        "phone": request.form['phone'],
        "emergency": request.form['emergency'],
        "location": request.form['location']

    })

    return """
    <h2 style='color:red;text-align:center;'>
        🚨 SOS Alert Sent Successfully!
    </h2>

    <center>
        <a href='/dashboard'>Back to Dashboard</a>
    </center>
    """


# ---------------- LOGOUT ----------------

@app.route('/logout')
def logout():

    session.pop('user', None)

    return redirect('/login')


# ---------------- RUN APP ----------------

if __name__ == '__main__':
    app.run(debug=True)

