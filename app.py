from flask import Flask, request, render_template, redirect, url_for
import sqlite3
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import os

# Initialize the Flask application
app = Flask(__name__)

# Configure the Firebase service account
# Path to your own Firebase service account key (never commit this file)
cred = credentials.Certificate(os.environ.get("FIREBASE_KEY_PATH", "serviceAccountKey.json"))
firebase_admin.initialize_app(cred)

# Firestore connection
db = firestore.client()

# Function to create SQLite connection
def get_db_connection():
    conn = sqlite3.connect(os.environ.get("SQLITE_PATH", "database.sqlite"), timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

# Home Page: List all reservations
@app.route('/')
def index():
    conn = get_db_connection()
    try:
        reservations = conn.execute('SELECT * FROM Reservation').fetchall()
    finally:
        conn.close()
    return render_template('index.html', reservations=reservations)

# Reservation addition form
@app.route('/add', methods=('GET', 'POST'))
def add():
    if request.method == 'POST':
        reservation_id = request.form['reservation_id']
        date = request.form['date']
        time = request.form['time']
        customer_id = request.form['customer_id']
        table_id = request.form['table_id']
        employee_id = request.form['employee_id']

        conn = get_db_connection()
        try:
            conn.execute(
                "INSERT INTO Reservation (ReservationID, Date, Time, CustomerID, TableID, EmployeeID) VALUES (?, ?, ?, ?, ?, ?)",
                (reservation_id, date, time, customer_id, table_id, employee_id)
            )
            conn.commit()
        finally:
            conn.close()

        try:
            db.collection('reservations').add({
                'ReservationID': reservation_id,
                'Date': date,
                'Time': time,
                'CustomerID': customer_id,
                'TableID': table_id,
                'EmployeeID': employee_id
            })
        except Exception as e:
            return f"An error occurred while adding to Firebase: {e}"

        return "Reservation successfully saved to SQLite and Firebase! <a href='/'>Home Page</a>"

    return render_template('add.html')

# Support Page: Submit a support message
@app.route('/support', methods=('GET', 'POST'))
def support():
    if request.method == 'POST':
        name = request.form['name']
        subject = request.form['subject']
        message = request.form['message']
        timestamp = datetime.now().isoformat()

        try:
            db.collection('support_messages').add({
                'name': name,
                'subject': subject,
                'message': message,
                'timestamp': timestamp,
                'reply': None  # Empty until the admin replies
            })
            return "Message successfully sent! <a href='/support'>Back to Support Page</a>"
        except Exception as e:
            return f"An error occurred while adding the message to Firebase: {e}"

    return render_template('support.html')

# Admin Page: View all support messages
@app.route('/admin')
def admin():
    try:
        messages_ref = db.collection('support_messages').stream()
        messages = [
            {
                'id': message.id,  # Message ID
                'name': message.get('name'),
                'subject': message.get('subject'),
                'message': message.get('message'),
                'timestamp': message.get('timestamp'),
                'reply': message.get('reply')  # Admin reply
            }
            for message in messages_ref
        ]
        return render_template('admin.html', messages=messages)
    except Exception as e:
        return f"An error occurred while fetching messages: {e}"

# Reply to a specific message
@app.route('/reply_support/<msg_id>', methods=('GET', 'POST'))
def reply_support(msg_id):
    if request.method == 'POST':
        reply = request.form['reply']  # Reply from the admin
        try:
            # Update the message in Firestore
            db.collection('support_messages').document(msg_id).update({
                'reply': reply
            })
            return redirect('/admin')  # Back to the admin panel
        except Exception as e:
            return f"An error occurred while updating the reply: {e}"

    # Fetch the message to show it above the reply form
    try:
        message = db.collection('support_messages').document(msg_id).get()
        if message.exists:
            message_data = message.to_dict()
            return render_template('reply_support.html', message=message_data)
        else:
            return "Message not found."
    except Exception as e:
        return f"An error occurred while fetching the message: {e}"


# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True, threaded=False, port=5001)
