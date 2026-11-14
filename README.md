# Restaurant Reservation & Support System

A Flask web application that manages restaurant reservations with a **relational database (SQLite)** and adds a **customer support page backed by Firebase Firestore**, where guests send messages and an admin replies.

> Course project for **CS306 – Database Systems**, Sabancı University

---

## Features

- **Reservation list:** view all reservations stored in SQLite
- **Add reservation:** form that writes each reservation to **both SQLite and Firestore**
- **Support page:** guests enter their name, choose a subject (*Defected Product, Late Order, Lost Product, Suggestion*) and send a message, timestamped automatically
- **Admin panel:** lists all support messages in one place and lets the admin reply to each one

## Tech stack

Python · Flask · SQLite · Firebase Firestore (firebase-admin SDK) · HTML / Jinja2 templates

##  Project structure

```
├── app.py                  # Flask routes (reservations, support, admin)
├── templates/
│   ├── index.html          # Reservation list
│   ├── add.html            # Add reservation form
│   ├── support.html        # Guest support form
│   ├── admin.html          # Admin view of all messages
│   └── reply_support.html  # Admin reply form
└── requirements.txt
```

## Running locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create a Firebase project, enable Firestore, and download a service account key from
   *Project settings → Service accounts → Generate new private key*.
   Save it as `serviceAccountKey.json` in the project folder (it is git-ignored), or point to it with:
   ```bash
   export FIREBASE_KEY_PATH=/path/to/serviceAccountKey.json
   ```
3. Provide a SQLite database containing a `Reservation` table
   (`ReservationID, Date, Time, CustomerID, TableID, EmployeeID`). By default the app looks for `database.sqlite`; to use another file:
   ```bash
   export SQLITE_PATH=/path/to/your.sqlite
   ```
4. Start the app and open http://localhost:5001:
   ```bash
   python app.py
   ```

## Note on credentials

The Firebase service account key is **not** included in this repository. Each user must supply their own.
