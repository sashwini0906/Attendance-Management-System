from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "secret123"   # later change this

# ---------- DATABASE CONNECTION ----------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Pyms@123",          # your MySQL password
    database="attendance_db"
)
cursor = db.cursor(dictionary=True, buffered=True)


# ---------- ROUTES ----------


@app.route("/")
def home():
    return render_template("home.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        cursor.execute("""
            SELECT * FROM teacher
            WHERE username=%s AND password=%s
        """, (username, password))

        teacher = cursor.fetchone()

        if teacher:
            session["teacher_id"] = teacher["id"]
            session["teacher_name"] = teacher["full_name"]
            session["standard"] = teacher["standard"]
            session["division"] = teacher["division"]

            return redirect(url_for("dashboard"))
        else:
            return "Invalid Username or Password"

    return render_template("login.html")




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
            return "Attendance already marked for today!"

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

    return render_template(
        "mark_attendance.html",
        students=students,
        standard=standard,
        division=division
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



if __name__ == "__main__":
    app.run(debug=True)

