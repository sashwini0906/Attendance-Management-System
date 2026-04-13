<<<<<<< HEAD
## GBM High School – Attendance System

Modern Flask-based web app to manage **class-wise student attendance** for GBM High School, with separate **Teacher** and **Admin** portals and Excel exports.

---

### Features

- **Role-based access**
  - Admin login: manage teachers (add/delete, assign subject + class).
  - Teacher login: mark attendance, manage students, view reports.
- **Teacher portal**
  - Dashboard with quick actions.
  - Add students (bulk: `Roll, Name` format).
  - Mark daily attendance per class/division.
  - View past attendance by date/class/division.
  - Export attendance to Excel.
  - Weekly defaulters report (students below 75% in last 7 days) + Excel export.
- **Admin portal**
  - View all teachers.
  - Add teacher with **subject**, **standard**, and **division**.
  - Delete teacher.
- **UI/UX**
  - Shared layout with sticky header/nav, smooth scrolling, subtle animations.
  - Responsive cards, buttons, and tables.

---

### Tech stack

- **Backend**: Python, Flask
- **Database**: MySQL
- **ORM/DB access**: `mysql-connector-python` (raw SQL)
- **Export**: `pandas`, `openpyxl` (Excel generation)
- **Config**: `.env` + `python-dotenv`

---

### Project structure (key files)

- `app.py` – main Flask application and routes.
- `as.sql` – base SQL script to create database and tables.
- `add_subject_column.sql` – one-time helper script to add `subject` column to existing `teacher` table (older DBs only; new ones already include it).
- `templates/`
  - `base.html` – shared HTML layout + styles.
  - `base_teacher.html` – teacher layout + nav.
  - `base_admin.html` – admin layout + nav.
  - `home.html` – public landing page.
  - `login.html` – combined Teacher/Admin login page.
  - `dashboard.html` – teacher dashboard.
  - `select_class.html`, `mark_attendance.html`, `view_attendance.html`, `weekly_defaulters.html`, `student_list.html` – teacher features.
  - `add_students.html` – bulk student import UI.
  - `admin_dashboard.html`, `add_teacher.html` – admin features.
- `requirements.txt` – Python dependencies.
- `.env.example` – sample environment config (copy to `.env`).

---

### Setup & installation

#### 1. Clone the repo

```bash
git clone <your-repo-url>
cd attendance-system
```

#### 2. Create & activate virtual environment (recommended)

```bash
python -m venv .venv
.venv\Scripts\activate  # on Windows
# source .venv/bin/activate  # on macOS/Linux
```

#### 3. Install dependencies

```bash
pip install -r requirements.txt
```

#### 4. Configure database

1. Make sure **MySQL** is installed and running.
2. Create the database and tables using `as.sql`:

```bash
mysql -u root -p < as.sql
```

This will:
- Create database `attendance_db`.
- Create `teacher`, `admin`, `students`, and `attendance` tables.
- Insert a default admin user:
  - **Username**: `admin`
  - **Password**: `admin123`

> If you created the database **before** `subject` was added to the `teacher` table and you still see an error like `Unknown column 'subject' in 'field list'`, either:
> - Run `add_subject_column.sql` manually, **or**
> - Restart the app – there is an **auto-migration** that adds the `subject` column if missing.

```bash
mysql -u root -p < add_subject_column.sql
```

#### 5. Configure environment variables

Copy `.env.example` to `.env` and adjust values:

```bash
copy .env.example .env   # Windows
```

Edit `.env`:

```ini
SECRET_KEY=your-secret-key-here
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your-mysql-password
DB_NAME=attendance_db
```

> `.env` is **ignored by git** via `.gitignore`, so your secrets stay local.

---

### Running the app (local dev)

From the project root:

```bash
set FLASK_DEBUG=1  # Windows
python app.py
```

The app will start on `http://127.0.0.1:5000/`.

Open a browser and visit:

- **Home / Landing**: `http://127.0.0.1:5000/`
- **Staff Login** (teachers & admin): `http://127.0.0.1:5000/login`

---

### Production run (gunicorn)

For production, run the app behind a WSGI server like **gunicorn** (already included in `requirements.txt`):

```bash
gunicorn "app:create_app()"
```

Common options:

- Bind to all interfaces on port 8000:

```bash
gunicorn --bind 0.0.0.0:8000 "app:create_app()"
```

- Control debug via env var (should be off in production):

```bash
set FLASK_DEBUG=0
gunicorn "app:create_app()"
```

---

### How to use

#### Admin workflow

1. Go to `/login`, switch to **Admin** tab.
2. Log in with default admin (`admin` / `admin123`).
3. From **Admin Dashboard**:
   - Click **Add Teacher**.
   - Fill in username, password, full name, **subject**, class (standard) and division.
4. Share teacher credentials with the staff member.

#### Teacher workflow

1. Go to `/login`, use **Teacher** tab.
2. Log in with your teacher username/password.
3. On the **Teacher Dashboard**:
   - **Add Students**: bulk add `Roll, Name` per class & division.
   - **Mark Today’s Attendance**:
     - Select class and division.
     - Mark each student as Present/Absent and save.
   - **View Attendance Records**:
     - Choose date, class, division.
     - See per-student status + summary and export to Excel.
   - **Weekly Defaulters (75%)**:
     - Choose class & division.
     - See students with attendance \< 75% over the last 7 days + export list to Excel.

---

### Important notes / known limitations

- **Passwords are stored in plain text** for simplicity in this learning project.
  - For production, replace with proper password hashing (e.g. `werkzeug.security.generate_password_hash`).
- A single MySQL connection is created at startup; for a large/real deployment, you would typically use a connection pool or per-request connections.
- Attendance is **one record per student per day per class/division**. Re-marking the same class/date is prevented by a check (with a friendly message on the dashboard).

---

### Customization ideas

- Add password hashing and change-password flows.
- Allow teachers to edit attendance after submission (within a time window).
- Add guardian/parent view for student attendance.
- Add CSV import for students instead of textarea.
- Deploy to a server (e.g. Render, Railway, or a VPS) with production-ready MySQL.

=======
## GBM High School – Attendance System

Modern Flask-based web app to manage **class-wise student attendance** for GBM High School, with separate **Teacher** and **Admin** portals and Excel exports.

---

### Features

- **Role-based access**
  - Admin login: manage teachers (add/delete, assign subject + class).
  - Teacher login: mark attendance, manage students, view reports.
- **Teacher portal**
  - Dashboard with quick actions.
  - Add students (bulk: `Roll, Name` format).
  - Mark daily attendance per class/division.
  - View past attendance by date/class/division.
  - Export attendance to Excel.
  - Weekly defaulters report (students below 75% in last 7 days) + Excel export.
- **Admin portal**
  - View all teachers.
  - Add teacher with **subject**, **standard**, and **division**.
  - Delete teacher.
- **UI/UX**
  - Shared layout with sticky header/nav, smooth scrolling, subtle animations.
  - Responsive cards, buttons, and tables.

---

### Tech stack

- **Backend**: Python, Flask
- **Database**: MySQL
- **ORM/DB access**: `mysql-connector-python` (raw SQL)
- **Export**: `pandas`, `openpyxl` (Excel generation)
- **Config**: `.env` + `python-dotenv`

---

### Project structure (key files)

- `app.py` – main Flask application and routes.
- `as.sql` – base SQL script to create database and tables.
- `add_subject_column.sql` – one-time helper script to add `subject` column to existing `teacher` table (older DBs only; new ones already include it).
- `templates/`
  - `base.html` – shared HTML layout + styles.
  - `base_teacher.html` – teacher layout + nav.
  - `base_admin.html` – admin layout + nav.
  - `home.html` – public landing page.
  - `login.html` – combined Teacher/Admin login page.
  - `dashboard.html` – teacher dashboard.
  - `select_class.html`, `mark_attendance.html`, `view_attendance.html`, `weekly_defaulters.html`, `student_list.html` – teacher features.
  - `add_students.html` – bulk student import UI.
  - `admin_dashboard.html`, `add_teacher.html` – admin features.
- `requirements.txt` – Python dependencies.
- `.env.example` – sample environment config (copy to `.env`).

---

### Setup & installation

#### 1. Clone the repo

```bash
git clone <your-repo-url>
cd attendance-system
```

#### 2. Create & activate virtual environment (recommended)

```bash
python -m venv .venv
.venv\Scripts\activate  # on Windows
# source .venv/bin/activate  # on macOS/Linux
```

#### 3. Install dependencies

```bash
pip install -r requirements.txt
```

#### 4. Configure database

1. Make sure **MySQL** is installed and running.
2. Create the database and tables using `as.sql`:

```bash
mysql -u root -p < as.sql
```

This will:
- Create database `attendance_db`.
- Create `teacher`, `admin`, `students`, and `attendance` tables.
- Insert a default admin user:
  - **Username**: `admin`
  - **Password**: `admin123`

> If you created the database **before** `subject` was added to the `teacher` table and you still see an error like `Unknown column 'subject' in 'field list'`, either:
> - Run `add_subject_column.sql` manually, **or**
> - Restart the app – there is an **auto-migration** that adds the `subject` column if missing.

```bash
mysql -u root -p < add_subject_column.sql
```

#### 5. Configure environment variables

Copy `.env.example` to `.env` and adjust values:

```bash
copy .env.example .env   # Windows
```

Edit `.env`:

```ini
SECRET_KEY=your-secret-key-here
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your-mysql-password
DB_NAME=attendance_db
```

> `.env` is **ignored by git** via `.gitignore`, so your secrets stay local.

---

### Running the app (local dev)

From the project root:

```bash
set FLASK_DEBUG=1  # Windows
python app.py
```

The app will start on `http://127.0.0.1:5000/`.

Open a browser and visit:

- **Home / Landing**: `http://127.0.0.1:5000/`
- **Staff Login** (teachers & admin): `http://127.0.0.1:5000/login`

---

### Production run (gunicorn)

For production, run the app behind a WSGI server like **gunicorn** (already included in `requirements.txt`):

```bash
gunicorn "app:create_app()"
```

Common options:

- Bind to all interfaces on port 8000:

```bash
gunicorn --bind 0.0.0.0:8000 "app:create_app()"
```

- Control debug via env var (should be off in production):

```bash
set FLASK_DEBUG=0
gunicorn "app:create_app()"
```

---

### How to use

#### Admin workflow

1. Go to `/login`, switch to **Admin** tab.
2. Log in with default admin (`admin` / `admin123`).
3. From **Admin Dashboard**:
   - Click **Add Teacher**.
   - Fill in username, password, full name, **subject**, class (standard) and division.
4. Share teacher credentials with the staff member.

#### Teacher workflow

1. Go to `/login`, use **Teacher** tab.
2. Log in with your teacher username/password.
3. On the **Teacher Dashboard**:
   - **Add Students**: bulk add `Roll, Name` per class & division.
   - **Mark Today’s Attendance**:
     - Select class and division.
     - Mark each student as Present/Absent and save.
   - **View Attendance Records**:
     - Choose date, class, division.
     - See per-student status + summary and export to Excel.
   - **Weekly Defaulters (75%)**:
     - Choose class & division.
     - See students with attendance \< 75% over the last 7 days + export list to Excel.

---

### Important notes / known limitations

- **Passwords are stored in plain text** for simplicity in this learning project.
  - For production, replace with proper password hashing (e.g. `werkzeug.security.generate_password_hash`).
- A single MySQL connection is created at startup; for a large/real deployment, you would typically use a connection pool or per-request connections.
- Attendance is **one record per student per day per class/division**. Re-marking the same class/date is prevented by a check (with a friendly message on the dashboard).

---

### Customization ideas

- Add password hashing and change-password flows.
- Allow teachers to edit attendance after submission (within a time window).
- Add guardian/parent view for student attendance.
- Add CSV import for students instead of textarea.
- Deploy to a server (e.g. Render, Railway, or a VPS) with production-ready MySQL.

>>>>>>> a741fce4340050b093253c89486b1f4e20183baf
