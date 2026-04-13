import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

db = mysql.connector.connect(
    host=os.environ.get("DB_HOST"),
    user=os.environ.get("DB_USER"),
    password=os.environ.get("DB_PASSWORD"),
    database=os.environ.get("DB_NAME")
)
cursor = db.cursor()

# Create teacher table
cursor.execute("""
CREATE TABLE IF NOT EXISTS teacher (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    subject VARCHAR(50),
    standard VARCHAR(20),
    division VARCHAR(10)
)
""")

# Create admin table
cursor.execute("""
CREATE TABLE IF NOT EXISTS admin (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
)
""")

# Create students table
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    roll INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    standard VARCHAR(20),
    division VARCHAR(10),
    UNIQUE KEY unique_student (standard, division, roll)
)
""")

# Create attendance table
cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    date DATE NOT NULL,
    status VARCHAR(10) NOT NULL,
    standard VARCHAR(20),
    division VARCHAR(10),
    UNIQUE KEY unique_attendance (student_id, date)
)
""")

# Create default admin (username: admin, password: admin123)
cursor.execute("SELECT * FROM admin WHERE username='admin'")
if not cursor.fetchone():
    from werkzeug.security import generate_password_hash
    hashed = generate_password_hash("admin123")
    cursor.execute("INSERT INTO admin (username, password) VALUES (%s, %s)", ("admin", hashed))
    db.commit()
    print("Default admin created: admin / admin123")

db.commit()
print("Database tables created successfully!")
