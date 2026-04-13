from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-me-in-production")

# ---------- DATABASE CONNECTION ----------
# Support both local development and Railway deployment
# Railway provides MYSQL_* variables, local uses DB_*

if "MYSQL_HOST" in os.environ:
    # Railway deployment
    db = mysql.connector.connect(
        host=os.environ.get("MYSQL_HOST"),
        port=os.environ.get("MYSQL_PORT", 3306),
        user=os.environ.get("MYSQL_USER", "root"),
        password=os.environ.get("MYSQL_PASSWORD"),
        database=os.environ.get("MYSQL_DATABASE")
    )
else:
    # Local development
    db = mysql.connector.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", ""),
        database=os.environ.get("DB_NAME", "attendance_db")
    )
cursor = db.cursor(dictionary=True, buffered=True)

# ---------- AUTO MIGRATION: Add subject column if missing ----------
try:
    cursor.execute("SHOW COLUMNS FROM teacher LIKE 'subject'")
    if not cursor.fetchone():
        raw_cursor = db.cursor()
        raw_cursor.execute("ALTER TABLE teacher ADD COLUMN subject VARCHAR(50) AFTER full_name")
        db.commit()
        raw_cursor.close()
except Exception:
    pass  # Ignore if migration fails


# ---------- ROUTES ----------


@app.route("/")
def home():
    return render_template("home.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        cursor.execute(
            "SELECT * FROM teacher WHERE username=%s",
            (username,),
        )

        teacher = cursor.fetchone()

        is_valid = False
        if teacher:
            stored_pw = teacher["password"]
            # Support both hashed and legacy plain-text passwords
            # First try hashed password verification
            if stored_pw and stored_pw.startswith('pbkdf2:sha256'):
                is_valid = check_password_hash(stored_pw, password)
            # Also check plain text for legacy passwords
            if not is_valid:
                is_valid = stored_pw == password

        if teacher and is_valid:
            session["teacher_id"] = teacher["id"]
            session["teacher_name"] = teacher["full_name"]
            session["teacher_subject"] = teacher.get("subject") or "Teacher"
            session["standard"] = teacher["standard"]
            session["division"] = teacher["division"]

            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid Username or Password")

    return render_template("login.html")


# ---------- ADMIN ROUTES ----------

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        cursor.execute(
            "SELECT * FROM admin WHERE username=%s",
            (username,),
        )

        admin = cursor.fetchone()

        is_valid = False
        if admin:
            stored_pw = admin["password"]
            # Support both hashed and legacy plain-text passwords
            # First try hashed password verification
            if stored_pw and stored_pw.startswith('pbkdf2:sha256'):
                is_valid = check_password_hash(stored_pw, password)
            # Also check plain text for legacy passwords
            if not is_valid:
                is_valid = stored_pw == password

        if admin and is_valid:
            session["admin_id"] = admin["id"]
            session["admin_username"] = admin["username"]
            return redirect(url_for("admin_dashboard"))
        else:
            return render_template("login.html", error="Invalid Admin Username or Password")

    return render_template("login.html")


@app.route("/admin-dashboard")
def admin_dashboard():
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    # Get all teachers
    cursor.execute("SELECT * FROM teacher ORDER BY full_name")
    teachers = cursor.fetchall()

    return render_template("admin_dashboard.html", teachers=teachers)


@app.route("/add-teacher", methods=["GET", "POST"])
def add_teacher():
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        username = request.form["username"]
        raw_password = request.form["password"]
        full_name = request.form["full_name"]
        subject = request.form["subject"]
        standard = request.form["standard"]
        division = request.form["division"]

        # Check if username already exists
        cursor.execute("SELECT id FROM teacher WHERE username=%s", (username,))
        if cursor.fetchone():
            return render_template("add_teacher.html", error="Username already exists!")

        hashed_password = generate_password_hash(raw_password)

        cursor.execute(
            """
            INSERT INTO teacher (username, password, full_name, subject, standard, division)
            VALUES (%s, %s, %s, %s, %s, %s)
        """,
            (username, hashed_password, full_name, subject, standard, division),
        )
        db.commit()

        return render_template("add_teacher.html", success="Teacher added successfully!")

    return render_template("add_teacher.html")


@app.route("/delete-teacher/<int:teacher_id>")
def delete_teacher(teacher_id):
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    cursor.execute("DELETE FROM teacher WHERE id=%s", (teacher_id,))
    db.commit()

    return redirect(url_for("admin_dashboard"))


@app.route("/admin-logout")
def admin_logout():
    session.clear()
    return redirect(url_for("home"))




@app.route("/dashboard")
def dashboard():
    if "teacher_id" not in session:
        return redirect(url_for("login"))

    return render_template("dashboard.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/select-class", methods=["GET", "POST"])
def select_class():
    if "teacher_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        standard = request.form["standard"]
        division = request.form["division"]

        # later we’ll use these to fetch students
        return redirect(url_for(
    "mark_attendance",
    standard=standard,
    division=division
))


    return render_template("select_class.html")


@app.route("/add-students", methods=["GET", "POST"])
def add_students():
    if "teacher_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        standard = request.form["standard"]
        division = request.form["division"]
        students_text = request.form.get("students_text", "").strip()

        if not students_text:
            return render_template("add_students.html", error="Please enter at least one student.")

        added, errors = _add_students_to_class(standard, division, students_text)

        if errors:
            msg = f"Added {added} student(s). Issues: " + "; ".join(errors[:5])
            if len(errors) > 5:
                msg += f" (+{len(errors)-5} more)"
            return render_template("add_students.html", success=msg)
        return render_template("add_students.html", success=f"Successfully added {added} student(s)!")

    return render_template("add_students.html")


def _add_students_to_class(standard, division, students_text):
    """Add students and return (added_count, errors_list)."""
    added = 0
    errors = []
    for line in students_text.split("\n"):
        line = line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split(",", 1)]
        if len(parts) < 2:
            errors.append(f"Invalid: '{line}' (use: Roll, Name)")
            continue
        try:
            roll = int(parts[0])
        except ValueError:
            errors.append(f"Invalid roll: '{parts[0]}'")
            continue
        name = parts[1]
        if not name:
            errors.append(f"Name required for roll {roll}")
            continue
        cursor.execute(
            "SELECT id FROM students WHERE standard=%s AND division=%s AND roll=%s",
            (standard, division, roll)
        )
        if cursor.fetchone():
            errors.append(f"Roll {roll} already exists")
            continue
        cursor.execute(
            "INSERT INTO students (roll, name, standard, division) VALUES (%s, %s, %s, %s)",
            (roll, name, standard, division)
        )
        added += 1
    db.commit()
    return added, errors


@app.route("/mark-attendance/<standard>/<division>/add-students", methods=["POST"])
def add_students_in_mark(standard, division):
    """Add students from mark attendance page, then redirect back."""
    if "teacher_id" not in session:
        return redirect(url_for("login"))
    students_text = request.form.get("students_text", "").strip()
    if not students_text:
        return redirect(url_for("mark_attendance", standard=standard, division=division))
    added, errors = _add_students_to_class(standard, division, students_text)
    if errors:
        msg = f"Added {added}. " + "; ".join(errors[:3])
        if len(errors) > 3:
            msg += f" (+{len(errors)-3} more)"
    else:
        msg = f"Added {added} student(s)!"
    return redirect(url_for("mark_attendance", standard=standard, division=division, add_msg=msg))


from datetime import date

@app.route("/mark-attendance/<standard>/<division>", methods=["GET", "POST"])
def mark_attendance(standard, division):
    if "teacher_id" not in session:
        return redirect(url_for("login"))

    today = date.today()

    if request.method == "POST":

        # check if attendance already marked
        cursor.execute("""
            SELECT id FROM attendance
            WHERE standard=%s AND division=%s AND date=%s
        """, (standard, division, today))

        already_marked = cursor.fetchone()

        if already_marked:
            flash("Attendance has already been marked for this class today.", "info")
            return redirect(url_for("dashboard"))

        # get students
        cursor.execute(
            "SELECT id FROM students WHERE standard=%s AND division=%s",
            (standard, division)
        )
        students = cursor.fetchall()

        for s in students:
            status = request.form.get(f"status_{s['id']}")
            if status:
                cursor.execute("""
                    INSERT INTO attendance (student_id, date, status, standard, division)
                    VALUES (%s, %s, %s, %s, %s)
                """, (s["id"], today, status, standard, division))

        db.commit()
        return redirect(url_for("dashboard"))

    # GET request → show students
    cursor.execute("""
        SELECT * FROM students
        WHERE standard=%s AND division=%s
        ORDER BY roll
    """, (standard, division))
    students = cursor.fetchall()
    add_msg = request.args.get("add_msg")

    return render_template(
        "mark_attendance.html",
        students=students,
        standard=standard,
        division=division,
        add_msg=add_msg
    )

@app.route("/students/<standard>/<division>")
def student_list(standard, division):
    if "teacher_id" not in session:
        return redirect(url_for("login"))

    cursor.execute("""
        SELECT * FROM students
        WHERE standard=%s AND division=%s
        ORDER BY roll
    """, (standard, division))

    students = cursor.fetchall()

    return render_template(
        "student_list.html",
        students=students,
        standard=standard,
        division=division
    )

@app.route("/view-attendance", methods=["GET", "POST"])
def view_attendance():
    if "teacher_id" not in session:
        return redirect(url_for("login"))

    records = []
    summary = None
    date_selected = None
    standard = None
    division = None

    if request.method == "POST":
        date_selected = request.form.get("date")
        standard = request.form.get("standard")
        division = request.form.get("division")

        cursor.execute("""
            SELECT s.roll, s.name, a.status
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            WHERE a.date = %s
              AND a.standard = %s
              AND a.division = %s
            ORDER BY s.roll
        """, (date_selected, standard, division))

        records = cursor.fetchall()

        total = len(records)
        present = sum(1 for r in records if r["status"] == "present")
        absent = total - present

        summary = {
            "total": total,
            "present": present,
            "absent": absent
        }

    return render_template(
        "view_attendance.html",
        records=records,
        summary=summary,
        date_selected=date_selected,
        standard_selected=standard,
        division_selected=division
    )



import pandas as pd
from flask import send_file
from io import BytesIO

@app.route("/export-attendance", methods=["POST"])
def export_attendance():
    if "teacher_id" not in session:
        return redirect(url_for("login"))

    date_selected = request.form["date"]
    standard = request.form["standard"]
    division = request.form["division"]

    cursor.execute("""
        SELECT s.roll, s.name, a.status
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        WHERE a.date=%s AND a.standard=%s AND a.division=%s
        ORDER BY s.roll
    """, (date_selected, standard, division))

    records = cursor.fetchall()

    # Convert to DataFrame
    df = pd.DataFrame(records)

    # Create Excel in memory
    output = BytesIO()
    df.to_excel(output, index=False, sheet_name="Attendance")
    output.seek(0)

    filename = f"Attendance_{standard}{division}_{date_selected}.xlsx"

    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

from datetime import date, timedelta

@app.route("/weekly-defaulters", methods=["GET", "POST"])
def weekly_defaulters():
    if "teacher_id" not in session:
        return redirect(url_for("login"))

    defaulters = None
    standard = None
    division = None

    if request.method == "POST":
        standard = request.form["standard"]
        division = request.form["division"]

        end_date = date.today()
        start_date = end_date - timedelta(days=6)

        cursor.execute("""
            SELECT 
                s.roll,
                s.name,
                ROUND(
                    SUM(CASE WHEN a.status='present' THEN 1 ELSE 0 END)
                    / COUNT(*) * 100, 2
                ) AS percentage
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            WHERE a.standard=%s 
              AND a.division=%s
              AND a.date BETWEEN %s AND %s
            GROUP BY s.id
            HAVING percentage < 75
            ORDER BY percentage ASC
        """, (standard, division, start_date, end_date))

        defaulters = cursor.fetchall()

    return render_template(
        "weekly_defaulters.html",
        defaulters=defaulters,
        standard=standard,
        division=division
    )


@app.route("/export-weekly-defaulters", methods=["POST"])
def export_weekly_defaulters():
    if "teacher_id" not in session:
        return redirect(url_for("login"))

    standard = request.form["standard"]
    division = request.form["division"]

    cursor.execute("""
        SELECT 
            s.roll,
            s.name,
            ROUND(
                SUM(CASE WHEN a.status='present' THEN 1 ELSE 0 END) * 100.0 
                / COUNT(a.id), 2
            ) AS percentage
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        WHERE a.standard=%s AND a.division=%s
          AND a.date >= CURDATE() - INTERVAL 7 DAY
        GROUP BY s.id
        HAVING percentage < 75
        ORDER BY percentage
    """, (standard, division))

    records = cursor.fetchall()

    import pandas as pd
    from io import BytesIO
    from flask import send_file

    df = pd.DataFrame(records)

    output = BytesIO()
    df.to_excel(output, index=False, sheet_name="Weekly Defaulters")
    output.seek(0)

    filename = f"Weekly_Defaulters_{standard}{division}.xlsx"

    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

def create_app():
    return app


if __name__ == "__main__":
    debug_flag = os.environ.get("FLASK_DEBUG", "1") == "1"
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=debug_flag)
=======
from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-me-in-production")

# ---------- DATABASE CONNECTION ----------
# Support both local development and Railway deployment
# Railway provides MYSQL_* variables, local uses DB_*

if "MYSQL_HOST" in os.environ:
    # Railway deployment
    db = mysql.connector.connect(
        host=os.environ.get("MYSQL_HOST"),
        port=os.environ.get("MYSQL_PORT", 3306),
        user=os.environ.get("MYSQL_USER", "root"),
        password=os.environ.get("MYSQL_PASSWORD"),
        database=os.environ.get("MYSQL_DATABASE")
    )
else:
    # Local development
    db = mysql.connector.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", ""),
        database=os.environ.get("DB_NAME", "attendance_db")
    )
cursor = db.cursor(dictionary=True, buffered=True)

# ---------- AUTO MIGRATION: Add subject column if missing ----------
try:
    cursor.execute("SHOW COLUMNS FROM teacher LIKE 'subject'")
    if not cursor.fetchone():
        raw_cursor = db.cursor()
        raw_cursor.execute("ALTER TABLE teacher ADD COLUMN subject VARCHAR(50) AFTER full_name")
        db.commit()
        raw_cursor.close()
except Exception:
    pass  # Ignore if migration fails


# ---------- ROUTES ----------


@app.route("/")
def home():
    return render_template("home.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        cursor.execute(
            "SELECT * FROM teacher WHERE username=%s",
            (username,),
        )

        teacher = cursor.fetchone()

        is_valid = False
        if teacher:
            stored_pw = teacher["password"]
            # Support both hashed and legacy plain-text passwords
            # First try hashed password verification
            if stored_pw and stored_pw.startswith('pbkdf2:sha256'):
                is_valid = check_password_hash(stored_pw, password)
            # Also check plain text for legacy passwords
            if not is_valid:
                is_valid = stored_pw == password

        if teacher and is_valid:
            session["teacher_id"] = teacher["id"]
            session["teacher_name"] = teacher["full_name"]
            session["teacher_subject"] = teacher.get("subject") or "Teacher"
            session["standard"] = teacher["standard"]
            session["division"] = teacher["division"]

            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid Username or Password")

    return render_template("login.html")


# ---------- ADMIN ROUTES ----------

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        cursor.execute(
            "SELECT * FROM admin WHERE username=%s",
            (username,),
        )

        admin = cursor.fetchone()

        is_valid = False
        if admin:
            stored_pw = admin["password"]
            # Support both hashed and legacy plain-text passwords
            # First try hashed password verification
            if stored_pw and stored_pw.startswith('pbkdf2:sha256'):
                is_valid = check_password_hash(stored_pw, password)
            # Also check plain text for legacy passwords
            if not is_valid:
                is_valid = stored_pw == password

        if admin and is_valid:
            session["admin_id"] = admin["id"]
            session["admin_username"] = admin["username"]
            return redirect(url_for("admin_dashboard"))
        else:
            return render_template("login.html", error="Invalid Admin Username or Password")

    return render_template("login.html")


@app.route("/admin-dashboard")
def admin_dashboard():
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    # Get all teachers
    cursor.execute("SELECT * FROM teacher ORDER BY full_name")
    teachers = cursor.fetchall()

    return render_template("admin_dashboard.html", teachers=teachers)


@app.route("/add-teacher", methods=["GET", "POST"])
def add_teacher():
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        username = request.form["username"]
        raw_password = request.form["password"]
        full_name = request.form["full_name"]
        subject = request.form["subject"]
        standard = request.form["standard"]
        division = request.form["division"]

        # Check if username already exists
        cursor.execute("SELECT id FROM teacher WHERE username=%s", (username,))
        if cursor.fetchone():
            return render_template("add_teacher.html", error="Username already exists!")

        hashed_password = generate_password_hash(raw_password)

        cursor.execute(
            """
            INSERT INTO teacher (username, password, full_name, subject, standard, division)
            VALUES (%s, %s, %s, %s, %s, %s)
        """,
            (username, hashed_password, full_name, subject, standard, division),
        )
        db.commit()

        return render_template("add_teacher.html", success="Teacher added successfully!")

    return render_template("add_teacher.html")


@app.route("/delete-teacher/<int:teacher_id>")
def delete_teacher(teacher_id):
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    cursor.execute("DELETE FROM teacher WHERE id=%s", (teacher_id,))
    db.commit()

    return redirect(url_for("admin_dashboard"))


@app.route("/admin-logout")
def admin_logout():
    session.clear()
    return redirect(url_for("home"))




@app.route("/dashboard")
def dashboard():
    if "teacher_id" not in session:
        return redirect(url_for("login"))

    return render_template("dashboard.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/select-class", methods=["GET", "POST"])
def select_class():
    if "teacher_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        standard = request.form["standard"]
        division = request.form["division"]

        # later we’ll use these to fetch students
        return redirect(url_for(
    "mark_attendance",
    standard=standard,
    division=division
))


    return render_template("select_class.html")


@app.route("/add-students", methods=["GET", "POST"])
def add_students():
    if "teacher_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        standard = request.form["standard"]
        division = request.form["division"]
        students_text = request.form.get("students_text", "").strip()

        if not students_text:
            return render_template("add_students.html", error="Please enter at least one student.")

        added, errors = _add_students_to_class(standard, division, students_text)

        if errors:
            msg = f"Added {added} student(s). Issues: " + "; ".join(errors[:5])
            if len(errors) > 5:
                msg += f" (+{len(errors)-5} more)"
            return render_template("add_students.html", success=msg)
        return render_template("add_students.html", success=f"Successfully added {added} student(s)!")

    return render_template("add_students.html")


def _add_students_to_class(standard, division, students_text):
    """Add students and return (added_count, errors_list)."""
    added = 0
    errors = []
    for line in students_text.split("\n"):
        line = line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split(",", 1)]
        if len(parts) < 2:
            errors.append(f"Invalid: '{line}' (use: Roll, Name)")
            continue
        try:
            roll = int(parts[0])
        except ValueError:
            errors.append(f"Invalid roll: '{parts[0]}'")
            continue
        name = parts[1]
        if not name:
            errors.append(f"Name required for roll {roll}")
            continue
        cursor.execute(
            "SELECT id FROM students WHERE standard=%s AND division=%s AND roll=%s",
            (standard, division, roll)
        )
        if cursor.fetchone():
            errors.append(f"Roll {roll} already exists")
            continue
        cursor.execute(
            "INSERT INTO students (roll, name, standard, division) VALUES (%s, %s, %s, %s)",
            (roll, name, standard, division)
        )
        added += 1
    db.commit()
    return added, errors


@app.route("/mark-attendance/<standard>/<division>/add-students", methods=["POST"])
def add_students_in_mark(standard, division):
    """Add students from mark attendance page, then redirect back."""
    if "teacher_id" not in session:
        return redirect(url_for("login"))
    students_text = request.form.get("students_text", "").strip()
    if not students_text:
        return redirect(url_for("mark_attendance", standard=standard, division=division))
    added, errors = _add_students_to_class(standard, division, students_text)
    if errors:
        msg = f"Added {added}. " + "; ".join(errors[:3])
        if len(errors) > 3:
            msg += f" (+{len(errors)-3} more)"
    else:
        msg = f"Added {added} student(s)!"
    return redirect(url_for("mark_attendance", standard=standard, division=division, add_msg=msg))


from datetime import date

@app.route("/mark-attendance/<standard>/<division>", methods=["GET", "POST"])
def mark_attendance(standard, division):
    if "teacher_id" not in session:
        return redirect(url_for("login"))

    today = date.today()

    if request.method == "POST":

        # check if attendance already marked
        cursor.execute("""
            SELECT id FROM attendance
            WHERE standard=%s AND division=%s AND date=%s
        """, (standard, division, today))

        already_marked = cursor.fetchone()

        if already_marked:
            flash("Attendance has already been marked for this class today.", "info")
            return redirect(url_for("dashboard"))

        # get students
        cursor.execute(
            "SELECT id FROM students WHERE standard=%s AND division=%s",
            (standard, division)
        )
        students = cursor.fetchall()

        for s in students:
            status = request.form.get(f"status_{s['id']}")
            if status:
                cursor.execute("""
                    INSERT INTO attendance (student_id, date, status, standard, division)
                    VALUES (%s, %s, %s, %s, %s)
                """, (s["id"], today, status, standard, division))

        db.commit()
        return redirect(url_for("dashboard"))

    # GET request → show students
    cursor.execute("""
        SELECT * FROM students
        WHERE standard=%s AND division=%s
        ORDER BY roll
    """, (standard, division))
    students = cursor.fetchall()
    add_msg = request.args.get("add_msg")

    return render_template(
        "mark_attendance.html",
        students=students,
        standard=standard,
        division=division,
        add_msg=add_msg
    )

@app.route("/students/<standard>/<division>")
def student_list(standard, division):
    if "teacher_id" not in session:
        return redirect(url_for("login"))

    cursor.execute("""
        SELECT * FROM students
        WHERE standard=%s AND division=%s
        ORDER BY roll
    """, (standard, division))

    students = cursor.fetchall()

    return render_template(
        "student_list.html",
        students=students,
        standard=standard,
        division=division
    )

@app.route("/view-attendance", methods=["GET", "POST"])
def view_attendance():
    if "teacher_id" not in session:
        return redirect(url_for("login"))

    records = []
    summary = None
    date_selected = None
    standard = None
    division = None

    if request.method == "POST":
        date_selected = request.form.get("date")
        standard = request.form.get("standard")
        division = request.form.get("division")

        cursor.execute("""
            SELECT s.roll, s.name, a.status
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            WHERE a.date = %s
              AND a.standard = %s
              AND a.division = %s
            ORDER BY s.roll
        """, (date_selected, standard, division))

        records = cursor.fetchall()

        total = len(records)
        present = sum(1 for r in records if r["status"] == "present")
        absent = total - present

        summary = {
            "total": total,
            "present": present,
            "absent": absent
        }

    return render_template(
        "view_attendance.html",
        records=records,
        summary=summary,
        date_selected=date_selected,
        standard_selected=standard,
        division_selected=division
    )



import pandas as pd
from flask import send_file
from io import BytesIO

@app.route("/export-attendance", methods=["POST"])
def export_attendance():
    if "teacher_id" not in session:
        return redirect(url_for("login"))

    date_selected = request.form["date"]
    standard = request.form["standard"]
    division = request.form["division"]

    cursor.execute("""
        SELECT s.roll, s.name, a.status
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        WHERE a.date=%s AND a.standard=%s AND a.division=%s
        ORDER BY s.roll
    """, (date_selected, standard, division))

    records = cursor.fetchall()

    # Convert to DataFrame
    df = pd.DataFrame(records)

    # Create Excel in memory
    output = BytesIO()
    df.to_excel(output, index=False, sheet_name="Attendance")
    output.seek(0)

    filename = f"Attendance_{standard}{division}_{date_selected}.xlsx"

    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

from datetime import date, timedelta

@app.route("/weekly-defaulters", methods=["GET", "POST"])
def weekly_defaulters():
    if "teacher_id" not in session:
        return redirect(url_for("login"))

    defaulters = None
    standard = None
    division = None

    if request.method == "POST":
        standard = request.form["standard"]
        division = request.form["division"]

        end_date = date.today()
        start_date = end_date - timedelta(days=6)

        cursor.execute("""
            SELECT 
                s.roll,
                s.name,
                ROUND(
                    SUM(CASE WHEN a.status='present' THEN 1 ELSE 0 END)
                    / COUNT(*) * 100, 2
                ) AS percentage
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            WHERE a.standard=%s 
              AND a.division=%s
              AND a.date BETWEEN %s AND %s
            GROUP BY s.id
            HAVING percentage < 75
            ORDER BY percentage ASC
        """, (standard, division, start_date, end_date))

        defaulters = cursor.fetchall()

    return render_template(
        "weekly_defaulters.html",
        defaulters=defaulters,
        standard=standard,
        division=division
    )


@app.route("/export-weekly-defaulters", methods=["POST"])
def export_weekly_defaulters():
    if "teacher_id" not in session:
        return redirect(url_for("login"))

    standard = request.form["standard"]
    division = request.form["division"]

    cursor.execute("""
        SELECT 
            s.roll,
            s.name,
            ROUND(
                SUM(CASE WHEN a.status='present' THEN 1 ELSE 0 END) * 100.0 
                / COUNT(a.id), 2
            ) AS percentage
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        WHERE a.standard=%s AND a.division=%s
          AND a.date >= CURDATE() - INTERVAL 7 DAY
        GROUP BY s.id
        HAVING percentage < 75
        ORDER BY percentage
    """, (standard, division))

    records = cursor.fetchall()

    import pandas as pd
    from io import BytesIO
    from flask import send_file

    df = pd.DataFrame(records)

    output = BytesIO()
    df.to_excel(output, index=False, sheet_name="Weekly Defaulters")
    output.seek(0)

    filename = f"Weekly_Defaulters_{standard}{division}.xlsx"

    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

def create_app():
    return app


if __name__ == "__main__":
    debug_flag = os.environ.get("FLASK_DEBUG", "1") == "1"
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=debug_flag)

