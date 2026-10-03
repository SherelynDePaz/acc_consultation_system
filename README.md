# ACC Consultation System

A role-based consultation booking system built with **Python (Flask)**, **SQLite**, and **HTML/CSS**.

## Roles (RBAC)

| Role             | Capabilities                                                                 |
|------------------|-------------------------------------------------------------------------------|
| **Super Admin**  | Approve/reject medical expert sign-ups, activate/deactivate any account, view all students, view every consultation in the system. |
| **Medical Expert** | Claim unassigned consultation requests, accept/decline requests, add notes, mark consultations completed. Requires super admin approval before first login. |
| **Student**      | Register (auto-approved), book a consultation with a chosen (or any available) medical expert, track status, cancel a pending request. |

Access control is enforced server-side with a `role_required()` decorator on every route — a
student can never reach `/admin/*` or `/expert/*` routes, and vice versa.

## Tech Stack

- **Backend:** Python 3 + Flask
- **Database:** SQLite (via the built-in `sqlite3` module — no ORM required)
- **Frontend:** Server-rendered HTML (Jinja2 templates) + plain CSS
- **Theme:** Blue color scheme throughout

## Project Structure

```
acc_consultation_system/
├── app.py                  # App factory / entry point
├── config.py                # Configuration (secret key, DB path)
├── db.py                     # SQLite connection, init, and seeding helpers
├── decorators.py             # login_required / role_required (RBAC)
├── requirements.txt
├── database/
│   └── schema.sql            # Table definitions (users, consultations)
├── routes/
│   ├── auth.py                # Register / login / logout / role redirect
│   ├── admin.py                # Super admin routes
│   ├── expert.py               # Medical expert routes
│   └── student.py              # Student routes
├── templates/                # Jinja2 HTML templates (blue theme)
│   ├── base.html, index.html, login.html, register.html
│   ├── admin/, expert/, student/
└── static/css/style.css      # Blue color scheme
```

## Step-by-Step: How to Run the Project

### 1. Requirements
- Python 3.9 or newer installed on your machine.

### 2. Extract the project
Unzip `acc_consultation_system.zip` to a folder of your choice, then open a terminal in that folder.

### 3. (Recommended) Create a virtual environment
```bash
python -m venv venv
```
Activate it:
- **Windows:** `venv\Scripts\activate`
- **macOS/Linux:** `source venv/bin/activate`

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the application
```bash
python app.py
```
On the first run, the app will automatically:
- Create the SQLite database file at `database/acc_consultation.db`
- Create all tables from `database/schema.sql`
- Seed a default **Super Admin** account

You should see this printed in the terminal:
```
DEFAULT SUPER ADMIN ACCOUNT CREATED
Email:    admin@acc.edu
Password: Admin@123
```

### 6. Open the app in your browser
Go to: **http://127.0.0.1:5000**

### 7. Log in
- **Super Admin:** `admin@acc.edu` / `Admin@123` (change this in production)
- **Medical Expert / Student:** Click "Register" on the home page to create an account.
  - Students are approved automatically.
  - Medical Experts must be approved by the Super Admin
    (Super Admin → "Medical Experts" → Approve) before they can log in.

### 8. Resetting the database (optional)
To start fresh, stop the server and delete the database file, then restart:
```bash
rm database/acc_consultation.db   # macOS/Linux
del database\acc_consultation.db  # Windows
python app.py
```

## Typical Workflow

1. A **student** registers and books a consultation, optionally choosing a specific medical expert.
2. If no expert is selected (or to hand off a request), any **medical expert** can claim it from the
   "Unassigned Requests" list on their dashboard.
3. The assigned **medical expert** accepts or declines the request, adding notes.
4. Once handled, the expert can mark the consultation as **completed**.
5. The **super admin** can view every consultation, approve/manage expert accounts, and manage
   student accounts at any time.

## Notes for Production Use

- Change `SECRET_KEY` in `config.py` (or set the `SECRET_KEY` environment variable).
- Change or remove the default super admin password after first login.
- Run behind a production WSGI server (e.g., `gunicorn`) instead of `app.run(debug=True)`.
